import React, { useState } from 'react';
import { Layout, Menu, Button, theme } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  MessageOutlined,
  PictureOutlined,
  CloudUploadOutlined,
  HomeOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  GithubOutlined,
  BulbOutlined,
  BulbFilled,
} from '@ant-design/icons';
import { useThemeStore } from '../../store/themeStore';

const { Header, Sider, Content } = Layout;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { isDarkMode, toggleTheme } = useThemeStore();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/chat',
      icon: <MessageOutlined />,
      label: '智能对话',
    },
    {
      key: '/gallery',
      icon: <PictureOutlined />,
      label: '图片画廊',
    },
    {
      key: '/upload',
      icon: <CloudUploadOutlined />,
      label: '上传图片',
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh', background: 'transparent' }}>
      <Sider trigger={null} collapsible collapsed={collapsed} theme={isDarkMode ? 'dark' : 'light'} style={{
        boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
        zIndex: 10,
        height: '100vh',
        position: 'sticky',
        top: 0,
        left: 0,
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <div style={{ 
            height: 64, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            borderBottom: '1px solid #f0f0f0' 
          }}>
            <h1 style={{ 
              fontSize: '1.2rem', 
              fontWeight: 'bold', 
              margin: 0,
              display: collapsed ? 'none' : 'block',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              color: isDarkMode ? '#fff' : 'rgba(0, 0, 0, 0.88)'
            }}>
              智能相册
            </h1>
            {collapsed && <span style={{ fontWeight: 'bold', color: isDarkMode ? '#fff' : 'rgba(0, 0, 0, 0.88)' }}>AI</span>}
          </div>
          <Menu
            theme={isDarkMode ? 'dark' : 'light'}
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
            style={{ borderRight: 0, flex: 1 }}
          />
          
          {/* GitHub Link */}
          <div style={{
            padding: '16px',
            borderTop: isDarkMode ? '1px solid #303030' : '1px solid #f0f0f0',
            display: 'flex',
            justifyContent: collapsed ? 'center' : 'flex-start'
          }}>
            <Button
              type="text"
              icon={<GithubOutlined style={{ fontSize: 18 }} />}
              onClick={() => window.open('https://github.com/harbour-z/ImgEmbedding2VecDB', '_blank')}
              block={!collapsed}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: collapsed ? 'center' : 'flex-start',
                height: 48,
                color: isDarkMode ? 'rgba(255, 255, 255, 0.65)' : 'rgba(0, 0, 0, 0.65)'
              }}
            >
              {!collapsed && <span style={{ marginLeft: 8 }}>GitHub 仓库</span>}
            </Button>
          </div>
        </div>
      </Sider>
      <Layout style={{ background: 'transparent' }}>
        <Header style={{ 
            padding: '0 24px 0 0', 
            // Remove background: colorBgContainer to allow transparency
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            position: 'sticky',
            top: 0,
            zIndex: 9,
            boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.03)',
            backdropFilter: 'blur(12px)',
            WebkitBackdropFilter: 'blur(12px)',
            backgroundColor: isDarkMode ? 'rgba(20, 20, 20, 0.7)' : 'rgba(255, 255, 255, 0.7)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', paddingLeft: 16 }}>
              <Button
                type="text"
                icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                onClick={() => setCollapsed(!collapsed)}
                style={{
                  fontSize: '16px',
                  width: 64,
                  height: 64,
                }}
              />
          </div>
          
          <Button 
            shape="circle" 
            icon={isDarkMode ? <BulbFilled /> : <BulbOutlined />} 
            onClick={toggleTheme}
            size="large"
            style={{ marginRight: 16 }}
            title={isDarkMode ? "切换到亮色模式" : "切换到暗黑模式"}
          />
        </Header>
        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            minHeight: 280,
            background: isDarkMode ? 'rgba(20, 20, 20, 0.4)' : 'rgba(255, 255, 255, 0.4)',
            backdropFilter: 'blur(20px) saturate(180%)',
            WebkitBackdropFilter: 'blur(20px) saturate(180%)',
            border: isDarkMode ? '1px solid rgba(255, 255, 255, 0.08)' : '1px solid rgba(255, 255, 255, 0.3)',
            boxShadow: isDarkMode ? '0 8px 32px 0 rgba(0, 0, 0, 0.37)' : '0 8px 32px 0 rgba(31, 38, 135, 0.07)',
            borderRadius: borderRadiusLG,
            overflow: 'auto',
            transition: 'all 0.2s',
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
