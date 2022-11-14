export type Stock = {
  name: string;
  ticker: string;
};

export type StockStub = {
  name: string;
  ticker: string;
};

export type Tweet = {
  content: string;
  timestamp: Date;
  author: string;
  sentiment: string;
  retweets: number;
  comments: number;
  likes: number;
  hashtags: string;
  url: string;
};

export type News = {
  headline: string;
  content: string;
  url: string;
  sentiment: string;
  summary: string;
};

export type Reddit = {
  title: string;
  content: string;
  timestamp: Date;
  author: string;
  sentiment: string;
  score: number;
  num_comments: number;
  url: string;
};

export type PaginatedList<T> = {
  items: T[];
  limit: number;
  total: number;
  page: number;
  pages: number;
};
