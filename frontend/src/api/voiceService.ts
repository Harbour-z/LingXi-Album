/**
 * ASR 语音识别服务
 * 通过 WebSocket 连接后端实时语音识别接口
 */

export interface ASRConfig {
  language: string;
  sampleRate: number;
  inputFormat: string;
  enableVad: boolean;
  vadThreshold: number;
  vadSilenceMs: number;
}

export interface ASREvent {
  type: string;
  session_id?: string;
  text?: string;
  is_final?: boolean;
  message?: string;
  config?: ASRConfig;
  final_transcript?: string;
}

export type ASREventCallback = (event: ASREvent) => void;

export class VoiceService {
  private ws: WebSocket | null = null;
  private sessionId: string | null = null;
  private eventCallback: ASREventCallback | null = null;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 3;
  private isConnecting: boolean = false;
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private isRecording: boolean = false;

  constructor() {
    this.handleMessage = this.handleMessage.bind(this);
    this.handleOpen = this.handleOpen.bind(this);
    this.handleClose = this.handleClose.bind(this);
    this.handleError = this.handleError.bind(this);
  }

  /**
   * 连接到 ASR WebSocket 服务
   */
  async connect(config: Partial<ASRConfig> = {}): Promise<boolean> {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return true;
    }

    if (this.isConnecting) {
      return false;
    }

    const defaultConfig: ASRConfig = {
      language: config.language || 'zh',
      sampleRate: config.sampleRate || 16000,
      inputFormat: config.inputFormat || 'pcm',
      enableVad: config.enableVad ?? true,
      vadThreshold: config.vadThreshold ?? 0.0,
      vadSilenceMs: config.vadSilenceMs ?? 400,
    };

    const params = new URLSearchParams({
      language: defaultConfig.language,
      sample_rate: defaultConfig.sampleRate.toString(),
      input_format: defaultConfig.inputFormat,
      enable_vad: defaultConfig.enableVad.toString(),
      vad_threshold: defaultConfig.vadThreshold.toString(),
      vad_silence_ms: defaultConfig.vadSilenceMs.toString(),
    });

    const wsUrl = `${this.getWebSocketBaseUrl()}/asr/realtime?${params}`;

    return new Promise((resolve, reject) => {
      try {
        this.isConnecting = true;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          this.handleOpen();
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          resolve(true);
        };

        this.ws.onmessage = this.handleMessage;
        this.ws.onclose = this.handleClose;
        this.ws.onerror = (error) => {
          this.handleError(error);
          this.isConnecting = false;
          reject(new Error('WebSocket connection failed'));
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  /**
   * 获取 WebSocket 基础 URL
   */
  private getWebSocketBaseUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}/api/v1`;
  }

  /**
   * 处理 WebSocket 打开事件
   */
  private handleOpen(): void {
    console.log('[VoiceService] WebSocket connected');
    this.emitEvent({ type: 'connected' });
  }

  /**
   * 处理 WebSocket 消息
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data) as ASREvent;
      
      if (data.type === 'session.ready') {
        this.sessionId = data.session_id || null;
        console.log('[VoiceService] Session ready:', this.sessionId);
      }

      this.emitEvent(data);
    } catch (error) {
      console.error('[VoiceService] Failed to parse message:', error);
    }
  }

  /**
   * 处理 WebSocket 关闭事件
   */
  private handleClose(event: CloseEvent): void {
    console.log('[VoiceService] WebSocket closed:', event.code, event.reason);
    this.ws = null;
    this.sessionId = null;
    this.emitEvent({ type: 'disconnected', message: event.reason });
  }

  /**
   * 处理 WebSocket 错误
   */
  private handleError(error: Event): void {
    console.error('[VoiceService] WebSocket error:', error);
    this.emitEvent({ type: 'error', message: 'WebSocket connection error' });
  }

  /**
   * 发送事件回调
   */
  private emitEvent(event: ASREvent): void {
    if (this.eventCallback) {
      this.eventCallback(event);
    }
  }

  /**
   * 设置事件回调
   */
  setEventCallback(callback: ASREventCallback): void {
    this.eventCallback = callback;
  }

  /**
   * 请求麦克风权限
   */
  async requestMicrophonePermission(): Promise<MediaStream | null> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
      this.mediaStream = stream;
      return stream;
    } catch (error) {
      console.error('[VoiceService] Failed to get microphone permission:', error);
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          throw new Error('麦克风权限被拒绝，请在浏览器设置中允许访问麦克风');
        } else if (error.name === 'NotFoundError') {
          throw new Error('未找到麦克风设备，请检查设备连接');
        }
      }
      throw new Error('无法访问麦克风，请检查权限设置');
    }
  }

  /**
   * 开始录音
   */
  async startRecording(): Promise<void> {
    if (this.isRecording) {
      return;
    }

    try {
      if (!this.mediaStream) {
        await this.requestMicrophonePermission();
      }

      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        await this.connect();
      }

      this.audioContext = new AudioContext({ sampleRate: 16000 });
      const source = this.audioContext.createMediaStreamSource(this.mediaStream!);
      
      const processor = this.audioContext.createScriptProcessor(4096, 1, 1);
      
      processor.onaudioprocess = (e) => {
        if (this.isRecording && this.ws?.readyState === WebSocket.OPEN) {
          const inputData = e.inputBuffer.getChannelData(0);
          const pcmData = this.float32ToPCM16(inputData);
          const base64Data = this.arrayBufferToBase64(pcmData);
          this.sendAudio(base64Data);
        }
      };

      source.connect(processor);
      processor.connect(this.audioContext.destination);

      this.isRecording = true;
      console.log('[VoiceService] Recording started');
      this.emitEvent({ type: 'recording.started' });

    } catch (error) {
      console.error('[VoiceService] Failed to start recording:', error);
      throw error;
    }
  }

  /**
   * 停止录音
   */
  stopRecording(): void {
    if (!this.isRecording) {
      return;
    }

    this.isRecording = false;

    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }

    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'end' }));
    }

    console.log('[VoiceService] Recording stopped');
    this.emitEvent({ type: 'recording.stopped' });
  }

  /**
   * 发送音频数据
   */
  private sendAudio(base64Audio: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'audio',
        data: base64Audio,
      }));
    }
  }

  /**
   * Float32 转 PCM16
   */
  private float32ToPCM16(float32Array: Float32Array): Int16Array {
    const int16Array = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
      const s = Math.max(-1, Math.min(1, float32Array[i]));
      int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return int16Array;
  }

  /**
   * ArrayBuffer 转 Base64
   */
  private arrayBufferToBase64(buffer: ArrayBuffer | Int16Array): string {
    const bytes = buffer instanceof Int16Array ? new Uint8Array(buffer.buffer) : new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    this.stopRecording();
    
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.sessionId = null;
    console.log('[VoiceService] Disconnected');
  }

  /**
   * 获取当前会话 ID
   */
  getSessionId(): string | null {
    return this.sessionId;
  }

  /**
   * 检查是否已连接
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * 检查是否正在录音
   */
  isCurrentlyRecording(): boolean {
    return this.isRecording;
  }
}

export const voiceService = new VoiceService();
export default voiceService;