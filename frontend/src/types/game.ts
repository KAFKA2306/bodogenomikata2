export interface Game {
  id: number;
  slug: string;
  title: string;
  title_ja?: string | null;
  description: string;
  image_url?: string | null;
  published_year: number;
  min_players: number;
  max_players: number;
  play_time: number;
  min_age: number;
  structured_data?: {
    mechanics?: string[];
  };
}
