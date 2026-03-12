import React, { useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { List, Button, Empty, Popconfirm, Tag, Space, Typography } from 'antd';
import {
    MessageOutlined,
    DeleteOutlined,
    PlusOutlined,
    ClockCircleOutlined
} from '@ant-design/icons';
import { useConversationStore } from '../../store/conversationStore';
import type { ConversationListItem } from '../../types/conversation';

const { Text } = Typography;

export const ConversationHistory: React.FC = () => {
    const navigate = useNavigate();
    const {
        conversations,
        isLoading,
        loadConversations,
        deleteConversation,
        createNewConversation,
        loadConversation,
        clearCurrentConversation,
    } = useConversationStore();

    useEffect(() => {
        loadConversations();
    }, [loadConversations]);

    const handleDelete = useCallback(async (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        try {
            await deleteConversation(id);
        } catch (error) {
            console.error('Failed to delete conversation:', error);
        }
    }, [deleteConversation]);

    const handleCreateNew = useCallback(async () => {
        try {
            // 清除当前对话状态
            await clearCurrentConversation();
            // 创建新对话
            const newConversation = await createNewConversation();
            // 导航到首页的聊天模式
            navigate(`/?mode=chat&conversationId=${newConversation.id}`);
        } catch (error) {
            console.error('Failed to create new conversation:', error);
        }
    }, [createNewConversation, clearCurrentConversation, navigate]);

    const handleConversationClick = useCallback(async (item: ConversationListItem) => {
        try {
            // 加载对话数据
            await loadConversation(item.id);
            // 导航到首页的聊天模式，带上 conversationId 参数
            navigate(`/?mode=chat&conversationId=${item.id}`);
        } catch (error) {
            console.error('Failed to load conversation:', error);
        }
    }, [loadConversation, navigate]);

    const formatDate = (date: Date) => {
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) return '今天';
        if (days === 1) return '昨天';
        if (days < 7) return `${days}天前`;
        if (days < 30) return `${Math.floor(days / 7)}周前`;
        return date.toLocaleDateString('zh-CN');
    };

    const renderListItem = (item: ConversationListItem) => (
        <List.Item
            key={item.id}
            style={{
                cursor: 'pointer',
                borderRadius: 8,
                marginBottom: 8,
                padding: 12,
                border: '1px solid #f0f0f0',
                transition: 'all 0.3s',
            }}
            onClick={() => handleConversationClick(item)}
            actions={[
                <Popconfirm
                    key="delete"
                    title="确定要删除这个对话吗？"
                    onConfirm={(e) => handleDelete(item.id, e as React.MouseEvent)}
                    okText="确定"
                    cancelText="取消"
                >
                    <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        size="small"
                        onClick={(e) => e.stopPropagation()}
                    />
                </Popconfirm>,
            ]}
        >
            <List.Item.Meta
                avatar={<MessageOutlined style={{ fontSize: 24, color: '#1677ff' }} />}
                title={
                    <Space>
                        <span style={{ fontWeight: 600 }}>{item.title}</span>
                        <Tag color="blue">{item.messageCount} 条消息</Tag>
                    </Space>
                }
                description={
                    <div>
                        <div style={{ marginBottom: 4, color: '#666' }}>
                            {item.preview}
                        </div>
                        <Space size="small">
                            <span style={{ fontSize: 12, color: '#999' }}>
                                <ClockCircleOutlined /> {formatDate(item.updatedAt)}
                            </span>
                        </Space>
                    </div>
                }
            />
        </List.Item>
    );

    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ padding: 16, borderBottom: '1px solid #f0f0f0' }}>
                <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={handleCreateNew}
                    block
                    size="large"
                >
                    新建对话
                </Button>
            </div>

            {/* 搜索功能暂未完善提示 */}
            <div style={{ padding: '8px 16px', background: '#fafafa' }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                    💡 搜索功能正在完善中，敬请期待
                </Text>
            </div>

            <div style={{ flex: 1, overflow: 'auto', padding: 16 }}>
                {isLoading ? (
                    <div style={{ textAlign: 'center', padding: 40 }}>
                        <div>加载中...</div>
                    </div>
                ) : conversations.length === 0 ? (
                    <Empty
                        description="暂无对话历史，点击上方按钮开始新对话"
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                    />
                ) : (
                    <List
                        dataSource={conversations}
                        renderItem={renderListItem}
                        style={{ background: '#fff' }}
                    />
                )}
            </div>
        </div>
    );
};