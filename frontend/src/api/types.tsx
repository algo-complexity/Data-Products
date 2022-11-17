import { ScriptableContext } from "chart.js";

export type Stock = {
  name: string;
  ticker: string;
  summary: string;
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

export type Price = {
  open: number;
  high: number;
  low: number;
  close: number;
  timestamp: Date;
};

export type Indicator = {
  name:
    | "sma_50"
    | "sma_100"
    | "sma_200"
    | "ema_50"
    | "ema_100"
    | "ema_200"
    | "macd"
    | "rsi"
    | "atr";
  value: number;
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

export type CategoricalMatrixDataPoint = {
  x: string;
  y: string;
  v: number;
};

export type MatrixData<T> = {
  label: string;
  data: T[];
  backgroundColor: string | ((context: ScriptableContext<"matrix">) => string);
  borderColor: string | ((context: ScriptableContext<"matrix">) => string);
  width: number | ((context: ScriptableContext<"matrix">) => number);
  height: number | ((context: ScriptableContext<"matrix">) => number);
  borderWidth: number | ((context: ScriptableContext<"matrix">) => number);
};

export type ChartData<T> = {
  datasets: T[];
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
