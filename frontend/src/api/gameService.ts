import { apiClient } from './client';
import type { Game } from '../types/game';

const fetchStaticGames = async (query: string = '', limit: number = 20, offset: number = 0) => {
  try {
    const response = await fetch('/data.json');
    if (!response.ok) throw new Error('Failed to fetch data.json');
    const allGames: Game[] = await response.json();
    const q = query.toLowerCase();
    const filtered = allGames.filter(g => {
      const titleMatch = g.title?.toLowerCase().includes(q) || false;
      const titleJaMatch = g.title_ja?.toLowerCase().includes(q) || false;
      return titleMatch || titleJaMatch;
    });
    return { data: filtered.slice(offset, offset + limit) };
  } catch (error) {
    console.error('Static fallback failed:', error);
    return { data: [] };
  }
};

export const fetchGames = async (query: string = '', limit: number = 20, offset: number = 0) => {
  try {
    const response = await apiClient.get<{ data: Game[] }>('/games/search', {
      params: { q: query, limit, offset }
    });
    return response.data;
  } catch (error) {
    console.warn('Backend API request failed, falling back to static data.json...', error);
    return await fetchStaticGames(query, limit, offset);
  }
};

export const fetchReviews = async (slug: string) => {
  try {
    const res = await apiClient.get<{ data: { rating: number, comment: string }[] }>('/games/' + slug + '/review', {
      params: { user_id: 'anonymous_user' }
    });
    return res.data;
  } catch (error) {
    console.warn('Backend API review fetch failed, returning empty mock list');
    return { data: [] };
  }
};

export const postReview = async (slug: string, rating: number, comment: string) => {
  try {
    return (await apiClient.post('/games/' + slug + '/review', { user_id: 'anonymous_user', rating, comment })).data;
  } catch (error) {
    console.warn('Backend API review post failed, returning mock success');
    return { status: 'success', message: 'Mocked review post' };
  }
};

