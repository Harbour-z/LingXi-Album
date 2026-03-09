import { create } from 'zustand';
import { voiceService, ASREvent, ASRConfig } from '../api/voiceService';

export type VoiceStatus = 
  | 'idle'           // 空闲状态
  | 'connecting'     // 正在连接
  | 'connected'      // 已连接
  | 'recording'      // 正在录音
  | 'processing'     // 正在处理
  | 'error';         // 错误状态

export interface VoiceState {
  status: VoiceStatus;
  isRecording: boolean;
  isConnected: boolean;
  partialTranscript: string;
  finalTranscript: string;
  error: string | null;
  sessionId: string | null;
  audioLevel: number;
  language: string;
  permissionGranted: boolean | null;
}

interface VoiceActions {
  connect: (config?: Partial<ASRConfig>) => Promise<void>;
  disconnect: () => void;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  setLanguage: (language: string) => void;
  clearTranscript: () => void;
  setError: (error: string | null) => void;
  setAudioLevel: (level: number) => void;
  checkPermission: () => Promise<boolean>;
}

export type VoiceStore = VoiceState & VoiceActions;

export const useVoiceStore = create<VoiceStore>((set, get) => ({
  status: 'idle',
  isRecording: false,
  isConnected: false,
  partialTranscript: '',
  finalTranscript: '',
  error: null,
  sessionId: null,
  audioLevel: 0,
  language: 'zh',
  permissionGranted: null,

  checkPermission: async () => {
    try {
      const result = await navigator.mediaDevices.getUserMedia({ audio: true });
      result.getTracks().forEach(track => track.stop());
      set({ permissionGranted: true });
      return true;
    } catch {
      set({ permissionGranted: false });
      return false;
    }
  },

  connect: async (config?: Partial<ASRConfig>) => {
    const { language } = get();
    set({ status: 'connecting', error: null });

    try {
      voiceService.setEventCallback((event: ASREvent) => {
        handleASREvent(event, set);
      });

      await voiceService.connect({
        language,
        ...config,
      });

      set({
        status: 'connected',
        isConnected: true,
        sessionId: voiceService.getSessionId(),
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : '连接失败';
      set({
        status: 'error',
        error: message,
        isConnected: false,
      });
    }
  },

  disconnect: () => {
    voiceService.disconnect();
    set({
      status: 'idle',
      isRecording: false,
      isConnected: false,
      sessionId: null,
      partialTranscript: '',
      audioLevel: 0,
    });
  },

  startRecording: async () => {
    const { isConnected, language, permissionGranted } = get();

    if (permissionGranted === false) {
      set({ error: '麦克风权限被拒绝，请在浏览器设置中允许访问麦克风' });
      return;
    }

    try {
      if (!isConnected) {
        await get().connect({ language });
      }

      await voiceService.startRecording();
      set({ status: 'recording', isRecording: true, error: null });
    } catch (error) {
      const message = error instanceof Error ? error.message : '录音启动失败';
      set({
        status: 'error',
        error: message,
        isRecording: false,
      });
    }
  },

  stopRecording: () => {
    voiceService.stopRecording();
    set({
      status: 'processing',
      isRecording: false,
      audioLevel: 0,
    });
  },

  setLanguage: (language: string) => {
    set({ language });
  },

  clearTranscript: () => {
    set({ partialTranscript: '', finalTranscript: '' });
  },

  setError: (error: string | null) => {
    set({ error, status: error ? 'error' : 'idle' });
  },

  setAudioLevel: (level: number) => {
    set({ audioLevel: level });
  },
}));

function handleASREvent(event: ASREvent, set: any) {
  switch (event.type) {
    case 'connected':
      set({ status: 'connected', isConnected: true });
      break;

    case 'disconnected':
      set({
        status: 'idle',
        isConnected: false,
        isRecording: false,
        sessionId: null,
      });
      break;

    case 'session.ready':
      set({ sessionId: event.session_id });
      break;

    case 'recording.started':
      set({ status: 'recording', isRecording: true });
      break;

    case 'recording.stopped':
      set({ status: 'processing', isRecording: false, audioLevel: 0 });
      break;

    case 'transcript.partial':
      if (event.text) {
        set({ partialTranscript: event.text });
      }
      break;

    case 'transcript.final':
      if (event.text) {
        set((state: VoiceStore) => ({
        finalTranscript: state.finalTranscript + event.text,
        partialTranscript: '',
      }));
      }
      break;

    case 'session.end':
      set({
        status: 'idle',
        isRecording: false,
        audioLevel: 0,
      });
      break;

    case 'error':
      set({
        status: 'error',
        error: event.message || '未知错误',
        isRecording: false,
      });
      break;

    default:
      break;
  }
}