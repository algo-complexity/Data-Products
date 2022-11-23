import React, { useEffect, useState } from "react";
import {
  HomeOutlined,
  LikeOutlined,
  DislikeOutlined,
  LineOutlined,
} from "@ant-design/icons";
import {
  Layout,
  Space,
  AutoComplete,
  List,
  Divider,
  Skeleton,
  Card,
  Menu,
  Image,
  Typography,
  Button,
} from "antd";
import "antd/dist/antd.css";
import {
  fetcher,
  searchStock,
  useSentiment,
  useStock,
  useStockIndicator,
  useStockPrice,
} from "./api/api";
import {
  PaginatedList,
  Stock,
  Tweet,
  News,
  Reddit,
  ChartData,
  CandlestickData,
  MatrixData,
  CategoricalMatrixDataPoint,
  PiechartData,
} from "./api/types";
import {
  Chart as ChartJS,
  CategoryScale,
  ArcElement,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeSeriesScale,
  FinancialDataPoint,
  TooltipItem,
  CartesianScaleTypeRegistry,
} from "chart.js";
import { useDebouncedCallback } from "use-debounce";
import InfiniteScroll from "react-infinite-scroll-component";
import useSWRInfinite from "swr/infinite";
import { Candlestick, Matrix } from "./components/typedCharts";
import "chartjs-adapter-date-fns";
import { CandlestickElement } from "chartjs-chart-financial";
import removeMarkdown from "markdown-to-text";
import { Pie } from "react-chartjs-2";
import { MatrixElement } from "chartjs-chart-matrix";

ChartJS.register(
  CategoryScale,
  ArcElement,
  LinearScale,
  TimeSeriesScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  CandlestickElement,
  MatrixElement,
);

const { Paragraph } = Typography;
const { Content, Footer, Sider } = Layout;

const Indicators = ({ stock }: { stock: Stock }) => {
  const { indicators } = useStockIndicator(stock.ticker);
  const [data, setData] = useState<
    ChartData<MatrixData<CategoricalMatrixDataPoint>>
  >({
    datasets: [
      {
        label: stock.name,
        data: [
          {
            x: "sma",
            y: "indicator",
            v: "positive",
          },
          {
            x: "ema",
            y: "indicator",
            v: "positive",
          },
          {
            x: "rsi",
            y: "indicator",
            v: "positive",
          },
          {
            x: "macd",
            y: "indicator",
            v: "positive",
          },
        ],
        backgroundColor: "#000000",
        borderColor: "#000000",
        width: 5,
        height: 5,
        borderWidth: 5,
      },
    ],
  });

  useEffect(() => {
    if (indicators) {
      setData({
        datasets: [
          {
            label: stock.name,
            backgroundColor: (context) =>
              (context.raw as CategoricalMatrixDataPoint).v === "positive"
                ? "rgb(102, 189, 99)"
                : (context.raw as CategoricalMatrixDataPoint).v === "negative"
                ? "rgb(215, 38, 39)"
                : "rgb(255, 255, 191)",
            borderColor: "#000000",
            width: ({ chart, dataset }) =>
              chart.chartArea.width / dataset.data.length,
            height: ({ chart }) => chart.chartArea.height,
            borderWidth: 1,
            data: indicators.map((indicator) => {
              return {
                x: indicator.name,
                y: "indicator",
                v: indicator.value,
              };
            }),
          },
        ],
      });
    }
  }, [indicators, stock.name]);

  const options = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: stock.name,
      },
      tooltip: {
        callbacks: {
          label: (context: TooltipItem<"matrix">) => {
            const v = context.raw as CategoricalMatrixDataPoint;
            return ["x: " + v.x, "y: " + v.y, "v: " + v.v];
          },
        },
      },
    },
    scales: {
      x: {
        type: "category" as keyof CartesianScaleTypeRegistry,
        labels: ["sma", "ema", "macd", "rsi"],
        ticks: {
          display: true,
        },
        grid: {
          display: false,
        },
      },
      y: {
        type: "category" as keyof CartesianScaleTypeRegistry,
        labels: ["indicator"],
        offset: true,
        ticks: {
          display: true,
        },
        grid: {
          display: false,
        },
      },
    },
  };
  return (
    <Matrix
      id="indicatorsChart"
      options={options}
      data={data}
      width={400}
      height={400}
    />
  );
};

const IconText = ({ icon, text }: { icon: React.FC; text: string }) => (
  <Space>
    {React.createElement(icon)}
    {text}
  </Space>
);

const StockPrice = ({ stock }: { stock: Stock }) => {
  const { prices } = useStockPrice(stock.ticker);
  const [data, setData] = useState<
    ChartData<CandlestickData<FinancialDataPoint>>
  >({
    datasets: [
      {
        label: stock.name,
        color: {
          up: "#01ff01",
          down: "#fe0000",
          unchanged: "#999",
        },
        data: [],
      },
    ],
  });

  useEffect(() => {
    if (prices) {
      setData({
        datasets: [
          {
            label: stock.name,
            color: {
              up: "#01ff01",
              down: "#fe0000",
              unchanged: "#999",
            },
            data: prices.map((price) => {
              return {
                x: new Date(price.timestamp).valueOf(),
                o: price.open,
                h: price.high,
                l: price.low,
                c: price.close,
              };
            }),
          },
        ],
      });
    }
  }, [prices, stock.name]);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
      },
      tooltip: {
        callbacks: {
          label: (context: TooltipItem<"candlestick">) => {
            const v = context.raw as FinancialDataPoint;
            return [
              "Open: " + v.o,
              "High: " + v.h,
              "Low: " + v.l,
              "Close: " + v.c,
            ];
          },
        },
      },
      title: {
        display: true,
        text: stock.name,
      },
    },
  };
  return (
    <Candlestick
      id="stockChart"
      options={options}
      data={data}
      width={1000}
      height={400}
    />
  );
};

const SentimentCharts = ({
  stock,
  source = "tweet",
}: {
  stock: Stock;
  source?: "tweet" | "news" | "reddit";
}) => {
  const { sentiments } = useSentiment(stock.ticker, source);
  const [data, setData] = useState<ChartData<PiechartData<number>, string[]>>({
    labels: [],
    datasets: [
      {
        label: "",
        data: [],
        backgroundColor: [],
      },
    ],
  });
  useEffect(() => {
    if (sentiments) {
      setData({
        labels: sentiments.map((sentiment) => sentiment.key),
        datasets: [
          {
            label: `${source} Sentiment`,
            backgroundColor: [
              "rgb(102, 189, 99)",
              "rgb(255, 255, 191)",
              "rgb(215, 48, 39)",
            ],
            data: sentiments.map((sentiment) => sentiment.value),
          },
        ],
      });
    }
  }, [sentiments, source]);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
      },
      title: {
        display: true,
        text: `${source[0].toUpperCase() + source.slice(1)} Sentiment`,
      },
    },
  };

  return (
    <Pie id="pieChart" data={data} options={options} height={300} width={300} />
  );
};

const Tweets = ({ stock }: { stock: Stock }) => {
  const getKey = (
    pageIndex: number,
    previousPageData: PaginatedList<Tweet>,
  ) => {
    if (previousPageData && !previousPageData.items.length) return null;
    return `/api/stock/${stock.ticker}/tweets?page=${pageIndex + 1}`;
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
            {
              <>
                <h1>Overall sentiment:</h1>
                <Space size={35}>
                  <IconText
                    icon={LikeOutlined}
                    text={tweets
                      .filter((item) => item.sentiment === "positive")
                      .length.toString()}
                  />
                  <IconText
                    icon={LineOutlined}
                    text={tweets
                      .filter((item) => item.sentiment === "neutral")
                      .length.toString()}
                  />
                  <IconText
                    icon={DislikeOutlined}
                    text={tweets
                      .filter((item) => item.sentiment === "negative")
                      .length.toString()}
                  />
                </Space>
              </>
            }
            <List
              dataSource={tweets}
              renderItem={(item) => (
                <List.Item
                  key={item.author}
                  actions={[
                    item.sentiment === "positive" && (
                      <IconText icon={LikeOutlined} text="1" />
                    ),
                    item.sentiment === "neutral" && (
                      <IconText icon={LineOutlined} text="1" />
                    ),
                    item.sentiment === "negative" && (
                      <IconText icon={DislikeOutlined} text="1" />
                    ),
                  ]}
                >
                  <Divider />
                  <List.Item.Meta
                    title={
                      <a target="_blank" rel="noreferrer" href={item.url}>
                        {item.author}
                      </a>
                    }
                    description={
                      <Space size={40}>
                        <div>Retweets: {item.retweets}</div>
                        <div>Likes: {item.likes}</div>
                        <div>Quotes: {item.quotes}</div>
                        <div>Replies: {item.replies}</div>
                        <div>Publicity Score: {item.pub_score}</div>
                        <div>Hashtags: {item.hashtags}</div>
                        <div>
                          {new Date(item.timestamp).toLocaleDateString()}
                        </div>
                      </Space>
                    }
                  />
                  {removeMarkdown(item.content)}
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
    return `/api/stock/${stock.ticker}/reddit?page=${pageIndex + 1}`;
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
            {
              <>
                <h1>Overall sentiment:</h1>
                <Space size={35}>
                  <IconText
                    icon={LikeOutlined}
                    text={reddit
                      .filter((item) => item.sentiment === "positive")
                      .length.toString()}
                  />
                  <IconText
                    icon={LineOutlined}
                    text={reddit
                      .filter((item) => item.sentiment === "neutral")
                      .length.toString()}
                  />
                  <IconText
                    icon={DislikeOutlined}
                    text={reddit
                      .filter((item) => item.sentiment === "negative")
                      .length.toString()}
                  />
                </Space>
              </>
            }
            <List
              dataSource={reddit}
              itemLayout="vertical"
              renderItem={(item, i) => (
                <List.Item
                  key={i}
                  actions={[
                    item.sentiment === "positive" && (
                      <IconText icon={LikeOutlined} text="1" />
                    ),
                    item.sentiment === "neutral" && (
                      <IconText icon={LineOutlined} text="1" />
                    ),
                    item.sentiment === "negative" && (
                      <IconText icon={DislikeOutlined} text="1" />
                    ),
                  ]}
                >
                  <Divider />
                  <List.Item.Meta
                    title={
                      <a target="_blank" rel="noreferrer" href={item.url}>
                        {item.author}
                      </a>
                    }
                    description={
                      <Space size={40}>
                        <div>Score: {item.score}</div>
                        <div>Commments: {item.num_comments}</div>
                        <div>
                          {new Date(item.timestamp).toLocaleDateString()}
                        </div>
                      </Space>
                    }
                  />
                  {removeMarkdown(item.content)}
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
    return `/api/stock/${stock.ticker}/news?page=${pageIndex + 1}`;
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
      <h3>News</h3>
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
            {
              <>
                <h1>Overall sentiment:</h1>
                <Space size={35}>
                  <IconText
                    icon={LikeOutlined}
                    text={news
                      .filter((item) => item.sentiment === "positive")
                      .length.toString()}
                  />
                  <IconText
                    icon={LineOutlined}
                    text={news
                      .filter((item) => item.sentiment === "neutral")
                      .length.toString()}
                  />
                  <IconText
                    icon={DislikeOutlined}
                    text={news
                      .filter((item) => item.sentiment === "negative")
                      .length.toString()}
                  />
                </Space>
              </>
            }
            <List
              dataSource={news}
              renderItem={(item) => (
                <List.Item
                  key={item.headline}
                  actions={[
                    item.sentiment === "positive" && (
                      <IconText icon={LikeOutlined} text="1" />
                    ),
                    item.sentiment === "neutral" && (
                      <IconText icon={LineOutlined} text="1" />
                    ),
                    item.sentiment === "negative" && (
                      <IconText icon={DislikeOutlined} text="1" />
                    ),
                  ]}
                >
                  <Divider />
                  <List.Item.Meta
                    title={
                      <a target="_blank" rel="noreferrer" href={item.url}>
                        {item.headline}
                      </a>
                    }
                  />
                  {"Source: " + item.source}
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
  const [ellipsis, setEllipsis] = useState(false);
  const [key, setKey] = useState(0);

  const typoMore = () => {
    setEllipsis(true);
    setKey(!ellipsis ? key + 0 : key + 1);
    return ellipsis;
  };
  const typoLess = () => {
    setEllipsis(false);
    setKey(!ellipsis ? key + 0 : key + 1);
    return ellipsis;
  };

  return (
    <div style={{ display: "flex", flexDirection: "row" }}>
      <Image src={stock.image_url ? stock.image_url : ""}></Image>
      <Card title={stock.name}>
        <Paragraph
          style={{ width: "800" }}
          key={key}
          ellipsis={{
            rows: 2,
            expandable: true,
            onExpand: typoMore,
            symbol: "more",
          }}
        >
          {stock.summary}
        </Paragraph>
        {ellipsis && <Button onClick={typoLess}>less</Button>}
      </Card>
    </div>
  );
};

const Dashboard = ({ ticker }: { ticker: string }) => {
  var { stock } = useStock(ticker);

  if (!stock) {
    return <div>Please Select a Stock</div>;
  }

  return (
    <Space size={40} direction="vertical" style={{ width: "100%" }}>
      <Space>
        <Profile stock={stock} />
      </Space>
      <Space style={{ width: "100%", justifyContent: "space-evenly" }}>
        <StockPrice stock={stock} />
        <Indicators stock={stock} />
      </Space>

      <Space style={{ width: "100%", justifyContent: "space-evenly" }}>
        <SentimentCharts stock={stock} source="news" />
        <SentimentCharts stock={stock} />
        <SentimentCharts stock={stock} source="reddit" />
      </Space>

      <NewsComponent stock={stock} />
      <Tweets stock={stock} />
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
  }, 1500);

  const onSelect = (data: string) => {
    setTicker(data);
  };

  const onSearch = (searchText: string) => {
    debounced(searchText);
  };

  return (
    <Space direction="vertical" size={30} style={{ width: "100%" }}>
      <h2>Home</h2>
      <AutoComplete
        options={options}
        style={{ width: 200 }}
        onSelect={onSelect}
        onSearch={onSearch}
        placeholder="Search stock"
      />
      <Dashboard ticker={ticker} />
    </Space>
  );
};

const App: React.FC = () => {
  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider>
        <div className="logo" style={{ color: "white", fontSize: 30 }}>
          Stocks
        </div>
        <Menu theme="dark" defaultSelectedKeys={["home"]} mode="inline">
          <Menu.Item key={"home"} icon={<HomeOutlined />} title={"Home"}>
            Home
          </Menu.Item>
        </Menu>
      </Sider>
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
