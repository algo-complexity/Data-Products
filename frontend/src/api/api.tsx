import axios from "axios";
import {
  Citation,
  GraphData,
  PaginatedList,
  Researcher,
  ResearcherStub,
  ResearcherWebsites,
} from "./types";
import useSWR from "swr";

export const fetcher = (url: string) => axios.get(url).then((res) => res.data);
export const pagedfetcher = (url: string) =>
  axios.get(url).then((res) => res.data.items);

export function searchResearcher(searchText: string) {
  return axios
    .get<PaginatedList<ResearcherStub>>(
      `/api/researcher/search?q=${searchText}`,
    )
    .then((res) => {
      return res.data.items;
    });
}

export function useResearcher(searchText: string) {
  const { data, error } = useSWR<Researcher>(
    `/api/researcher/${searchText}`,
    fetcher,
  );
  return {
    researcher: data,
    loading: !error && !data,
    error: error,
  };
}

export function useResearcherCitations(searchText: string) {
  const { data, error } = useSWR<Citation[]>(
    `/api/researcher/${searchText}/citations`,
    fetcher,
  );
  return {
    citations: data,
    loading: !error && !data,
    error: error,
  };
}

export function useResearcherWebsites(searchText: string) {
  const { data, error } = useSWR<PaginatedList<ResearcherWebsites>>(
    `/api/researcher/${searchText}/websites`,
    fetcher,
  );
  return {
    websites: data,
    loading: !error && !data,
    error: error,
  };
}

export function useSCSEGraph() {
  const { data, error } = useSWR<GraphData>(`/api/scse/graph`, fetcher);
  return {
    graph: data,
    loading: !error && !data,
    error: error,
  };
}
