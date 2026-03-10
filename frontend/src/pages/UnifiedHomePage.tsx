import React, { useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useUnifiedStore } from '../store/unifiedStore';
import { HomePageView } from '../components/unified/HomePageView';
import { ChatView } from '../components/unified/ChatView';
import { SearchResultsView } from '../components/unified/SearchResultsView';
import { ModeSwitcher } from '../components/unified/ModeSwitcher';
import { useUnifiedDataPersistence } from '../hooks/useUnifiedDataPersistence';
import { Flex, Button, theme } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';

export const UnifiedHomePage: React.FC = () => {
  const { token } = theme.useToken();
  const [searchParams, setSearchParams] = useSearchParams();
  const { resetToHome } = useUnifiedStore();
  const contentRef = useRef<HTMLDivElement>(null);

  useUnifiedDataPersistence();

  // 直接从 URL 读取 viewMode，不再使用 unifiedStore 管理
  const modeParam = searchParams.get('mode');
  const viewMode = (modeParam === 'chat' || modeParam === 'search') ? modeParam : 'home';

  useEffect(() => {
    if (contentRef.current) {
      contentRef.current.scrollTop = 0;
    }
  }, [viewMode]);

  const handleBackToHome = () => {
    resetToHome();
    setSearchParams({});
  };

  const handleGoBack = () => {
    // 简单实现：返回按钮直接回到首页
    handleBackToHome();
  };

  const handleModeChange = (mode: 'home' | 'chat' | 'search') => {
    if (mode === 'home') {
      handleBackToHome();
    } else {
      setSearchParams({ mode });
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: 'calc(100vh - 140px)',
      position: 'relative'
    }}>
      <Flex
        justify="space-between"
        align="center"
        style={{
          marginBottom: 16,
          padding: viewMode === 'home' ? '0 24px' : '0 24px 0 0'
        }}
      >
        {viewMode !== 'home' && (
          <Button
            type="text"
            icon={<ArrowLeftOutlined />}
            onClick={handleGoBack}
            style={{ color: token.colorTextSecondary }}
          >
            返回
          </Button>
        )}
        <ModeSwitcher currentMode={viewMode} onModeChange={handleModeChange} />
        {viewMode !== 'home' && <div style={{ width: 88 }} />}
      </Flex>

      <div
        ref={contentRef}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: viewMode === 'home' ? '0 24px' : '0 24px 0 0',
          scrollBehavior: 'smooth'
        }}
      >
        {viewMode === 'home' && <HomePageView />}
        {viewMode === 'chat' && <ChatView />}
        {viewMode === 'search' && <SearchResultsView />}
      </div>
    </div>
  );
};