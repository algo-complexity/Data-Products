import React, { useEffect, useState } from "react";
import { HomeOutlined, UserOutlined } from "@ant-design/icons";
import {
  Layout,
  Menu,
  Space,
  AutoComplete,
  List,
  Divider,
  Skeleton,
  Card,
  Tag,
} from "antd";
import "antd/dist/antd.css";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import {
  fetcher,
  searchResearcher,
  useResearcher,
  useResearcherCitations,
  useResearcherWebsites,
  useSCSEGraph,
} from "./api/api";
import {
  BarChartData,
  PaginatedList,
  Publication,
  Researcher,
} from "./api/types";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import InfiniteScroll from "react-infinite-scroll-component";
import useSWRInfinite from "swr/infinite";
import { ForceGraph2D } from "react-force-graph";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
);

const { Content, Footer, Sider } = Layout;

const Citations = ({ researcher }: { researcher: Researcher }) => {
  const { citations } = useResearcherCitations(researcher.name);
  const [data, setData] = useState<BarChartData>({
    labels: [1, 2, 3, 4],
    datasets: [],
  });

  useEffect(() => {
    if (citations) {
      setData({
        labels: citations.map((citation) =>
          new Date(citation.year).getFullYear(),
        ),
        datasets: [
          {
            label: researcher.name,
            data: citations.map((citation) => citation.count),
            backgroundColor: "rgba(255, 99, 132, 0.5)",
          },
        ],
      });
    }
  }, [citations, researcher.name]);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
      },
      title: {
        display: true,
        text: "Number of Citations",
      },
    },
  };

  return <Bar options={options} data={data} width={600} height={500} />;
};

const Coauthors = ({
  researcher,
  setName,
}: {
  researcher: Researcher;
  setName: React.Dispatch<React.SetStateAction<string>>;
}) => {
  return (
    <>
      <h3>Co-Authors</h3>
      <List
        bordered
        dataSource={researcher.co_authors}
        style={{ border: "1px solid rgba(140, 140, 140, 0.35)" }}
        renderItem={(item) => (
          <List.Item key={item}>
            <div onClick={() => setName(item)} style={{ cursor: "pointer" }}>
              {item}
            </div>
          </List.Item>
        )}
      />
    </>
  );
};

const Publications = ({ researcher }: { researcher: Researcher }) => {
  const getKey = (
    pageIndex: number,
    previousPageData: PaginatedList<Publication>,
  ) => {
    if (previousPageData && !previousPageData.items.length) return null;
    return `/api/researcher/${researcher.name}/publications?page=${
      pageIndex + 1
    }`;
  };

  const { data, size, setSize } = useSWRInfinite<PaginatedList<Publication>>(
    getKey,
    fetcher,
    { initialSize: 1 },
  );

  const [publications, setPublications] = useState<Publication[]>([]);
  const [maxData, setMaxData] = useState(0);

  useEffect(() => {
    if (data) {
      setPublications(data.map((paged) => paged.items).flat());
      setMaxData(data[0].total);
    }
  }, [data]);

  return (
    <>
      <h3>Publications</h3>
      <div
        id="scrollableDiv"
        style={{
          height: 400,
          overflow: "auto",
          padding: "0 16px",
          border: "1px solid rgba(140, 140, 140, 0.35)",
        }}
      >
        {data && publications ? (
          <InfiniteScroll
            dataLength={publications.length}
            next={() => setSize(size + 1)}
            hasMore={publications.length < maxData}
            loader={<Skeleton avatar paragraph={{ rows: 1 }} active />}
            endMessage={<Divider plain>End</Divider>}
            scrollableTarget="scrollableDiv"
          >
            <List
              dataSource={publications}
              renderItem={(item) => (
                <List.Item key={item.title}>
                  <List.Item.Meta
                    title={
                      <a href={item.paper_url ? item.paper_url : "#"}>
                        {item.title}
                      </a>
                    }
                    description={item.conference}
                  />
                  <div>Citations: {item.num_citations}</div>
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

const Profile = ({ researcher }: { researcher: Researcher }) => {
  var imageUrl = "";
  const { websites } = useResearcherWebsites(researcher.name);
  if (websites) {
    imageUrl = websites.items
      .filter((website) => website.type === "image")
      .map((website) => website.url)[0];
  }

  return (
    <Card
      title={researcher.name}
      size={"small"}
      cover={
        <img
          alt="Profile"
          style={{ height: 350, objectFit: "contain" }}
          src={imageUrl}
        />
      }
    >
      <p>Email: {researcher.email}</p>
      <p>Number of Citations: {researcher.citations}</p>
      {researcher.interests.map((interest) => (
        <Tag>{interest}</Tag>
      ))}
    </Card>
  );
};

const Dashboard = ({
  name,
  setName,
}: {
  name: string;
  setName: React.Dispatch<React.SetStateAction<string>>;
}) => {
  const { researcher } = useResearcher(name);

  if (!researcher) {
    return <div>Please Select a researcher</div>;
  }

  return (
    <Space size={40} direction="vertical">
      <Space align="start" size={100} direction="horizontal">
        <Profile researcher={researcher} />
        <Citations researcher={researcher} />
      </Space>
      <Publications researcher={researcher} />
      <Coauthors researcher={researcher} setName={setName} />
    </Space>
  );
};

const Home: React.FC = () => {
  const [options, setOptions] = useState<{ value: string }[]>([]);
  const [name, setName] = useState("");

  const onSelect = (data: string) => {
    setName(data);
  };

  const onSearch = (searchText: string) => {
    searchResearcher(searchText).then((researchers) => {
      setOptions(
        researchers.map((researcher) => {
          return { value: researcher.name };
        }),
      );
    });
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
          placeholder="Search Researcher"
        />
        <Dashboard name={name} setName={setName} />
      </Space>
    </div>
  );
};
const SCSE: React.FC = () => {
  const { graph } = useSCSEGraph();

  return (
    <div>
      <h2>SCSE</h2>
      <ForceGraph2D
        graphData={graph}
        nodeAutoColorBy="type"
        nodeLabel={(node: any) => {
          return `<div>
          ${
            node.type === "prof"
              ? `<h4>Prof: ${node.name}</h4><p>Citations:${node.data.citations}</p>`
              : `<h4>Interest: ${node.name}</h4>`
          }
          </div>`;
        }}
        nodeCanvasObject={(node: any, ctx, globalScale) => {
          const label = node.id;
          const fontSize = 12 / globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          const textWidth = ctx.measureText(label).width;
          const bckgDimensions: [number, number] = [
            textWidth + fontSize * 0.2,
            fontSize + fontSize * 0.2,
          ]; // some padding

          ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
          ctx.fillRect(
            node.x - bckgDimensions[0] / 2,
            node.y - bckgDimensions[1] / 2,
            ...bckgDimensions,
          );

          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillStyle = node.color;
          ctx.fillText(label, node.x, node.y);

          node.__bckgDimensions = bckgDimensions; // to re-use in nodePointerAreaPaint
        }}
      />
    </div>
  );
};

const App: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <Router>
      <Layout style={{ minHeight: "100vh" }}>
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={(value) => setCollapsed(value)}
        >
          <div className="logo" style={{ color: "white", fontSize: 30 }}>
            Data Products
          </div>
          <Menu theme="dark" defaultSelectedKeys={["home"]} mode="inline">
            <Menu.Item key={"home"} icon={<HomeOutlined />} title={"Home"}>
              <Link to={"/"}>Home</Link>
            </Menu.Item>
            <Menu.Item key={"scse"} icon={<UserOutlined />}>
              <Link to={"/scse"}>SCSE</Link>
            </Menu.Item>
          </Menu>
        </Sider>
        <Layout className="site-layout">
          <Content style={{ margin: "0 16px" }}>
            <div
              className="site-layout-background"
              style={{ padding: 24, minHeight: 360 }}
            >
              <Routes>
                <Route path="/scse" element={<SCSE />} />
                <Route path="/" element={<Home />} />
              </Routes>
            </div>
          </Content>
          <Footer style={{ textAlign: "center" }}>Bhargav Singapuri</Footer>
        </Layout>
      </Layout>
    </Router>
  );
};

export default App;
