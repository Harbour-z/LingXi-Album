import { create } from 'zustand';
import type { ImageResult } from '../api/types';

interface UnifiedStore {
  searchQuery: string;
  topK: number;
  searchResults: ImageResult[] | null;
  lastSearchQuery: string | null;

  setSearchQuery: (query: string) => void;
  setTopK: (topK: number) => void;
  setSearchResults: (results: ImageResult[] | null) => void;
  setLastSearchQuery: (query: string | null) => void;
  resetToHome: () => void;
}

export const useUnifiedStore = create<UnifiedStore>((set) => ({
  searchQuery: '',
  topK: 10,
  searchResults: null,
  lastSearchQuery: null,

  setSearchQuery: (query) => set({ searchQuery: query }),

  setTopK: (topK) => set({ topK }),

  setSearchResults: (results) => set({ searchResults: results }),

  setLastSearchQuery: (query) => set({ lastSearchQuery: query }),

  resetToHome: () => {
    set({
      searchQuery: '',
      searchResults: null,
      lastSearchQuery: null,
    });
  },
}));
