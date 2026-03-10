import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Empty, Spin, Typography, Space, Card, Tag, Button, InputNumber, Flex, message, theme } from 'antd';
import {
  MessageOutlined,
  ReloadOutlined,
  ArrowRightOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { searchImages } from '../../api/search';
import type { ImageResult } from '../../api/types';
import { useUnifiedStore } from '../../store/unifiedStore';
import { useThemeStore } from '../../store/themeStore';
import { VirtualImageGrid } from './VirtualImageGrid';
import { useDebounce } from '../../hooks/useDebounce';

const { Title, Text } = Typography;

export const SearchResultsView: React.FC = () => {
  const navigate = useNavigate();
  const [, setSearchParams] = useSearchParams();
  const { isDarkMode } = useThemeStore();
  const { searchQuery, topK, setSearchResults, searchResults } = useUnifiedStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [localTopK, setLocalTopK] = useState(topK);
  const { token } = theme.useToken();
  const debouncedSearchQuery = useDebounce(searchQuery, 500);

  useEffect(() => {
    const performSearch = async () => {
      if (!debouncedSearchQuery.trim()) {
        setError('请输入搜索词');
        setSearchResults(null);
        return;
      }

      setLoading(true);
      setError(null);
      setSearchResults(null);

      try {
        const response = await searchImages({ query_text: debouncedSearchQuery, top_k: localTopK });
        setSearchResults(response.data);
        setLocalTopK(localTopK);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : '搜索失败，请稍后重试';
        setError(errorMessage);
        message.error(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    performSearch();
  }, [debouncedSearchQuery, localTopK, setSearchResults]);

  const handleImageClick = useCallback((image: ImageResult) => {
    navigate(`/gallery?image_id=${image.id}`);
  }, [navigate]);

  const handleSearchAgain = () => {
    setSearchParams({});
  };

  const handleStartChat = () => {
    setSearchParams({ mode: 'chat' });
  };

  const handleTopKChange = (value: number | null) => {
    if (value && value !== localTopK) {
      setLocalTopK(value);
    }
  };

  return (
    <div style={{ maxWidth: 1400, margin: '0 auto', padding: '24px' }}>
      <div style={{ marginBottom: 24 }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Flex justify="space-between" align="center">
            <div>
              <Title level={2} style={{ margin: 0 }}>
                <Space>
                  <SearchOutlined style={{ color: token.colorPrimary }} />
                  搜索结果
                </Space>
              </Title>
              <Text type="secondary">
                {loading ? '正在搜索...' : `找到 ${searchResults?.length || 0} 张图片`}
                {searchQuery && ` · "${searchQuery}"`}
              </Text>
            </div>
            <Space>
              <Button
                icon={<ReloadOutlined />}
                onClick={handleSearchAgain}
                disabled={loading}
              >
                重新搜索
              </Button>
              <Button
                type="primary"
                icon={<MessageOutlined />}
                onClick={handleStartChat}
              >
                继续对话
              </Button>
            </Space>
          </Flex>

          <Card
            variant="borderless"
            style={{
              borderRadius: 16,
              border: `1px solid ${isDarkMode ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.04)'}`,
              backgroundColor: isDarkMode ? 'rgba(30,28,25,0.8)' : 'rgba(255,255,255,0.8)',
            }}
          >
            <Flex justify="space-between" align="center">
              <Space>
                <Text type="secondary">搜索词:</Text>
                <Text strong style={{ fontSize: 16 }}>{searchQuery}</Text>
                {searchResults && searchResults.length > 0 && (
                  <Tag color="green">匹配度: {searchResults[0].score.toFixed(2)}</Tag>
                )}
              </Space>
              <Space align="center">
                <Text type="secondary">显示结果:</Text>
                <InputNumber
                  min={1}
                  max={100}
                  value={localTopK}
                  onChange={handleTopKChange}
                  disabled={loading}
                  style={{ width: 80 }}
                />
                <Text type="secondary">条</Text>
              </Space>
            </Flex>
          </Card>
        </Space>
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text type="secondary">正在为您搜索...</Text>
          </div>
        </div>
      )}

      {!loading && error && (
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <Empty
            description={error}
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Button type="primary" icon={<ArrowRightOutlined />} onClick={handleSearchAgain}>
              重新搜索
            </Button>
          </Empty>
        </div>
      )}

      {!loading && !error && (!searchResults || searchResults.length === 0) && (
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <Empty
            description="未找到匹配的图片，尝试使用不同的关键词或调整搜索条件"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Button type="primary" icon={<ArrowRightOutlined />} onClick={handleSearchAgain}>
              重新搜索
            </Button>
          </Empty>
        </div>
      )}

      {!loading && !error && searchResults && searchResults.length > 0 && (
        <div>
          <VirtualImageGrid
            images={searchResults}
            onImageClick={handleImageClick}
            containerHeight={600}
            itemHeight={280}
          />

          {searchResults.length >= localTopK && (
            <div style={{ textAlign: 'center', marginTop: 32 }}>
              <Button
                size="large"
                onClick={() => handleTopKChange(localTopK + 20)}
                style={{ borderRadius: 24 }}
              >
                加载更多结果
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
