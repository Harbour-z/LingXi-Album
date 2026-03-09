"""
ASR (Automatic Speech Recognition) 实时语音识别路由
支持 WebSocket 实时音频流传输和 REST API 会话管理
"""

import asyncio
import base64
import json
import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import JSONResponse

from ..models.schemas import (
    BaseResponse,
    ResponseStatus,
    ASRSessionConfig,
    ASRSessionInfo,
    ASRSessionStatus,
    ASRSessionResponse,
)
from ..services.asr_service import get_asr_service, ASRSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/asr", tags=["ASR - 实时语音识别"])


@router.websocket("/realtime")
async def websocket_asr_realtime(
    websocket: WebSocket,
    language: str = Query("zh", description="音频源语言"),
    sample_rate: int = Query(16000, description="音频采样率"),
    input_format: str = Query("pcm", description="音频格式: pcm 或 opus"),
    enable_vad: bool = Query(True, description="是否开启服务端VAD"),
    vad_threshold: float = Query(0.0, description="VAD检测阈值"),
    vad_silence_ms: int = Query(400, description="VAD断句检测阈值(ms)")
):
    """
    WebSocket 实时语音识别端点

    客户端通过 WebSocket 连接后，发送音频数据（Base64 编码或二进制），
    服务端实时返回识别结果。

    消息格式：
    - 客户端发送音频: {"type": "audio", "data": "<base64-encoded-audio>"}
    - 客户端发送结束信号: {"type": "end"}
    - 服务端返回事件: {"type": "<event-type>", "text": "...", "is_final": true/false, ...}
    """
    await websocket.accept()
    logger.info(f"[ASR WebSocket] New connection request")

    asr_service = get_asr_service()
    session: Optional[ASRSession] = None
    event_task: Optional[asyncio.Task] = None

    async def event_sender():
        """事件发送协程，从会话事件队列中取出事件并发送给客户端"""
        if not session:
            return
        try:
            while session.status not in ["closed", "finished", "error"]:
                try:
                    event = await asyncio.wait_for(
                        session._event_queue.get(),
                        timeout=1.0
                    )
                    await websocket.send_json(event)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"[ASR WebSocket] Error sending event: {e}")
                    break
        except asyncio.CancelledError:
            pass
        logger.info(f"[ASR WebSocket] Event sender stopped")

    try:
        session = asr_service.create_session(
            language=language,
            sample_rate=sample_rate,
            input_format=input_format,
            enable_vad=enable_vad,
            vad_threshold=vad_threshold,
            vad_silence_ms=vad_silence_ms
        )

        session.callback.set_event_loop(asyncio.get_event_loop())

        asr_service.connect_session(session)

        await websocket.send_json({
            "type": "session.ready",
            "session_id": session.session_id,
            "config": session.config
        })

        event_task = asyncio.create_task(event_sender())

        while True:
            try:
                message = await websocket.receive()

                if message["type"] == "websocket.receive":
                    if "text" in message:
                        data = json.loads(message["text"])
                        msg_type = data.get("type")

                        if msg_type == "audio":
                            audio_b64 = data.get("data", "")
                            if audio_b64:
                                try:
                                    audio_bytes = base64.b64decode(audio_b64)
                                    asr_service.send_audio(session, audio_bytes)
                                except Exception as e:
                                    await websocket.send_json({
                                        "type": "error",
                                        "message": f"Failed to process audio: {str(e)}"
                                    })

                        elif msg_type == "end":
                            logger.info(f"[ASR WebSocket] Client requested end")
                            final_transcript = asr_service.end_session(session)
                            await websocket.send_json({
                                "type": "session.end",
                                "session_id": session.session_id,
                                "final_transcript": final_transcript
                            })
                            break

                        elif msg_type == "ping":
                            await websocket.send_json({"type": "pong"})

                    elif "bytes" in message:
                        audio_bytes = message["bytes"]
                        asr_service.send_audio(session, audio_bytes)

                elif message["type"] == "websocket.disconnect":
                    logger.info(f"[ASR WebSocket] Client disconnected")
                    break

            except json.JSONDecodeError as e:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Invalid JSON: {str(e)}"
                })
            except Exception as e:
                logger.error(f"[ASR WebSocket] Error processing message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })

    except WebSocketDisconnect:
        logger.info(f"[ASR WebSocket] WebSocket disconnected")
    except Exception as e:
        logger.error(f"[ASR WebSocket] Error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        if event_task:
            event_task.cancel()
            try:
                await event_task
            except asyncio.CancelledError:
                pass

        if session and session.status not in ["closed", "finished"]:
            asr_service.close_session(session)

        logger.info(f"[ASR WebSocket] Connection closed")


@router.post("/session/create", response_model=ASRSessionResponse)
async def create_asr_session(config: ASRSessionConfig):
    """
    创建 ASR 会话（REST API）

    创建一个新的 ASR 会话，返回会话 ID 和配置信息。
    客户端需要通过 WebSocket 端点进行音频传输。
    """
    try:
        asr_service = get_asr_service()
        session = asr_service.create_session(
            language=config.language,
            sample_rate=config.sample_rate,
            input_format=config.input_format,
            enable_vad=config.enable_vad,
            vad_threshold=config.vad_threshold,
            vad_silence_ms=config.vad_silence_ms
        )

        return ASRSessionResponse(
            status=ResponseStatus.SUCCESS,
            message="ASR session created successfully",
            data=ASRSessionInfo(
                session_id=session.session_id,
                status=ASRSessionStatus.CONNECTING,
                config=config,
                created_at=session.created_at
            )
        )
    except Exception as e:
        logger.error(f"[ASR] Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/connect", response_model=BaseResponse)
async def connect_asr_session(session_id: str):
    """
    连接 ASR 会话

    建立 WebSocket 连接并配置会话参数。
    """
    try:
        asr_service = get_asr_service()
        session = asr_service.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        asr_service.connect_session(session)

        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message="Session connected successfully",
            data={"session_id": session_id, "status": session.status}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ASR] Failed to connect session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/audio", response_model=BaseResponse)
async def send_audio_to_session(session_id: str, audio_data: str):
    """
    发送音频数据到会话

    Args:
        session_id: 会话 ID
        audio_data: Base64 编码的音频数据
    """
    try:
        asr_service = get_asr_service()
        session = asr_service.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        audio_bytes = base64.b64decode(audio_data)
        asr_service.send_audio(session, audio_bytes)

        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message="Audio sent successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ASR] Failed to send audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/end", response_model=BaseResponse)
async def end_asr_session(session_id: str):
    """
    结束 ASR 会话

    发送结束信号，等待最终识别结果，然后关闭会话。
    """
    try:
        asr_service = get_asr_service()
        session = asr_service.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        final_transcript = asr_service.end_session(session)

        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message="Session ended successfully",
            data={
                "session_id": session_id,
                "final_transcript": final_transcript
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ASR] Failed to end session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}", response_model=BaseResponse)
async def close_asr_session(session_id: str):
    """
    关闭 ASR 会话（立即终止）

    立即关闭会话，不等待最终结果。
    """
    try:
        asr_service = get_asr_service()
        session = asr_service.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        asr_service.close_session(session)

        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message="Session closed successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ASR] Failed to close session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}", response_model=ASRSessionResponse)
async def get_asr_session_info(session_id: str):
    """
    获取 ASR 会话信息
    """
    try:
        asr_service = get_asr_service()
        session = asr_service.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        status_map = {
            "connecting": ASRSessionStatus.CONNECTING,
            "connected": ASRSessionStatus.CONNECTED,
            "active": ASRSessionStatus.ACTIVE,
            "closing": ASRSessionStatus.CLOSING,
            "closed": ASRSessionStatus.CLOSED,
            "finished": ASRSessionStatus.CLOSED,
            "error": ASRSessionStatus.ERROR,
        }

        return ASRSessionResponse(
            status=ResponseStatus.SUCCESS,
            message="Session info retrieved",
            data=ASRSessionInfo(
                session_id=session.session_id,
                status=status_map.get(session.status, ASRSessionStatus.ERROR),
                config=ASRSessionConfig(
                    language=session.config["language"],
                    sample_rate=session.config["sample_rate"],
                    input_format=session.config["input_format"],
                    enable_vad=session.config["enable_vad"],
                    vad_threshold=session.config["vad_threshold"],
                    vad_silence_ms=session.config["vad_silence_ms"]
                ),
                created_at=session.created_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ASR] Failed to get session info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=BaseResponse)
async def list_asr_sessions():
    """
    列出所有活跃的 ASR 会话
    """
    try:
        asr_service = get_asr_service()
        sessions = asr_service.get_all_sessions()

        session_list = [
            {
                "session_id": s.session_id,
                "status": s.status,
                "created_at": s.created_at.isoformat(),
                "language": s.config["language"]
            }
            for s in sessions.values()
        ]

        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Found {len(session_list)} active sessions",
            data={"sessions": session_list, "total": len(session_list)}
        )
    except Exception as e:
        logger.error(f"[ASR] Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config", response_model=BaseResponse)
async def get_asr_config():
    """
    获取 ASR 服务配置信息
    """
    from ..config import get_settings
    settings = get_settings()

    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        message="ASR configuration",
        data={
            "model": settings.ASR_MODEL_NAME,
            "base_url": settings.ASR_BASE_URL,
            "default_language": settings.ASR_LANGUAGE,
            "default_sample_rate": settings.ASR_SAMPLE_RATE,
            "default_input_format": settings.ASR_INPUT_FORMAT,
            "default_enable_vad": settings.ASR_ENABLE_VAD,
            "default_vad_threshold": settings.ASR_VAD_THRESHOLD,
            "default_vad_silence_ms": settings.ASR_VAD_SILENCE_MS,
            "supported_languages": [
                {"code": "zh", "name": "中文（普通话、四川话、闽南语、吴语）"},
                {"code": "yue", "name": "粤语"},
                {"code": "en", "name": "英文"},
                {"code": "ja", "name": "日语"},
                {"code": "de", "name": "德语"},
                {"code": "ko", "name": "韩语"},
                {"code": "ru", "name": "俄语"},
                {"code": "fr", "name": "法语"},
                {"code": "pt", "name": "葡萄牙语"},
                {"code": "ar", "name": "阿拉伯语"},
                {"code": "it", "name": "意大利语"},
                {"code": "es", "name": "西班牙语"},
            ],
            "supported_sample_rates": [8000, 16000],
            "supported_formats": ["pcm", "opus"]
        }
    )