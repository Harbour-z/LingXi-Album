/**
 * ChatPage - 重构版
 * 
 * 与 ChatView 统一架构：
 * 1. 消息状态统一从 conversationStore 获取
 * 2. chatStore 仅用于 API 调用
 */
import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  Layout,
  Input,
  Button,
  Avatar,
  Card,
  Space,
  Typography,
  Image,
  Tag,
  Spin,
  Tooltip,
  Modal,
  message as antdMessage,
} from 'antd';
import {
  SendOutlined,
  UserOutlined,
  RobotOutlined,
  DeleteOutlined,
  PictureOutlined,
  BulbOutlined,
  PlusOutlined,
  HistoryOutlined,
} from '@ant-design/icons';
import { useChatStore } from '../store/chatStore';
import { useConversationStore } from '../store/conversationStore';
import type { ChatMessage } from '../api/types';
import { MarkdownRenderer } from '../components/common/MarkdownRenderer';
import { VoiceInput } from '../components/common/VoiceInput';
import { InputBubble } from '../components/chat/InputBubble';

const { Content, Footer } = Layout;
const { Text } = Typography;
const { TextArea } = Input;

export const ChatPage: React.FC = () => {
  // chatStore - 仅用于 API 调用状态
  const { isLoading, sendMessage, clearSession, setOnNewMessage } = useChatStore();

  // conversationStore - 消息状态的唯一来源
  const {
    currentConversation,
    createNewConversation,
    loadConversation,
    addMessageToCurrent,
    clearCurrentConversation,
    deleteConversation,
    loadConversations,
  } = useConversationStore();

  const [inputValue, setInputValue] = useState('');
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [isRestoring, setIsRestoring] = useState(false);

  // 用于追踪正在加载的对话ID
  const loadingRef = useRef<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 从 conversationStore 获取消息（统一数据源）
  const messages = currentConversation?.messages || [];

  // Initialize conversationId from URL params
  const getConversationIdFromUrl = useCallback(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('conversationId');
  }, []);

  // 设置消息回调
  useEffect(() => {
    setOnNewMessage((message: ChatMessage) => {
      if (currentConversation) {
        addMessageToCurrent(message);
      }
    });

    return () => setOnNewMessage(null);
  }, [currentConversation, addMessageToCurrent, setOnNewMessage]);

  // Load conversation from URL params
  useEffect(() => {
    const convId = getConversationIdFromUrl();

    if (!convId) {
      setIsRestoring(false);
      loadingRef.current = null;
      return;
    }

    // 如果正在加载同一个对话，跳过
    if (loadingRef.current === convId) {
      return;
    }

    // 如果已经加载了这个对话，跳过
    if (currentConversation?.id === convId) {
      setIsRestoring(false);
      loadingRef.current = null;
      return;
    }

    // 开始加载
    loadingRef.current = convId;
    setIsRestoring(true);

    loadConversation(convId).catch(err => {
      console.error('Failed to load conversation:', err);
      const errorMsg = err instanceof Error ? err.message : '加载对话历史失败';
      antdMessage.error({
        content: `加载对话失败: ${errorMsg}`,
        duration: 5,
      });
    }).finally(() => {
      setIsRestoring(false);
      loadingRef.current = null;
    });
  }, [getConversationIdFromUrl, currentConversation?.id, loadConversation]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = useCallback(async () => {
    if (!inputValue.trim() || isLoading) return;

    const query = inputValue.trim();
    setInputValue('');

    // Create new conversation if not exists
    let conversation = currentConversation;
    if (!conversation) {
      conversation = await createNewConversation();
      // Update URL with conversation ID
      window.history.pushState({}, '', `/chat?conversationId=${conversation.id}`);
    }

    // 构建用户消息
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      type: 'user',
      content: query,
      timestamp: new Date(),
    };

    // 先保存用户消息
    await addMessageToCurrent(userMessage);

    // 发送到后端
    await sendMessage(query);
  }, [
    inputValue,
    isLoading,
    currentConversation,
    createNewConversation,
    addMessageToCurrent,
    sendMessage
  ]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  const handleNewConversation = useCallback(async () => {
    clearSession();
    await clearCurrentConversation();
    window.history.pushState({}, '', '/chat');
  }, [clearSession, clearCurrentConversation]);

  const handleDeleteConversation = useCallback(async () => {
    if (currentConversation) {
      await deleteConversation(currentConversation.id);
      clearSession();
      window.history.pushState({}, '', '/chat');
    }
  }, [currentConversation, deleteConversation, clearSession]);

  const renderMessage = useCallback((msg: ChatMessage) => {
    const isUser = msg.type === 'user';
    const isSystem = msg.type === 'system';

    return (
      <div
        key={msg.id}
        style={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          marginBottom: 24,
        }}
      >
        <Space align="start" size={16} style={{ flexDirection: isUser ? 'row-reverse' : 'row' }}>
          <Avatar
            icon={
              isUser ? <UserOutlined /> :
                isSystem ? <BulbOutlined /> :
                  <RobotOutlined />
            }
            style={{
              backgroundColor: isUser ? '#1677ff' : isSystem ? '#faad14' : '#52c41a',
              flexShrink: 0
            }}
          />
          <div style={{ maxWidth: 600 }}>
            <Card
              size="small"
              variant="borderless"
              style={{
                backgroundColor: isUser ? '#e6f7ff' : isSystem ? '#fffbe6' : '#f6f6f6',
                borderRadius: isUser ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
                boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                border: isSystem ? '1px solid #ffe58f' : undefined
              }}
              styles={{ body: { padding: '12px 16px' } }}
            >
              {isUser ? (
                <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                  {msg.content}
                </div>
              ) : (
                <MarkdownRenderer content={msg.content} />
              )}
            </Card>

            {msg.images && msg.images.length > 0 && (
              <div style={{ marginTop: 12 }}>
                <Space size="small" style={{ marginBottom: 8 }}>
                  <PictureOutlined />
                  <Text type="secondary" style={{ fontSize: 12 }}>找到 {msg.images.length} 张图片</Text>
                </Space>
                <div style={{
                  background: '#f0f0f0',
                  padding: 8,
                  borderRadius: 8,
                  overflowX: 'auto',
                  whiteSpace: 'nowrap'
                }}>
                  <Image.PreviewGroup>
                    <Space size={8}>
                      {msg.images.map(img => (
                        <div key={img.id} style={{ width: 100, height: 100, borderRadius: 4, overflow: 'hidden', display: 'inline-block' }}>
                          <Image
                            src={img.preview_url || `/api/v1/storage/images/${img.id}`}
                            width={100}
                            height={100}
                            style={{ objectFit: 'cover' }}
                          />
                        </div>
                      ))}
                    </Space>
                  </Image.PreviewGroup>
                </div>
              </div>
            )}

            {msg.suggestions && msg.suggestions.length > 0 && (
              <div style={{ marginTop: 12 }}>
                <Space size={[8, 8]} wrap>
                  {msg.suggestions.map((s, i) => (
                    <Tag
                      key={i}
                      icon={<BulbOutlined />}
                      color="blue"
                      style={{ cursor: 'pointer', borderRadius: 12 }}
                      onClick={() => setInputValue(s)}
                    >
                      {s}
                    </Tag>
                  ))}
                </Space>
              </div>
            )}

            <div style={{ textAlign: isUser ? 'right' : 'left', marginTop: 4 }}>
              <Text type="secondary" style={{ fontSize: 10 }}>
                {new Date(msg.timestamp).toLocaleTimeString()}
              </Text>
            </div>
          </div>
        </Space>
      </div>
    );
  }, []);

  return (
    <Layout style={{ height: 'calc(100vh - 100px)', background: 'transparent' }}>
      <div style={{
        position: 'absolute',
        top: -60,
        right: 0,
        zIndex: 1
      }}>
        <Space>
          <Tooltip title="对话历史">
            <Button
              type="text"
              icon={<HistoryOutlined />}
              onClick={() => setShowHistoryModal(true)}
            />
          </Tooltip>
          {currentConversation && messages.length > 0 && (
            <Tooltip title="删除当前对话">
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
                onClick={handleDeleteConversation}
              />
            </Tooltip>
          )}
        </Space>
      </div>

      <Content style={{ overflowY: 'auto', padding: '0 16px', scrollBehavior: 'smooth' }}>
        {isRestoring ? (
          <div style={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#999'
          }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>正在加载对话历史...</div>
          </div>
        ) : messages.length === 0 ? (
          <div style={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#999'
          }}>
            <Avatar size={64} icon={<RobotOutlined />} style={{ backgroundColor: '#f0f0f0', color: '#ccc', marginBottom: 24 }} />
            <Typography.Title level={4} style={{ color: '#666' }}>有什么可以帮您？</Typography.Title>
            <Space wrap style={{ maxWidth: 600, justifyItems: 'center', justifyContent: 'center' }}>
              {['查找去年的海边照片', '搜索红色的跑车', '最近上传的文档'].map(text => (
                <Button key={text} shape="round" onClick={() => setInputValue(text)}>
                  {text}
                </Button>
              ))}
            </Space>
          </div>
        ) : (
          <div style={{ maxWidth: 800, margin: '0 auto', paddingBottom: 20 }}>
            {messages.map(renderMessage)}
            {isLoading && (
              <div style={{ display: 'flex', marginBottom: 24 }}>
                <Space align="start" size={16}>
                  <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#52c41a' }} />
                  <Card size="small" variant="borderless" style={{ backgroundColor: '#f6f6f6', borderRadius: '4px 16px 16px 16px' }}>
                    <Space>
                      <Spin size="small" />
                      <Text type="secondary">正在思考...</Text>
                    </Space>
                  </Card>
                </Space>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </Content>

      <Footer style={{ background: 'transparent', padding: '16px 0' }}>
        <div style={{ maxWidth: 800, margin: '0 auto' }}>
          <InputBubble isTyping={inputValue.length > 0}>
            <VoiceInput
              onTranscript={(text) => setInputValue(prev => prev ? prev + ' ' + text : text)}
              disabled={isLoading}
              size="large"
              showLanguageSelector={true}
            />
            <TextArea
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入消息... (支持语音输入)"
              autoSize={{ minRows: 1, maxRows: 6 }}
              variant="borderless"
              style={{
                resize: 'none',
                padding: '8px 12px',
                fontSize: 15,
                lineHeight: 1.6,
                flex: 1
              }}
              disabled={isLoading}
            />
            <Button
              type="primary"
              shape="circle"
              icon={<SendOutlined />}
              size="large"
              onClick={handleSend}
              disabled={!inputValue.trim() || isLoading}
              style={{ marginBottom: 4, marginRight: 4 }}
            />
          </InputBubble>
          <div style={{ textAlign: 'center', marginTop: 8 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>AI生成内容可能不准确，请核实重要信息 | 支持语音输入</Text>
          </div>
        </div>
      </Footer>

      <Modal
        title="对话历史"
        open={showHistoryModal}
        onCancel={() => setShowHistoryModal(false)}
        footer={null}
        width={800}
        style={{ top: 20 }}
      >
        <div style={{ maxHeight: 600, overflowY: 'auto' }}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleNewConversation}
            style={{ marginBottom: 16 }}
            block
          >
            新建对话
          </Button>
          {currentConversation && (
            <div style={{
              padding: 12,
              background: '#e6f7ff',
              borderRadius: 8,
              marginBottom: 16,
              border: '1px solid #1677ff'
            }}>
              <Space direction="vertical" size="small">
                <Text strong>当前对话</Text>
                <Text type="secondary">{currentConversation.title}</Text>
                <Text type="secondary">{messages.length} 条消息</Text>
              </Space>
            </div>
          )}
          <div style={{ marginTop: 16 }}>
            <Text type="secondary">点击下方卡片查看对话历史</Text>
          </div>
          <Button
            type="link"
            onClick={() => {
              loadConversations();
              window.location.href = '/conversations';
            }}
            style={{ marginTop: 8 }}
          >
            查看完整历史
          </Button>
        </div>
      </Modal>
    </Layout>
  );
};