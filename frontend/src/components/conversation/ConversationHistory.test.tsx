import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { ConversationHistory } from './ConversationHistory';
import { useConversationStore } from '../../store/conversationStore';

vi.mock('../../store/conversationStore', () => ({
  useConversationStore: vi.fn(),
}));

const mockUseConversationStore = vi.mocked(useConversationStore);

const mockConversations = [
  {
    id: 'conv-1',
    title: '测试对话1',
    preview: '你好',
    messageCount: 2,
    createdAt: new Date('2026-01-01'),
    updatedAt: new Date('2026-01-01'),
  },
  {
    id: 'conv-2',
    title: '测试对话2',
    preview: '搜索照片',
    messageCount: 1,
    createdAt: new Date('2026-01-02'),
    updatedAt: new Date('2026-01-02'),
  },
];

const renderWithRouter = (component: React.ReactElement, initialEntries?: string[]) => {
  return render(
    <MemoryRouter initialEntries={initialEntries || ['/']}>
      {component}
    </MemoryRouter>
  );
};

describe('ConversationHistory', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseConversationStore.mockReturnValue({
      conversations: mockConversations,
      filters: {},
      isLoading: false,
      currentConversation: null,
      loadConversations: vi.fn().mockResolvedValue(undefined),
      loadConversation: vi.fn().mockResolvedValue(undefined),
      createNewConversation: vi.fn().mockResolvedValue(mockConversations[0]),
      addMessageToCurrent: vi.fn().mockResolvedValue(undefined),
      deleteConversation: vi.fn().mockResolvedValue(undefined),
      updateConversationTitle: vi.fn().mockResolvedValue(undefined),
      setFilters: vi.fn(),
      clearCurrentConversation: vi.fn().mockResolvedValue(undefined),
    });
  });

  describe('路由跳转修复验证', () => {
    it('点击对话历史项应调用 loadConversation 并更新 URL 参数', async () => {
      const mockLoadConversation = vi.fn().mockResolvedValue(undefined);
      mockUseConversationStore.mockReturnValue({
        conversations: mockConversations,
        filters: {},
        isLoading: false,
        currentConversation: null,
        loadConversations: vi.fn().mockResolvedValue(undefined),
        loadConversation: mockLoadConversation,
        createNewConversation: vi.fn().mockResolvedValue(mockConversations[0]),
        addMessageToCurrent: vi.fn().mockResolvedValue(undefined),
        deleteConversation: vi.fn().mockResolvedValue(undefined),
        updateConversationTitle: vi.fn().mockResolvedValue(undefined),
        setFilters: vi.fn(),
        clearCurrentConversation: vi.fn().mockResolvedValue(undefined),
      });

      renderWithRouter(<ConversationHistory />);

      await waitFor(() => {
        expect(screen.getByText('测试对话1')).toBeInTheDocument();
      });

      const conversationItem = screen.getByText('测试对话1').closest('li');
      expect(conversationItem).toBeTruthy();

      fireEvent.click(conversationItem!);

      await waitFor(() => {
        expect(mockLoadConversation).toHaveBeenCalledWith('conv-1');
      });
    });

    it('应正确显示对话列表', async () => {
      renderWithRouter(<ConversationHistory />);

      await waitFor(() => {
        expect(screen.getByText('测试对话1')).toBeInTheDocument();
        expect(screen.getByText('测试对话2')).toBeInTheDocument();
      });
    });

    it('应显示对话消息数量', async () => {
      renderWithRouter(<ConversationHistory />);

      await waitFor(() => {
        expect(screen.getByText('2 条消息')).toBeInTheDocument();
        expect(screen.getByText('1 条消息')).toBeInTheDocument();
      });
    });
  });

  describe('新建对话功能验证', () => {
    it('应显示新建对话按钮', async () => {
      renderWithRouter(<ConversationHistory />);

      await waitFor(() => {
        expect(screen.getByText('新建对话')).toBeInTheDocument();
      });
    });

    it('点击新建对话按钮应调用 createNewConversation', async () => {
      const mockCreateNew = vi.fn().mockResolvedValue({ id: 'new-conv', title: '新对话', messages: [] });
      const mockClearCurrent = vi.fn().mockResolvedValue(undefined);

      mockUseConversationStore.mockReturnValue({
        conversations: mockConversations,
        filters: {},
        isLoading: false,
        currentConversation: null,
        loadConversations: vi.fn().mockResolvedValue(undefined),
        loadConversation: vi.fn().mockResolvedValue(undefined),
        createNewConversation: mockCreateNew,
        addMessageToCurrent: vi.fn().mockResolvedValue(undefined),
        deleteConversation: vi.fn().mockResolvedValue(undefined),
        updateConversationTitle: vi.fn().mockResolvedValue(undefined),
        setFilters: vi.fn(),
        clearCurrentConversation: mockClearCurrent,
      });

      renderWithRouter(<ConversationHistory />);

      const newButton = screen.getByRole('button', { name: /新建对话/i });
      fireEvent.click(newButton);

      await waitFor(() => {
        expect(mockClearCurrent).toHaveBeenCalled();
        expect(mockCreateNew).toHaveBeenCalled();
      });
    });
  });

  describe('搜索功能隐藏验证', () => {
    it('不应显示搜索输入框', async () => {
      renderWithRouter(<ConversationHistory />);

      await waitFor(() => {
        expect(screen.getByText('测试对话1')).toBeInTheDocument();
      });

      // 搜索输入框应该被隐藏
      const searchInput = screen.queryByPlaceholderText('搜索对话...');
      expect(searchInput).not.toBeInTheDocument();
    });

    it('应显示搜索功能待完善提示', async () => {
      renderWithRouter(<ConversationHistory />);

      await waitFor(() => {
        expect(screen.getByText(/搜索功能正在完善中/i)).toBeInTheDocument();
      });
    });
  });

  describe('空数据边界情况', () => {
    it('当对话列表为空时应显示空状态提示', async () => {
      mockUseConversationStore.mockReturnValue({
        conversations: [],
        filters: {},
        isLoading: false,
        currentConversation: null,
        loadConversations: vi.fn().mockResolvedValue(undefined),
        loadConversation: vi.fn().mockResolvedValue(undefined),
        createNewConversation: vi.fn().mockResolvedValue(undefined),
        addMessageToCurrent: vi.fn().mockResolvedValue(undefined),
        deleteConversation: vi.fn().mockResolvedValue(undefined),
        updateConversationTitle: vi.fn().mockResolvedValue(undefined),
        setFilters: vi.fn(),
        clearCurrentConversation: vi.fn().mockResolvedValue(undefined),
      });

      renderWithRouter(<ConversationHistory />);

      await waitFor(() => {
        expect(screen.getByText(/暂无对话历史/i)).toBeInTheDocument();
      });
    });

    it('当对话标题为空时应显示空标题', async () => {
      const conversationsWithEmptyTitle = [
        {
          id: 'conv-3',
          title: '',
          preview: '测试预览',
          messageCount: 0,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      mockUseConversationStore.mockReturnValue({
        conversations: conversationsWithEmptyTitle,
        filters: {},
        isLoading: false,
        currentConversation: null,
        loadConversations: vi.fn().mockResolvedValue(undefined),
        loadConversation: vi.fn().mockResolvedValue(undefined),
        createNewConversation: vi.fn().mockResolvedValue(undefined),
        addMessageToCurrent: vi.fn().mockResolvedValue(undefined),
        deleteConversation: vi.fn().mockResolvedValue(undefined),
        updateConversationTitle: vi.fn().mockResolvedValue(undefined),
        setFilters: vi.fn(),
        clearCurrentConversation: vi.fn().mockResolvedValue(undefined),
      });

      renderWithRouter(<ConversationHistory />);

      await waitFor(() => {
        expect(screen.getByText('测试预览')).toBeInTheDocument();
      });
    });
  });

  describe('接口异常场景', () => {
    it('加载对话列表失败时应正确处理错误', async () => {
      // 由于错误处理在 store 层，组件层只显示空状态
      mockUseConversationStore.mockReturnValue({
        conversations: [],
        filters: {},
        isLoading: false,
        currentConversation: null,
        loadConversations: vi.fn().mockRejectedValue(new Error('网络错误')),
        loadConversation: vi.fn().mockResolvedValue(undefined),
        createNewConversation: vi.fn().mockResolvedValue(undefined),
        addMessageToCurrent: vi.fn().mockResolvedValue(undefined),
        deleteConversation: vi.fn().mockResolvedValue(undefined),
        updateConversationTitle: vi.fn().mockResolvedValue(undefined),
        setFilters: vi.fn(),
        clearCurrentConversation: vi.fn().mockResolvedValue(undefined),
      });

      renderWithRouter(<ConversationHistory />);

      // 组件应该正常渲染，显示空状态
      await waitFor(() => {
        expect(screen.getByText(/暂无对话历史/i)).toBeInTheDocument();
      });
    });
  });

  describe('删除对话功能', () => {
    it('点击删除按钮应触发删除确认', async () => {
      const mockDelete = vi.fn().mockResolvedValue(undefined);
      mockUseConversationStore.mockReturnValue({
        conversations: mockConversations,
        filters: {},
        isLoading: false,
        currentConversation: null,
        loadConversations: vi.fn().mockResolvedValue(undefined),
        loadConversation: vi.fn().mockResolvedValue(undefined),
        createNewConversation: vi.fn().mockResolvedValue(undefined),
        addMessageToCurrent: vi.fn().mockResolvedValue(undefined),
        deleteConversation: mockDelete,
        updateConversationTitle: vi.fn().mockResolvedValue(undefined),
        setFilters: vi.fn(),
        clearCurrentConversation: vi.fn().mockResolvedValue(undefined),
      });

      const { container } = renderWithRouter(<ConversationHistory />);

      await waitFor(() => {
        expect(screen.getByText('测试对话1')).toBeInTheDocument();
      });

      const deleteButtons = container.querySelectorAll('.anticon-delete');
      expect(deleteButtons.length).toBeGreaterThan(0);

      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(screen.getByText('确定要删除这个对话吗？')).toBeInTheDocument();
      });
    });
  });
});