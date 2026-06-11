import { apiClient } from './client';
import { Game } from '../types/game';

export const fetchGames = async (query: string = '', limit: number = 20, offset: number = 0) => {
  const response = await apiClient.get<{ data: Game[] }>('/games/search', {
    params: { q: query, limit, offset }
  });
  return response.data;
};
export const postReview = async (slug: string, rating: number, comment: string) => {
  return await apiClient.post(`/games/${slug}/review`, { rating, comment });
};
