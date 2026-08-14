import { apiClient } from './client';
import { findCuratedGameBySlug, mergeCuratedGames } from '../data/curatedGames';
import { flipSevenWithAVengeance } from '../data/flipSevenWithAVengeance';
import type { Game } from '../types/game';

const additionalCuratedGames: Game[] = [flipSevenWithAVengeance];

const findAdditionalCuratedGameBySlug = (slug: string) =>
  additionalCuratedGames.find(game => game.slug === slug);

const mergeAdditionalCuratedGames = (games: Game[], query: string, limit: number, offset: number) => {
  if (offset !== 0) return games;

  const normalizedQuery = query.normalize('NFKC').toLocaleLowerCase('ja').trim();
  const matches = additionalCuratedGames.filter(game => {
    if (!normalizedQuery) return true;
    return game.title.toLocaleLowerCase('ja').includes(normalizedQuery)
      || game.title_ja?.toLocaleLowerCase('ja').includes(normalizedQuery);
  });
  const existingSlugs = new Set(games.map(game => game.slug));
  return [
    ...matches.filter(game => !existingSlugs.has(game.slug)),
    ...games,
  ].slice(0, limit);
};

const mergeAllCuratedGames = (games: Game[], query: string, limit: number, offset: number) =>
  mergeAdditionalCuratedGames(
    mergeCuratedGames(games, query, limit, offset),
    query,
    limit,
    offset,
  );

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
    const paged = filtered.slice(offset, offset + limit);
    return { data: mergeAllCuratedGames(paged, query, limit, offset) };
  } catch (error) {
    console.error('Static fallback failed:', error);
    return { data: mergeAllCuratedGames([], query, limit, offset) };
  }
};

export const fetchGames = async (query: string = '', limit: number = 20, offset: number = 0) => {
  try {
    const response = await apiClient.get<{ data: Game[] }>('/games/search', {
      params: { q: query, limit, offset }
    });
    return { data: mergeAllCuratedGames(response.data.data, query, limit, offset) };
  } catch (error) {
    console.warn('Backend API request failed, falling back to static data.json...', error);
    return await fetchStaticGames(query, limit, offset);
  }
};

export const fetchGameBySlug = async (slug: string): Promise<{ data: Game }> => {
  const additionalCuratedGame = findAdditionalCuratedGameBySlug(slug);
  if (additionalCuratedGame) return { data: additionalCuratedGame };

  const curatedGame = findCuratedGameBySlug(slug);
  if (curatedGame) return { data: curatedGame };

  try {
    const response = await apiClient.get<{ data: Game }>(`/games/${slug}`);
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
