import type { Game } from '../types/game';

export const fetchGames = async (query: string = '', limit: number = 20, offset: number = 0) => {
    const response = await fetch('/data.json');
    const allGames: Game[] = await response.json();
    
    // Client-side filter for now
    const filtered = allGames.filter(g => g.title.toLowerCase().includes(query.toLowerCase()));
    return { data: filtered.slice(offset, offset + limit) };
};

export const fetchReviews = async (slug: string) => {
    return { data: [] }; // Mock for static
};
