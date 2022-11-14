import React, { useEffect, useState } from "react";
import {
  Layout,
  Space,
  AutoComplete,
  List,
  Divider,
  Skeleton,
  Card,
} from "antd";
import "antd/dist/antd.css";
import { fetcher, searchStock, useStock } from "./api/api";
import { PaginatedList, Stock, Tweet, News, Reddit } from "./api/types";
// import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { useDebouncedCallback } from "use-debounce";
import InfiniteScroll from "react-infinite-scroll-component";
import useSWRInfinite from "swr/infinite";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
);

const { Content, Footer } = Layout;

// const Citations = ({ researcher }: { researcher: Researcher }) => {
//   const { citations } = useResearcherCitations(researcher.name);
//   const [data, setData] = useState<BarChartData>({
//     labels: [1, 2, 3, 4],
//     datasets: [],
//   });

//   useEffect(() => {
//     if (citations) {
//       setData({
//         labels: citations.map((citation) =>
//           new Date(citation.year).getFullYear(),
//         ),
//         datasets: [
//           {
//             label: researcher.name,
//             data: citations.map((citation) => citation.count),
//             backgroundColor: "rgba(255, 99, 132, 0.5)",
//           },
//         ],
//       });
//     }
//   }, [citations, researcher.name]);

//   const options = {
//     responsive: true,
//     plugins: {
//       legend: {
//         position: "top" as const,
//       },
//       title: {
//         display: true,
//         text: "Number of Citations",
//       },
//     },
//   };

//   return <Bar options={options} data={data} width={600} height={500} />;
// };

const Tweets = ({ stock }: { stock: Stock }) => {
  const getKey = (
    pageIndex: number,
    previousPageData: PaginatedList<Tweet>,
  ) => {
    if (previousPageData && !previousPageData.items.length) return null;
    return `/api/stock/${stock.name}/tweets?page=${pageIndex + 1}`;
  };

  const { data, size, setSize } = useSWRInfinite<PaginatedList<Tweet>>(
    getKey,
    fetcher,
    { initialSize: 1 },
  );

  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [maxData, setMaxData] = useState(0);

  useEffect(() => {
    if (data) {
      setTweets(data.map((paged) => paged.items).flat());
      setMaxData(data[0].total);
    }
  }, [data]);

  return (
    <>
      <h3>Tweets</h3>
      <div
        id="scrollableDiv"
        style={{
          height: 400,
          overflow: "auto",
          padding: "0 16px",
          border: "1px solid rgba(140, 140, 140, 0.35)",
        }}
      >
        {data && tweets ? (
          <InfiniteScroll
            dataLength={tweets.length}
            next={() => setSize(size + 1)}
            hasMore={tweets.length < maxData}
            loader={<Skeleton avatar paragraph={{ rows: 1 }} active />}
            endMessage={<Divider plain>End</Divider>}
            scrollableTarget="scrollableDiv"
          >
            <List
              dataSource={tweets}
              renderItem={(item) => (
                <List.Item key={item.author}>
                  <List.Item.Meta
                    title={<a href={item.url}>{item.author}</a>}
                    description={item.content}
                  />
                  <div>hashtags: {item.hashtags}</div>
                </List.Item>
              )}
            />
          </InfiniteScroll>
        ) : (
          ""
        )}
      </div>
    </>
  );
};

const RedditComponent = ({ stock }: { stock: Stock }) => {
  const getKey = (
    pageIndex: number,
    previousPageData: PaginatedList<Reddit>,
  ) => {
    if (previousPageData && !previousPageData.items.length) return null;
    return `/api/stock/${stock.name}/reddit?page=${pageIndex + 1}`;
  };

  const { data, size, setSize } = useSWRInfinite<PaginatedList<Reddit>>(
    getKey,
    fetcher,
    { initialSize: 1 },
  );

  const [reddit, setReddit] = useState<Reddit[]>([]);
  const [maxData, setMaxData] = useState(0);

  useEffect(() => {
    if (data) {
      setReddit(data.map((paged) => paged.items).flat());
      setMaxData(data[0].total);
    }
  }, [data]);

  return (
    <>
      <h3>Reddit Posts</h3>
      <div
        id="scrollableDiv"
        style={{
          height: 400,
          overflow: "auto",
          padding: "0 16px",
          border: "1px solid rgba(140, 140, 140, 0.35)",
        }}
      >
        {data && reddit ? (
          <InfiniteScroll
            dataLength={reddit.length}
            next={() => setSize(size + 1)}
            hasMore={reddit.length < maxData}
            loader={<Skeleton avatar paragraph={{ rows: 1 }} active />}
            endMessage={<Divider plain>End</Divider>}
            scrollableTarget="scrollableDiv"
          >
            <List
              dataSource={reddit}
              renderItem={(item) => (
                <List.Item key={item.author}>
                  <List.Item.Meta
                    title={<a href={item.url}>{item.author}</a>}
                    description={item.content}
                  />
                  <div>Score: {item.score}</div>
                </List.Item>
              )}
            />
          </InfiniteScroll>
        ) : (
          ""
        )}
      </div>
    </>
  );
};

const NewsComponent = ({ stock }: { stock: Stock }) => {
  const getKey = (pageIndex: number, previousPageData: PaginatedList<News>) => {
    if (previousPageData && !previousPageData.items.length) return null;
    return `/api/stock/${stock.name}/news?page=${pageIndex + 1}`;
  };

  const { data, size, setSize } = useSWRInfinite<PaginatedList<News>>(
    getKey,
    fetcher,
    { initialSize: 1 },
  );

  const [news, setNews] = useState<News[]>([]);
  const [maxData, setMaxData] = useState(0);

  useEffect(() => {
    if (data) {
      setNews(data.map((paged) => paged.items).flat());
      setMaxData(data[0].total);
    }
  }, [data]);

  return (
    <>
      <h3>news</h3>
      <div
        id="scrollableDiv"
        style={{
          height: 400,
          overflow: "auto",
          padding: "0 16px",
          border: "1px solid rgba(140, 140, 140, 0.35)",
        }}
      >
        {data && news ? (
          <InfiniteScroll
            dataLength={news.length}
            next={() => setSize(size + 1)}
            hasMore={news.length < maxData}
            loader={<Skeleton avatar paragraph={{ rows: 1 }} active />}
            endMessage={<Divider plain>End</Divider>}
            scrollableTarget="scrollableDiv"
          >
            <List
              dataSource={news}
              renderItem={(item) => (
                <List.Item key={item.headline}>
                  <List.Item.Meta
                    title={<a href={item.url}>{item.headline}</a>}
                    description={item.content}
                  />
                  <div>sentiment: {item.sentiment}</div>
                </List.Item>
              )}
            />
          </InfiniteScroll>
        ) : (
          ""
        )}
      </div>
    </>
  );
};

const Profile = ({ stock }: { stock: Stock }) => {
  return <Card title={stock.name} size={"small"}></Card>;
};

const Dashboard = ({ ticker }: { ticker: string }) => {
  const { stock } = useStock(ticker);

  if (!stock) {
    return <div>Please Select a Stock</div>;
  }

  return (
    <Space size={40} direction="vertical">
      <Profile stock={stock} />
      <Tweets stock={stock} />
      <NewsComponent stock={stock} />
      <RedditComponent stock={stock} />
    </Space>
  );
};

const Home: React.FC = () => {
  const [options, setOptions] = useState<{ value: string; label: string }[]>(
    [],
  );
  const [ticker, setTicker] = useState("");
  const debounced = useDebouncedCallback((searchText) => {
    searchStock(searchText).then((stocks) => {
      setOptions(
        stocks.map((stock) => {
          return {
            value: stock.ticker,
            label: `${stock.name} (${stock.ticker})`,
          };
        }),
      );
    });
  }, 1000);

  const onSelect = (data: string) => {
    setTicker(data);
  };

  const onSearch = (searchText: string) => {
    debounced(searchText);
  };

  return (
    <div>
      <h2>Home</h2>
      <Space direction="vertical" size={30}>
        <AutoComplete
          options={options}
          style={{ width: 200 }}
          onSelect={onSelect}
          onSearch={onSearch}
          placeholder="Search stock"
        />
        <Dashboard ticker={ticker} />
      </Space>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Layout className="site-layout">
        <Content style={{ margin: "0 16px" }}>
          <div
            className="site-layout-background"
            style={{ padding: 24, minHeight: 360 }}
          >
            <Home />
          </div>
        </Content>
        <Footer style={{ textAlign: "center" }}>Data Products</Footer>
      </Layout>
    </Layout>
  );
};

export default App;
