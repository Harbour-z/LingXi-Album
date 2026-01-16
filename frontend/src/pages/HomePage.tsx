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
  Tag,
  theme,
  Slider,
  Tooltip,
} from 'antd';
import {
  SearchOutlined,
  PictureOutlined,
  BulbOutlined,
  RocketOutlined,
  CameraOutlined,
} from '@ant-design/icons';
import { TypewriterEffect } from '../components/common/TypewriterEffect';
import { useChatStore } from '../store/chatStore';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { sendMessage } = useChatStore();
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(10);
  const { token } = theme.useToken();
  const [topic, setTopic] = useState('');

  // 预设话题列表
  const topics = [
    '帮我找最新的AI论文',
    '搜索本周科技新闻',
    '寻找雨天的咖啡馆照片',
    '需要一张开心的柯基犬图片',
    '找一下去年夏天的海边合影',
    '搜索红色跑车在赛道上飞驰',
    '帮我找几张极简风格的办公桌图片',
    '寻找秋天落叶铺满街道的场景'
  ];

  // 每次页面加载时随机选择一个话题
  React.useEffect(() => {
    const randomTopic = topics[Math.floor(Math.random() * topics.length)];
    setTopic(randomTopic);
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

  const suggestions = [
    { icon: '🌅', text: '日落时的海滩' },
    { icon: '🐕', text: '可爱的小狗' },
    { icon: '🏔️', text: '山间风景' },
    { icon: '🎂', text: '生日聚会' },
    { icon: '🌸', text: '春天的花朵' },
    { icon: '🌃', text: '城市夜景' },
  ];

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
        minHeight: '80vh',
        padding: '20px'
    }}>
      <div style={{ maxWidth: 800, width: '100%', textAlign: 'center' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          
          <div style={{ marginBottom: 40 }}>
            <Title level={1} style={{ fontSize: '3rem', marginBottom: 16 }}>
                <TypewriterEffect 
                    parts={[
                        { text: '用语言描述，' },
                        { text: '智能搜索', style: { color: token.colorPrimary } }
                    ]}
                    speed={150} 
                    cursorColor={token.colorPrimary} 
                />
            </Title>
            <Paragraph style={{ fontSize: '1.2rem', color: token.colorTextSecondary }}>
              基于深度学习的图像语义理解，让您用自然语言找到任何想要的照片
            </Paragraph>
          </div>

          <Card 
            bordered={false}
            style={{ 
                boxShadow: '0 8px 24px rgba(0,0,0,0.08)', 
                borderRadius: 16,
                overflow: 'hidden'
            }}
            bodyStyle={{ padding: 0 }}
          >
            <div style={{ padding: '24px 24px 12px' }}>
                <TextArea
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="描述您想找的图片，例如：海边的日落、穿红色衣服的人..."
                    autoSize={{ minRows: 2, maxRows: 6 }}
                    variant="borderless"
                    style={{ fontSize: 18, resize: 'none' }}
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
                padding: '12px 24px 24px', 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                borderTop: '1px solid #f0f0f0'
            }}>
                <Space>
                    <Button type="text" icon={<PictureOutlined />} disabled>以图搜图 (开发中)</Button>
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

          <div style={{ marginTop: 32 }}>
            <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>试试这些搜索</Text>
            <Space wrap size={[12, 12]} style={{ justifyContent: 'center' }}>
                {suggestions.map((item, index) => (
                    <Button 
                        key={index} 
                        shape="round" 
                        size="large"
                        onClick={() => {
                            navigate(`/gallery?q=${encodeURIComponent(item.text)}`);
                        }}
                        style={{ height: 'auto', padding: '8px 20px' }}
                    >
                        <span style={{ fontSize: 18, marginRight: 8 }}>{item.icon}</span>
                        {item.text}
                    </Button>
                ))}
            </Space>
          </div>

          <div style={{ marginTop: 60 }}>
            <Row gutter={[24, 24]}>
                {features.map((feature, index) => (
                    <Col xs={24} md={8} key={index}>
                        <Card hoverable style={{ height: '100%', borderRadius: 12 }}>
                            <div style={{ textAlign: 'center', padding: 16 }}>
                                <div style={{ marginBottom: 16 }}>{feature.icon}</div>
                                <Title level={4} style={{ marginBottom: 8 }}>{feature.title}</Title>
                                <Paragraph type="secondary" style={{ marginBottom: 0 }}>
                                    {feature.desc}
                                </Paragraph>
                            </div>
                        </Card>
                    </Col>
                ))}
            </Row>
          </div>

        </Space>
      </div>
    </div>
  );
};
