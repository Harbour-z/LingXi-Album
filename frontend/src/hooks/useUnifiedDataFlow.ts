import { useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useUnifiedStore } from '../store/unifiedStore';
import { useChatStore } from '../store/chatStore';
import type { ImageResult } from '../api/types';

export const useUnifiedDataFlow = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const {
    searchQuery,
    topK,
    searchResults,
    lastSearchQuery,
    setSearchQuery,
    setTopK,
    setSearchResults,
    setLastSearchQuery,
  } = useUnifiedStore();

  const { sendMessage } = useChatStore();

  const transitionToChatFromSearch = useCallback((query?: string) => {
    const queryToUse = query || searchQuery || lastSearchQuery || '';
    if (queryToUse) {
      setSearchQuery(queryToUse);
      setLastSearchQuery(queryToUse);
      setSearchParams({ mode: 'chat' });
      return queryToUse;
    }
    return null;
  }, [searchQuery, lastSearchQuery, setSearchQuery, setLastSearchQuery, setSearchParams]);

  const transitionToSearchFromHome = useCallback((query: string, topKValue?: number) => {
    setSearchQuery(query);
    if (topKValue) {
      setTopK(topKValue);
    }
    setSearchParams({ mode: 'search' });
    return query;
  }, [setSearchQuery, setTopK, setSearchParams]);

  const transitionToHome = useCallback(() => {
    setSearchParams({});
  }, [setSearchParams]);

  const handleImageClick = useCallback((image: ImageResult) => {
    const imageId = image.id;
    const description = image.metadata.description || '';
    const tags = image.metadata.tags || [];
    
    const queryParts = [];
    if (description) {
      queryParts.push(description);
    }
    if (tags.length > 0) {
      queryParts.push(tags.slice(0, 3).join('、'));
    }
    
    const query = queryParts.length > 0 ? queryParts.join('，') : `查看图片 ${imageId}`;
    transitionToChatFromSearch(query);
  }, [transitionToChatFromSearch]);

  const handleSearchWithAgent = useCallback(async (query: string) => {
    const searchQueryLower = query.toLowerCase();
    const shouldUseAgent = searchQueryLower.includes('帮我') || 
                           searchQueryLower.includes('找') || 
                           searchQueryLower.includes('搜索') ||
                           searchQueryLower.includes('查') ||
                           searchQueryLower.includes('找找');
    
    if (shouldUseAgent) {
      transitionToChatFromSearch(query);
      try {
        await sendMessage(query);
      } catch (error) {
        console.error('Failed to send message to agent:', error);
      }
      return true;
    }
    
    return false;
  }, [transitionToChatFromSearch, sendMessage]);

  const getSearchContext = useCallback(() => {
    return {
      query: searchQuery || lastSearchQuery || '',
      topK,
      hasResults: searchResults !== null && searchResults.length > 0,
      resultCount: searchResults?.length || 0,
    };
  }, [searchQuery, lastSearchQuery, topK, searchResults]);

  return {
    transitionToChatFromSearch,
    transitionToSearchFromHome,
    transitionToHome,
    handleImageClick,
    handleSearchWithAgent,
    getSearchContext,
  };
};
