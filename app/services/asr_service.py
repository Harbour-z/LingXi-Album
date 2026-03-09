"""
ASR (Automatic Speech Recognition) 实时语音识别服务
基于阿里云 DashScope SDK 的 qwen3-asr-flash-realtime 模型
"""

import asyncio
import logging
import threading
import time
import uuid
from typing import Optional, Callable, Dict, Any
from datetime import datetime

from ..config import get_settings

logger = logging.getLogger(__name__)


class ASRSession:
    """ASR 会话管理类"""

    def __init__(self, session_id: str, config: Dict[str, Any]):
        self.session_id = session_id
        self.config = config
        self.status = "connecting"
        self.created_at = datetime.now()
        self.conversation = None
        self.callback = None
        self.transcript_buffer: list = []
        self.final_transcript: str = ""
        self._lock = threading.Lock()
        self._event_queue: asyncio.Queue = asyncio.Queue()


class ASRCallbackHandler:
    """ASR 回调处理器，处理 DashScope SDK 的回调事件"""

    def __init__(self, session: ASRSession, event_callback: Optional[Callable] = None):
        self.session = session
        self.event_callback = event_callback
        self._loop = None

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        """设置事件循环，用于跨线程事件传递"""
        self._loop = loop

    def on_open(self):
        """WebSocket 连接成功"""
        logger.info(f"[ASR] Session {self.session.session_id} connected")
        with self.session._lock:
            self.session.status = "connected"
        self._push_event({
            "type": "session.connected",
            "session_id": self.session.session_id
        })

    def on_close(self, code, msg):
        """WebSocket 连接关闭"""
        logger.info(f"[ASR] Session {self.session.session_id} closed: code={code}, msg={msg}")
        with self.session._lock:
            self.session.status = "closed"
        self._push_event({
            "type": "session.closed",
            "session_id": self.session.session_id,
            "code": code,
            "message": msg
        })

    def on_event(self, response: dict):
        """处理服务端事件"""
        try:
            event_type = response.get("type", "")
            logger.debug(f"[ASR] Event: {event_type}")

            if event_type == "session.created":
                self._handle_session_created(response)
            elif event_type == "session.updated":
                self._handle_session_updated(response)
            elif event_type == "input_audio_buffer.speech_started":
                self._handle_speech_started(response)
            elif event_type == "input_audio_buffer.speech_stopped":
                self._handle_speech_stopped(response)
            elif event_type == "conversation.item.input_audio_transcription.text":
                self._handle_partial_transcript(response)
            elif event_type == "conversation.item.input_audio_transcription.completed":
                self._handle_final_transcript(response)
            elif event_type == "session.finished":
                self._handle_session_finished(response)
            else:
                logger.debug(f"[ASR] Unhandled event type: {event_type}")

        except Exception as e:
            logger.error(f"[ASR] Error handling event: {e}")
            self._push_event({
                "type": "error",
                "session_id": self.session.session_id,
                "message": str(e)
            })

    def _handle_session_created(self, response: dict):
        """处理会话创建事件"""
        session_id = response.get("session", {}).get("id", "")
        logger.info(f"[ASR] Session created: {session_id}")
        with self.session._lock:
            self.session.status = "active"
        self._push_event({
            "type": "session.created",
            "session_id": session_id
        })

    def _handle_session_updated(self, response: dict):
        """处理会话更新事件"""
        logger.info(f"[ASR] Session updated")
        self._push_event({
            "type": "session.updated",
            "session_id": self.session.session_id
        })

    def _handle_speech_started(self, response: dict):
        """处理语音开始事件"""
        logger.info(f"[ASR] Speech started")
        self._push_event({
            "type": "speech.started",
            "session_id": self.session.session_id
        })

    def _handle_speech_stopped(self, response: dict):
        """处理语音结束事件"""
        logger.info(f"[ASR] Speech stopped")
        self._push_event({
            "type": "speech.stopped",
            "session_id": self.session.session_id
        })

    def _handle_partial_transcript(self, response: dict):
        """处理中间转写结果"""
        stash_text = response.get("stash", "")
        if stash_text:
            logger.debug(f"[ASR] Partial: {stash_text}")
            self._push_event({
                "type": "transcript.partial",
                "session_id": self.session.session_id,
                "text": stash_text,
                "is_final": False
            })

    def _handle_final_transcript(self, response: dict):
        """处理最终转写结果"""
        transcript = response.get("transcript", "")
        if transcript:
            logger.info(f"[ASR] Final: {transcript}")
            with self.session._lock:
                self.session.final_transcript += transcript
            self._push_event({
                "type": "transcript.final",
                "session_id": self.session.session_id,
                "text": transcript,
                "is_final": True
            })

    def _handle_session_finished(self, response: dict):
        """处理会话结束事件"""
        logger.info(f"[ASR] Session finished")
        with self.session._lock:
            self.session.status = "finished"
        self._push_event({
            "type": "session.finished",
            "session_id": self.session.session_id,
            "final_transcript": self.session.final_transcript
        })

    def _push_event(self, event: dict):
        """推送事件到队列"""
        if self._loop and self.session._event_queue:
            asyncio.run_coroutine_threadsafe(
                self.session._event_queue.put(event),
                self._loop
            )
        if self.event_callback:
            try:
                self.event_callback(event)
            except Exception as e:
                logger.error(f"[ASR] Callback error: {e}")


class ASRService:
    """ASR 实时语音识别服务"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = False
        self._sessions: Dict[str, ASRSession] = {}
        self._session_lock = threading.Lock()
        self._settings = None

    def initialize(self):
        """初始化服务"""
        if self._initialized:
            return
        self._settings = get_settings()
        self._initialized = True
        logger.info("[ASR] Service initialized")

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    def _get_api_key(self) -> str:
        """获取 API Key"""
        settings = self._settings or get_settings()
        api_key = settings.ASR_API_KEY or settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("ASR API Key not configured. Set ASR_API_KEY or OPENAI_API_KEY in environment.")
        return api_key

    def create_session(
        self,
        language: str = "zh",
        sample_rate: int = 16000,
        input_format: str = "pcm",
        enable_vad: bool = True,
        vad_threshold: float = 0.0,
        vad_silence_ms: int = 400,
        event_callback: Optional[Callable] = None
    ) -> ASRSession:
        """
        创建 ASR 会话

        Args:
            language: 音频源语言 (zh, yue, en, ja, de, ko, ru, fr, pt, ar, it, es, hi, id, th, tr, uk, vi, cs, da, fil, fi, is, ms, no, pl, sv)
            sample_rate: 音频采样率 (16000 或 8000)
            input_format: 音频格式 (pcm 或 opus)
            enable_vad: 是否开启服务端 VAD
            vad_threshold: VAD 检测阈值 (-1 到 1，推荐 0.0)
            vad_silence_ms: VAD 断句检测阈值 (200-6000ms)
            event_callback: 事件回调函数

        Returns:
            ASRSession: ASR 会话对象
        """
        try:
            from dashscope.audio.qwen_omni import (
                OmniRealtimeConversation,
                OmniRealtimeCallback,
                TranscriptionParams,
                MultiModality
            )
            import dashscope
        except ImportError as e:
            raise ImportError(
                "DashScope SDK not installed. Install with: pip install dashscope>=1.25.6"
            ) from e

        settings = self._settings or get_settings()
        api_key = self._get_api_key()
        dashscope.api_key = api_key

        session_id = str(uuid.uuid4())
        config = {
            "language": language,
            "sample_rate": sample_rate,
            "input_format": input_format,
            "enable_vad": enable_vad,
            "vad_threshold": vad_threshold,
            "vad_silence_ms": vad_silence_ms
        }

        session = ASRSession(session_id, config)
        callback_handler = ASRCallbackHandler(session, event_callback)
        session.callback = callback_handler

        class DashScopeCallback(OmniRealtimeCallback):
            """DashScope SDK 回调适配器"""

            def __init__(self, handler: ASRCallbackHandler):
                self.handler = handler

            def on_open(self):
                self.handler.on_open()

            def on_close(self, code, msg):
                self.handler.on_close(code, msg)

            def on_event(self, response):
                self.handler.on_event(response)

        ds_callback = DashScopeCallback(callback_handler)

        conversation = OmniRealtimeConversation(
            model=settings.ASR_MODEL_NAME,
            url=settings.ASR_BASE_URL,
            callback=ds_callback
        )
        session.conversation = conversation

        with self._session_lock:
            self._sessions[session_id] = session

        logger.info(f"[ASR] Created session: {session_id}")
        return session

    def connect_session(self, session: ASRSession) -> bool:
        """
        连接 ASR 会话

        Args:
            session: ASR 会话对象

        Returns:
            bool: 是否连接成功
        """
        if not session.conversation:
            raise ValueError("Session conversation not initialized")

        try:
            session.conversation.connect()

            settings = self._settings or get_settings()
            transcription_params = TranscriptionParams(
                language=session.config["language"],
                sample_rate=session.config["sample_rate"],
                input_audio_format=session.config["input_format"]
            )

            session.conversation.update_session(
                output_modalities=[MultiModality.TEXT],
                enable_turn_detection=session.config["enable_vad"],
                turn_detection_type="server_vad" if session.config["enable_vad"] else None,
                turn_detection_threshold=session.config["vad_threshold"],
                turn_detection_silence_duration_ms=session.config["vad_silence_ms"],
                enable_input_audio_transcription=True,
                transcription_params=transcription_params
            )

            session.status = "active"
            logger.info(f"[ASR] Session {session.session_id} connected and configured")
            return True

        except Exception as e:
            logger.error(f"[ASR] Failed to connect session: {e}")
            session.status = "error"
            raise

    def send_audio(self, session: ASRSession, audio_data: bytes) -> bool:
        """
        发送音频数据

        Args:
            session: ASR 会话对象
            audio_data: 音频数据 (PCM 或 Opus 格式)

        Returns:
            bool: 是否发送成功
        """
        if not session.conversation:
            raise ValueError("Session conversation not initialized")

        if session.status not in ["active", "connected"]:
            raise ValueError(f"Session not active, current status: {session.status}")

        try:
            import base64
            audio_b64 = base64.b64encode(audio_data).decode("ascii")
            session.conversation.append_audio(audio_b64)
            return True
        except Exception as e:
            logger.error(f"[ASR] Failed to send audio: {e}")
            raise

    def end_session(self, session: ASRSession, timeout: int = 20) -> str:
        """
        结束 ASR 会话

        Args:
            session: ASR 会话对象
            timeout: 等待超时时间（秒）

        Returns:
            str: 最终转写结果
        """
        if not session.conversation:
            return session.final_transcript

        try:
            session.conversation.end_session(timeout=timeout)
            session.status = "finished"
            logger.info(f"[ASR] Session {session.session_id} ended")
        except Exception as e:
            logger.error(f"[ASR] Error ending session: {e}")
        finally:
            self._cleanup_session(session.session_id)

        return session.final_transcript

    def close_session(self, session: ASRSession):
        """
        关闭 ASR 会话（立即终止）

        Args:
            session: ASR 会话对象
        """
        if session.conversation:
            try:
                session.conversation.close()
            except Exception as e:
                logger.error(f"[ASR] Error closing session: {e}")

        session.status = "closed"
        self._cleanup_session(session.session_id)

    def _cleanup_session(self, session_id: str):
        """清理会话资源"""
        with self._session_lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                logger.info(f"[ASR] Cleaned up session: {session_id}")

    def get_session(self, session_id: str) -> Optional[ASRSession]:
        """获取会话"""
        with self._session_lock:
            return self._sessions.get(session_id)

    def get_all_sessions(self) -> Dict[str, ASRSession]:
        """获取所有会话"""
        with self._session_lock:
            return dict(self._sessions)


_asr_service_instance: Optional[ASRService] = None
_service_lock = threading.Lock()


def get_asr_service() -> ASRService:
    """获取 ASR 服务单例"""
    global _asr_service_instance
    if _asr_service_instance is None:
        with _service_lock:
            if _asr_service_instance is None:
                _asr_service_instance = ASRService()
                _asr_service_instance.initialize()
    return _asr_service_instance