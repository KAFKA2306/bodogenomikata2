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

export const fetchGameBySlug = async (slug: string): Promise<{ data: Game }> => {
  try {
    const response = await apiClient.get<{ data: Game }>(`/games/${slug}`);
    // Extract Axios response data structure containing the game object inside 'data' property
    return response.data;
  } catch (error) {
    console.warn(`Backend API fetch for slug "${slug}" failed, falling back to static data.json...`, error);
    const response = await fetch('/data.json');
    if (!response.ok) throw new Error('Failed to fetch data.json');
    const allGames: Game[] = await response.json();
    const game = allGames.find(g => g.slug === slug);
    if (!game) throw new Error(`Game with slug "${slug}" not found in static data`);
    return { data: game };
  }
};

export const fetchReviews = async (slug: string) => {
  try {
    const res = await apiClient.get<{ data: { rating: number, comment: string }[] }>('/games/' + slug + '/review', {
      params: { user_id: 'anonymous_user' }
    });
    return res.data;
  } catch (error) {
    console.warn('Backend API review fetch failed, falling back to localStorage');
    try {
      const localReviewsStr = localStorage.getItem(`reviews_${slug}`);
      const localReviews = localReviewsStr ? JSON.parse(localReviewsStr) : [];
      return { data: localReviews };
    } catch (e) {
      console.error('Failed to read reviews from localStorage:', e);
      return { data: [] };
    }
  }
};

export const postReview = async (slug: string, rating: number, comment: string) => {
  const newReview = { rating, comment, created_at: new Date().toISOString() };
  try {
    return (await apiClient.post('/games/' + slug + '/review', { user_id: 'anonymous_user', rating, comment })).data;
  } catch (error) {
    console.warn('Backend API review post failed, falling back to localStorage');
    try {
      const localReviewsStr = localStorage.getItem(`reviews_${slug}`);
      const localReviews = localReviewsStr ? JSON.parse(localReviewsStr) : [];
      localReviews.unshift(newReview);
      localStorage.setItem(`reviews_${slug}`, JSON.stringify(localReviews));
      return { status: 'success', message: 'Saved to localStorage' };
    } catch (e) {
      console.error('Failed to save review to localStorage:', e);
      return { status: 'error', message: 'Failed to save locally' };
    }
  }
};

