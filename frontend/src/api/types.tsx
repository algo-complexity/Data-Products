export type Stock = {
  name: string;
  ticker: string;
  summary: string;
  image_url: string | null;
};

export type StockStub = {
  name: string;
  ticker: string;
};

export type Tweet = {
  content: string;
  timestamp: Date;
  author: number;
  url: string;
  sentiment: "positive" | "negative" | "neutral" | null;
  retweets: number;
  replies: number;
  likes: number;
  quotes: number;
  pub_score: number;
  hashtags: string[];
};

export type News = {
  headline: string;
  url: string;
  timestamp: Date;
  sentiment: "positive" | "negative" | "neutral" | null;
  source: string;
};

export type Price = {
  open: number;
  high: number;
  low: number;
  close: number;
  timestamp: Date;
};

export type CandlestickData<T> = {
  label: string;
  color: {
    up: string;
    down: string;
    unchanged: string;
  };
  data: T[];
};

export type PiechartData<T> = {
  label: string;
  backgroundColor: string[];
  data: T[];
};

export type ChartData<TData, TLabel = undefined> = {
  labels?: TLabel;
  datasets: TData[];
};

export type Reddit = {
  title: string;
  content: string;
  timestamp: Date;
  author: string;
  sentiment: "positive" | "negative" | "neutral" | null;
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

export type PieValue = {
  key: string;
  value: number;
};
