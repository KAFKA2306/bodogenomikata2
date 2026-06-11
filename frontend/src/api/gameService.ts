import { apiClient } from './client';
import type { Game } from '../types/game';

export const fetchGames = async (query: string = '', limit: number = 20, offset: number = 0) => {
  try {
    const response = await apiClient.get<{ data: Game[] }>('/games/search', {
      params: { q: query, limit, offset }
    });
    return response.data;
  } catch (error) {
    console.error('API Fetch Error:', error);
    throw error;
  }
};
