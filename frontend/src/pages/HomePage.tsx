import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Input,
  Button,
  Card,
  Row,
  Col,
  Space,
  Flex,
  theme,
  Slider,
  Tooltip,
} from 'antd';
import {
  SearchOutlined,
  PictureOutlined,
  BulbOutlined,
} from '@ant-design/icons';
import { TypewriterEffect } from '../components/common/TypewriterEffect';
import { useThemeStore } from '../store/themeStore';
import { ImageSearchModal } from '../components/search/ImageSearchModal';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { isDarkMode } = useThemeStore();
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(10);
  const { token } = theme.useToken();
  const [currentSuggestions, setCurrentSuggestions] = useState<{ icon: string; text: string }[]>([]);
  const [isAnimating, setIsAnimating] = useState(false);
  const [titleParts, setTitleParts] = useState<{ text: string; style?: React.CSSProperties }[]>([]);
  const [isImageSearchOpen, setIsImageSearchOpen] = useState(false);

  // 首页标题变体列表
  const titleVariations = [
    [
      { text: '用语言描述，' },
      { text: '智能搜索', style: { color: token.colorPrimary } }
    ],
    [
      { text: '以自然语言，' },
      { text: '寻心中所想', style: { color: token.colorPrimary } }
    ],
    [
      { text: '懂你所想，' },
      { text: '搜你所见', style: { color: token.colorPrimary } }
    ],
    [
      { text: '语义理解，' },
      { text: '精准搜图', style: { color: token.colorPrimary } }
    ],
    [
      { text: '告别关键词，' },
      { text: '描述即所得', style: { color: token.colorPrimary } }
    ]
  ];

  const allSuggestions = [
    // 自然风景
    { icon: '🌅', text: '日出' }, { icon: '🏔️', text: '雪山' }, { icon: '🏖️', text: '海滩' }, { icon: '🌲', text: '森林' },
    // 萌宠
    { icon: '🐱', text: '猫咪特写' }, { icon: '🐕', text: '狗狗' }, { icon: '💤', text: '睡觉的猫' }, { icon: '🐾', text: '奔跑的狗' },
    // 美食
    { icon: '🍲', text: '火锅' }, { icon: '🍰', text: '蛋糕' }, { icon: '☕', text: '咖啡' }, { icon: '🥢', text: '家庭聚餐' },
    // 城市生活
    { icon: '📸', text: '街拍' }, { icon: '🌃', text: '夜景' }, { icon: '📚', text: '书店' }, { icon: '🚦', text: '繁忙的街道' },
    // 人物摄影
    { icon: '👨‍👩‍👧', text: '全家福' }, { icon: '💑', text: '情侣照' }, { icon: '🤳', text: '自拍' }, { icon: '🎓', text: '毕业照' },
    // 旅行记录
    { icon: '🗼', text: '地标建筑' }, { icon: '✈️', text: '飞机机翼' }, { icon: '🎫', text: '车票' }, { icon: '🎒', text: '旅行背包' },
    // 实用场景 (新增)
    { icon: '🆔', text: '证件照' }, { icon: '💬', text: '聊天截图' }, { icon: '🖼️', text: '微信图片' },
    { icon: '👶', text: '孩子成长' }, { icon: '📝', text: '工作资料' }, { icon: '📊', text: '会议白板' },
  ];

  const refreshSuggestions = () => {
    setIsAnimating(true);
    setTimeout(() => {
      // Fisher-Yates Shuffle
      const shuffled = [...allSuggestions];
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
      }
      setCurrentSuggestions(shuffled.slice(0, 4));
      setIsAnimating(false);
    }, 300); // 300ms transition
  };

  // 每次页面加载时随机选择一个话题和标题，并刷新建议
  React.useEffect(() => {
    const randomTitle = titleVariations[Math.floor(Math.random() * titleVariations.length)];
    setTitleParts(randomTitle);

    refreshSuggestions();
  }, []);

  const handleSearch = async () => {
    if (!query.trim()) return;
    // Redirect to Gallery for search results instead of Chat
    navigate(`/gallery?q=${encodeURIComponent(query)}&top_k=${topK}`);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const features = [
    { icon: <SearchOutlined style={{ fontSize: 24, color: token.colorPrimary }} />, title: '语义搜索', desc: '用自然语言描述，智能理解您的意图' },
    { icon: <PictureOutlined style={{ fontSize: 24, color: token.colorSuccess }} />, title: '以图搜图', desc: '上传图片，找到相似的照片' },
    { icon: <BulbOutlined style={{ fontSize: 24, color: token.colorWarning }} />, title: 'AI 理解', desc: '深度理解图片内容和场景' },
  ];

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '85vh',
      padding: '24px'
    }}>
      <div style={{ maxWidth: 900, width: '100%', textAlign: 'center' }}>
        <Flex vertical gap="large" style={{ width: '100%' }}>

          <div style={{ marginBottom: 48 }}>
            <Title level={1} style={{ fontSize: '3.5rem', marginBottom: 20, fontWeight: 700 }}>
              {titleParts.length > 0 && (
                <TypewriterEffect
                  parts={titleParts}
                  speed={150}
                  cursorColor={token.colorPrimary}
                />
              )}
            </Title>

            {/* 预设话题展示区 */}
            <Paragraph style={{ fontSize: '1.25rem', color: token.colorTextSecondary, maxWidth: 700, margin: '0 auto' }}>
              基于深度学习的图像语义理解，让您用自然语言找到任何想要的照片
            </Paragraph>
          </div>

          <Card
            variant="borderless"
            style={{
              boxShadow: '0 12px 48px rgba(72,60,48,0.08), 0 0 0 1px rgba(255,255,255,0.5) inset',
              borderRadius: 24,
              overflow: 'hidden',
              backdropFilter: 'blur(24px) saturate(200%)',
              WebkitBackdropFilter: 'blur(24px) saturate(200%)',
              backgroundColor: isDarkMode ? 'rgba(30, 28, 25, 0.5)' : 'rgba(255, 253, 250, 0.5)',
              border: `1px solid ${isDarkMode ? 'rgba(255,255,255,0.12)' : 'rgba(255,255,255,0.6)'}`,
            }}
            styles={{ body: { padding: 0 } }}
          >
            <div style={{ padding: '28px 28px 16px' }}>
              <TextArea
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="描述您想找的图片，例如：海边的日落、穿红色衣服的人..."
                autoSize={{ minRows: 2, maxRows: 6 }}
                variant="borderless"
                style={{ fontSize: 16, resize: 'none', lineHeight: 1.6 }}
              />
              <div style={{ marginTop: 16, padding: '0 12px' }}>
                <Row align="middle" gutter={16}>
                  <Col flex="none">
                    <Space size={4} align="center">
                      <Text type="secondary">显示结果数量: {topK}</Text>
                      <Tooltip title="设置搜索返回的最大图片数量，数量越多覆盖越广，但精确度可能略有下降">
                        <div style={{
                          width: 16,
                          height: 16,
                          borderRadius: '50%',
                          border: `1px solid ${token.colorTextQuaternary}`,
                          color: token.colorTextQuaternary,
                          fontSize: 12,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          cursor: 'help'
                        }}>?</div>
                      </Tooltip>
                    </Space>
                  </Col>
                  <Col flex="auto">
                    <Slider
                      min={1}
                      max={50}
                      value={topK}
                      onChange={setTopK}
                      tooltip={{ formatter: (value) => `展示前 ${value} 条结果` }}
                    />
                  </Col>
                </Row>
              </div>
            </div>
            <div style={{
              padding: '16px 28px 28px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              borderTop: `1px solid ${isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.04)'}`
            }}>
              <Space>
                <Button
                  type="text"
                  icon={<PictureOutlined />}
                  onClick={() => setIsImageSearchOpen(true)}
                >
                  以图搜图
                </Button>
              </Space>
              <Button
                type="primary"
                size="large"
                icon={<SearchOutlined />}
                shape="round"
                onClick={handleSearch}
                disabled={!query.trim()}
                style={{ paddingLeft: 32, paddingRight: 32 }}
              >
                搜索
              </Button>
            </div>
          </Card>

          <div style={{ marginTop: 40 }}>
            <Text type="secondary" style={{ display: 'block', marginBottom: 20, fontSize: 15 }}>试试这些搜索</Text>
            <Flex
              wrap
              gap="small"
              style={{
                justifyContent: 'center',
                opacity: isAnimating ? 0 : 1,
                transition: 'opacity 0.3s ease-in-out',
                width: '100%', // Ensure width for responsiveness
              }}
            >
              {currentSuggestions.map((item, index) => (
                <Button
                  key={index}
                  shape="round"
                  size="large"
                  onClick={() => {
                    navigate(`/gallery?q=${encodeURIComponent(item.text)}&top_k=${topK}`);
                  }}
                  style={{
                    height: 'auto',
                    padding: '10px 24px',
                    minWidth: 'auto',
                    borderRadius: 9999,
                    border: `1px solid ${token.colorBorderSecondary}`,
                    transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 6px 20px rgba(72,60,48,0.1)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <span style={{ fontSize: 18, marginRight: 8 }}>{item.icon}</span>
                  {item.text}
                </Button>
              ))}
            </Flex>
            {/* Mobile Scroll Hint (Optional, can be added if we strictly want scroll on mobile) */}
            <style>{`
                @media (max-width: 576px) {
                    .ant-flex {
                        flex-wrap: nowrap !important;
                        overflow-x: auto;
                        justify-content: flex-start !important;
                        padding-bottom: 8px; /* space for scrollbar */
                        -webkit-overflow-scrolling: touch;
                        scrollbar-width: none; /* Firefox */
                    }
                    .ant-flex::-webkit-scrollbar {
                        display: none; /* Chrome/Safari */
                    }
                }
            `}</style>
          </div>

          <div style={{ marginTop: 72 }}>
            <Row gutter={[24, 24]}>
              {features.map((feature, index) => (
                <Col xs={24} md={8} key={index}>
                  <Card hoverable style={{
                    height: '100%',
                    borderRadius: 16,
                    transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
                    border: `1px solid ${isDarkMode ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.04)'}`,
                  }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-4px)';
                      e.currentTarget.style.boxShadow = '0 12px 40px rgba(72,60,48,0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  >
                    <div style={{ textAlign: 'center', padding: 24 }}>
                      <div style={{ marginBottom: 20, transform: 'scale(1.15)' }}>{feature.icon}</div>
                      <Title level={4} style={{ marginBottom: 12, fontWeight: 600 }}>{feature.title}</Title>
                      <Paragraph type="secondary" style={{ marginBottom: 0 }}>
                        {feature.desc}
                      </Paragraph>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </div>

        </Flex>
      </div>
      <ImageSearchModal
        open={isImageSearchOpen}
        onCancel={() => setIsImageSearchOpen(false)}
        topK={topK}
      />
    </div>
  );
};
