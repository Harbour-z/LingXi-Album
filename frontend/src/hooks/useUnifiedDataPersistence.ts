import { useEffect } from 'react';
import { useUnifiedStore } from '../store/unifiedStore';

const STORAGE_KEYS = {
  SEARCH_QUERY: 'smart_album_search_query',
  TOP_K: 'smart_album_top_k',
  SEARCH_RESULTS: 'smart_album_search_results',
  LAST_SEARCH_QUERY: 'smart_album_last_search_query',
};

export const useUnifiedDataPersistence = () => {
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

  useEffect(() => {
    const savedSearchQuery = localStorage.getItem(STORAGE_KEYS.SEARCH_QUERY);
    if (savedSearchQuery) {
      setSearchQuery(savedSearchQuery);
    }

    const savedTopK = localStorage.getItem(STORAGE_KEYS.TOP_K);
    if (savedTopK) {
      setTopK(parseInt(savedTopK, 10));
    }

    const savedLastSearchQuery = localStorage.getItem(STORAGE_KEYS.LAST_SEARCH_QUERY);
    if (savedLastSearchQuery) {
      setLastSearchQuery(savedLastSearchQuery);
    }

    const savedSearchResults = localStorage.getItem(STORAGE_KEYS.SEARCH_RESULTS);
    if (savedSearchResults) {
      try {
        setSearchResults(JSON.parse(savedSearchResults));
      } catch (error) {
        console.error('Failed to parse saved search results:', error);
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.SEARCH_QUERY, searchQuery);
  }, [searchQuery]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.TOP_K, topK.toString());
  }, [topK]);

  useEffect(() => {
    if (searchResults) {
      localStorage.setItem(STORAGE_KEYS.SEARCH_RESULTS, JSON.stringify(searchResults));
    } else {
      localStorage.removeItem(STORAGE_KEYS.SEARCH_RESULTS);
    }
  }, [searchResults]);

  useEffect(() => {
    if (lastSearchQuery) {
      localStorage.setItem(STORAGE_KEYS.LAST_SEARCH_QUERY, lastSearchQuery);
    } else {
      localStorage.removeItem(STORAGE_KEYS.LAST_SEARCH_QUERY);
    }
  }, [lastSearchQuery]);

  return {
    clearPersistedData: () => {
      Object.values(STORAGE_KEYS).forEach(key => {
        localStorage.removeItem(key);
      });
    },
  };
};
