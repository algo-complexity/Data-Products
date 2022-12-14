import axios from "axios";
import {
  PaginatedList,
  Indicator,
  PieValue,
  Price,
  Stock,
  StockStub,
} from "./types";
import useSWR from "swr";

export const fetcher = (url: string) => axios.get(url).then((res) => res.data);
export const pagedfetcher = (url: string) =>
  axios.get(url).then((res) => res.data.items);

export function searchStock(searchText: string) {
  return axios
    .get<PaginatedList<StockStub>>(`/api/stock/search?q=${searchText}`)
    .then((res) => {
      return res.data.items;
    });
}

export function useStock(searchText: string) {
  const { data, error } = useSWR<Stock>(`/api/stock/${searchText}`, fetcher);
  return {
    stock: data,
    loading: !error && !data,
    error: error,
  };
}

export function useSentiment(searchText: string, source: string = "tweet") {
  const { data, error } = useSWR<PieValue[]>(
    `/api/stock/${searchText}/sentiment?q=${source}`,
    fetcher,
  );
  return {
    sentiments: data,
    loading: !error && !data,
    error: error,
  };
}

export function useStockPrice(searchText: string) {
  const { data, error } = useSWR<Price[]>(
    `/api/stock/${searchText}/price`,
    fetcher,
  );
  return {
    prices: data,
    loading: !error && !data,
    error: error,
  };
}

export function useStockIndicator(searchText: string) {
  const { data, error } = useSWR<Indicator[]>(
    `/api/stock/${searchText}/indicators`,
    fetcher,
  );
  return {
    indicators: data,
    loading: !error && !data,
    error: error,
  };
}
