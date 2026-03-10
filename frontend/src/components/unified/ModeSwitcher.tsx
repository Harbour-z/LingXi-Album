import React from 'react';
import { Segmented } from 'antd';
import { HomeOutlined, MessageOutlined, SearchOutlined } from '@ant-design/icons';
import type { ViewMode } from '../../store/unifiedStore';

interface ModeSwitcherProps {
  currentMode: ViewMode;
  onModeChange: (mode: 'home' | 'chat' | 'search') => void;
}

export const ModeSwitcher: React.FC<ModeSwitcherProps> = ({ currentMode, onModeChange }) => {
  const options = [
    { value: 'home', icon: <HomeOutlined />, label: '首页' },
    { value: 'chat', icon: <MessageOutlined />, label: '对话' },
    { value: 'search', icon: <SearchOutlined />, label: '搜索' },
  ];

  return (
    <Segmented
      value={currentMode}
      onChange={(value) => onModeChange(value as 'home' | 'chat' | 'search')}
      options={options}
      size="large"
      style={{
        backgroundColor: 'rgba(0,0,0,0.04)',
        padding: 4,
        borderRadius: 12,
      }}
    />
  );
};
