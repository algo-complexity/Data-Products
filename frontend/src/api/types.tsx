export type Researcher = {
  name: string;
  email: string | null;
  citations: number | null;
  scholar_id: string;
  faculty: string | null;
  interests: string[];
  co_authors: string[];
  publications: string[];
};

export type ResearcherStub = {
  name: string;
  email: string | null;
  citations: number | null;
  scholar_id: string;
  faculty: string | null;
  interests: string[];
  co_authors: string[];
  publications: string[];
};

export type Citation = {
  year: Date;
  count: number;
};

export type PaginatedList<T> = {
  items: T[];
  limit: number;
  total: number;
  page: number;
  pages: number;
};

export type BarChartData = {
  labels: any[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string;
  }[];
};

export type ResearcherWebsites = {
  url: string;
  type: "dr_ntu" | "dblp" | "linkedin" | "image" | "other";
};

export type Publication = {
  title: string;
  abstract: string;
  num_citations: number;
  year: Date | null;
  paper_url: string | null;
  conference: string | null;
};

export type InterestNode = {
  id: string;
  name: string;
  type: "interest";
};

export type ProfNode = {
  id: string;
  name: string;
  type: "prof";
  data: Researcher;
};

export type Node = InterestNode | ProfNode;

export type Link = {
  source: string;
  target: string;
};

export type GraphData = {
  nodes: Node[];
  links: Link[];
};
