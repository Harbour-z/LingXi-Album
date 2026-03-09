import React, { useEffect, useCallback, useRef, useState } from 'react';
import { Button, Tooltip, Modal, Typography, Space, Select, message } from 'antd';
import {
  AudioOutlined,
  AudioMutedOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { useVoiceStore } from '../../store/voiceStore';
import { AudioWaveform } from './AudioWaveform';

const { Text } = Typography;

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
  size?: 'small' | 'middle' | 'large';
  showLanguageSelector?: boolean;
}

const SUPPORTED_LANGUAGES = [
  { value: 'zh', label: '中文' },
  { value: 'en', label: 'English' },
  { value: 'yue', label: '粤语' },
  { value: 'ja', label: '日本語' },
  { value: 'ko', label: '한국어' },
];

export const VoiceInput: React.FC<VoiceInputProps> = ({
  onTranscript,
  disabled = false,
  size = 'large',
  showLanguageSelector = true,
}) => {
  const {
    status,
    isRecording,
    isConnected,
    partialTranscript,
    finalTranscript,
    error,
    language,
    permissionGranted,
    startRecording,
    stopRecording,
    disconnect,
    setLanguage,
    clearTranscript,
    checkPermission,
  } = useVoiceStore();

  const [showModal, setShowModal] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const pressTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isPressingRef = useRef(false);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationRef = useRef<number | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    checkPermission();
    return () => {
      disconnect();
    };
  }, []);

  useEffect(() => {
    if (finalTranscript && status === 'idle') {
      if (finalTranscript.trim()) {
        onTranscript(finalTranscript.trim());
        clearTranscript();
        setShowModal(false);
      }
    }
  }, [finalTranscript, status, onTranscript, clearTranscript]);

  useEffect(() => {
    if (error) {
      message.error(error);
    }
  }, [error]);

  const startAudioAnalysis = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 256;

      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);

      const updateLevel = () => {
        if (analyserRef.current && isRecording) {
          analyserRef.current.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
          setAudioLevel(average / 255);
        }
        animationRef.current = requestAnimationFrame(updateLevel);
      };

      updateLevel();
    } catch (err) {
      console.error('Failed to start audio analysis:', err);
    }
  }, [isRecording]);

  const stopAudioAnalysis = useCallback(() => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }
    setAudioLevel(0);
  }, []);

  useEffect(() => {
    if (isRecording) {
      startAudioAnalysis();
    } else {
      stopAudioAnalysis();
    }
  }, [isRecording, startAudioAnalysis, stopAudioAnalysis]);

  const handlePressStart = useCallback(() => {
    if (disabled || permissionGranted === false) {
      setShowModal(true);
      return;
    }

    isPressingRef.current = true;
    pressTimerRef.current = setTimeout(() => {
      if (isPressingRef.current) {
        startRecording();
      }
    }, 200);
  }, [disabled, permissionGranted, startRecording]);

  const handlePressEnd = useCallback(() => {
    isPressingRef.current = false;
    if (pressTimerRef.current) {
      clearTimeout(pressTimerRef.current);
      pressTimerRef.current = null;
    }

    if (isRecording) {
      stopRecording();
    }
  }, [isRecording, stopRecording]);

  const handleClick = useCallback(() => {
    if (disabled) return;

    if (permissionGranted === false) {
      setShowModal(true);
      return;
    }

    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
      setShowModal(true);
    }
  }, [disabled, permissionGranted, isRecording, startRecording, stopRecording]);

  const handleModalClose = useCallback(() => {
    if (isRecording) {
      stopRecording();
    }
    setShowModal(false);
  }, [isRecording, stopRecording]);

  const handleLanguageChange = useCallback((value: string) => {
    setLanguage(value);
    clearTranscript();
  }, [setLanguage, clearTranscript]);

  const getStatusIcon = () => {
    switch (status) {
      case 'connecting':
        return <LoadingOutlined spin />;
      case 'recording':
        return <AudioOutlined style={{ color: '#ff4d4f' }} />;
      case 'processing':
        return <LoadingOutlined spin />;
      case 'error':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return permissionGranted === false ? <AudioMutedOutlined /> : <AudioOutlined />;
    }
  };

  const getStatusColor = () => {
    if (isRecording) return '#ff4d4f';
    if (status === 'error') return '#ff4d4f';
    if (status === 'connecting' || status === 'processing') return '#1677ff';
    return undefined;
  };

  const getTooltipTitle = () => {
    if (permissionGranted === false) return '点击授权麦克风';
    if (status === 'recording') return '正在录音...';
    if (status === 'processing') return '正在识别...';
    if (status === 'connecting') return '正在连接...';
    return '语音输入';
  };

  return (
    <>
      <Tooltip title={getTooltipTitle()}>
        <Button
          type={isRecording ? 'primary' : 'text'}
          shape="circle"
          icon={getStatusIcon()}
          size={size}
          onClick={handleClick}
          onMouseDown={handlePressStart}
          onMouseUp={handlePressEnd}
          onMouseLeave={handlePressEnd}
          onTouchStart={handlePressStart}
          onTouchEnd={handlePressEnd}
          disabled={disabled && permissionGranted !== false}
          danger={isRecording}
          style={{
            backgroundColor: getStatusColor(),
            borderColor: getStatusColor(),
          }}
        />
      </Tooltip>

      <Modal
        title={
          <Space>
            <AudioOutlined style={{ color: isRecording ? '#ff4d4f' : '#1677ff' }} />
            <span>语音输入</span>
          </Space>
        }
        open={showModal}
        onCancel={handleModalClose}
        footer={null}
        width={480}
        centered
      >
        <div style={{ padding: '24px 0' }}>
          {permissionGranted === false ? (
            <div style={{ textAlign: 'center' }}>
              <ExclamationCircleOutlined style={{ fontSize: 48, color: '#ff4d4f', marginBottom: 16 }} />
              <Typography.Title level={5}>需要麦克风权限</Typography.Title>
              <Text type="secondary">
                请在浏览器设置中允许访问麦克风，然后刷新页面重试。
              </Text>
              <div style={{ marginTop: 16 }}>
                <Button type="primary" onClick={() => window.location.reload()}>
                  刷新页面
                </Button>
              </div>
            </div>
          ) : (
            <>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center',
                minHeight: 80,
                marginBottom: 16 
              }}>
                <AudioWaveform
                  isRecording={isRecording}
                  audioLevel={audioLevel}
                  height={40}
                  barCount={32}
                  color={isRecording ? '#ff4d4f' : '#1677ff'}
                />
              </div>

              <div style={{ textAlign: 'center', marginBottom: 16 }}>
                {status === 'recording' && (
                  <Text type="danger">正在录音，请说话...</Text>
                )}
                {status === 'processing' && (
                  <Space>
                    <LoadingOutlined spin />
                    <Text type="secondary">正在识别...</Text>
                  </Space>
                )}
                {status === 'idle' && !finalTranscript && (
                  <Text type="secondary">点击下方按钮开始录音</Text>
                )}
              </div>

              {(partialTranscript || finalTranscript) && (
                <div style={{
                  background: '#f5f5f5',
                  borderRadius: 8,
                  padding: 16,
                  marginBottom: 16,
                  minHeight: 60,
                }}>
                  <Text>
                    {finalTranscript}
                    {partialTranscript && (
                      <Text type="secondary" style={{ marginLeft: 4 }}>
                        {partialTranscript}
                      </Text>
                    )}
                  </Text>
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'center', gap: 16 }}>
                {showLanguageSelector && (
                  <Select
                    value={language}
                    onChange={handleLanguageChange}
                    options={SUPPORTED_LANGUAGES}
                    style={{ width: 120 }}
                    disabled={isRecording}
                  />
                )}
                <Button
                  type={isRecording ? 'default' : 'primary'}
                  danger={isRecording}
                  icon={isRecording ? <CheckCircleOutlined /> : <AudioOutlined />}
                  onClick={isRecording ? stopRecording : startRecording}
                  loading={status === 'connecting'}
                  size="large"
                >
                  {isRecording ? '完成' : '开始录音'}
                </Button>
              </div>

              {finalTranscript && status === 'idle' && (
                <div style={{ marginTop: 16, textAlign: 'center' }}>
                  <Button
                    type="primary"
                    onClick={() => {
                      onTranscript(finalTranscript.trim());
                      clearTranscript();
                      setShowModal(false);
                    }}
                  >
                    使用此文本
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      </Modal>
    </>
  );
};

export default VoiceInput;