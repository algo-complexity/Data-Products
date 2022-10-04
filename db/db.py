from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Integer, String

from db.base import Base


class Stock(Base):
    __tablename__ = "stock"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    ticker = Column(String(4), nullable=False)
    summary = Column(String, nullable=False)
    exchange_id = Column(Integer, ForeignKey("exchange.id"), nullable=False)

    def __repr__(self):
        return f"""
                Stock(
                    id={self.id!r},
                    name={self.name!r},
                    ticker={self.ticker!r},
                    summary={self.summary!r}
                )
                """


class Exchange(Base):
    __tablename__ = "exchange"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    short_name = Column(String(5), nullable=False)
    country = Column(Integer, ForeignKey("country.id"), nullable=False)

    def __repr__(self):
        return f"""
                Exchange(
                    id={self.id!r},
                    name={self.name!r},
                    short_name={self.short_name!r},
                    country={self.country!r}
                )
                """


class Country(Base):
    __tablename__ = "country"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String(3), nullable=False)

    def __repr__(self):
        return f"""
                Country(
                    id={self.id!r},
                    name={self.name!r},
                    code={self.code!r}
                )
                """


class Price(Base):
    __tablename__ = "price"
    id = Column(Integer, primary_key=True)
    low = Column(Integer, nullable=False)
    high = Column(Integer, nullable=False)
    open = Column(Integer, nullable=False)
    close = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"""
                Price(
                    id={self.id!r},
                    low={self.low!r},
                    high={self.high!r},
                    open={self.open!r}
                    close={self.close!r}
                    timestamp={self.timestamp!r}
                )
                """


class StockPrice(Base):
    __tablename__ = "stockprice"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stock.id"), nullable=False)
    price_id = Column(Integer, ForeignKey("price.id"), nullable=False)

    def __repr__(self):
        return f"""
                StockPrice(
                    stock_id={self.stock_id!r},
                    price_id={self.price_id!r},
                )
                """


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    headline = Column(String, nullable=False)
    content = Column(String, nullable=False)
    url = Column(String, nullable=False)
    sentiment = Column(String)
    summary = Column(String, nullable=False)

    def __repr__(self):
        return f"""
                News(
                    id={self.id!r},
                    headline={self.headline!r},
                    content={self.content!r},
                    url={self.url!r},
                    sentiment={self.sentiment!r},
                    summary={self.summary!r},
                )
                """


class StockNews(Base):
    __tablename__ = "stocknews"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stock.id"), nullable=False)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)

    def __repr__(self):
        return f"""
                StockNews(
                    stock_id={self.stock_id!r},
                    news_id={self.news_id!r},
                )
                """


class Tweet(Base):
    __tablename__ = "tweet"
    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    author = Column(String, nullable=False)
    sentiment = Column(String)
    retweets = Column(Integer, nullable=False)
    comments = Column(Integer, nullable=False)
    hashtags = Column(String, nullable=False)
    likes = Column(Integer, nullable=False)
    url = Column(String, nullable=False)

    def __repr__(self):
        return f"""
                Tweet(
                    id={self.id!r},
                    content={self.content!r},
                    timestamp={self.timestamp!r},
                    author={self.author!r},
                    sentiment={self.sentiment!r},
                    retweets={self.retweets!r},
                    comments={self.comments!r},
                    hashtags={self.hashtags!r},
                    likes={self.likes!r},
                    url={self.url!r},
                )
                """


class StockTweet(Base):
    __tablename__ = "stocktweet"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stock.id"), nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweet.id"), nullable=False)

    def __repr__(self):
        return f"""
                StockTweet(
                    stock_id={self.stock_id!r},
                    tweet_id={self.tweet_id!r},
                )
                """


class RedditPost(Base):
    __tablename__ = "redditpost"
    id = Column(BigInteger, primary_key=True)
    api_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    author = Column(String, nullable=False)
    sentiment = Column(String)
    score = Column(Integer, nullable=False)
    num_comments = Column(Integer, nullable=False)
    url = Column(String, nullable=False)

    def __repr__(self):
        return f"""
                RedditPost(
                    id={self.id!r},
                    title={self.title!r},
                    content={self.content!r},
                    timestamp={self.timestamp!r},
                    author={self.author!r},
                    sentiment={self.sentiment!r},
                    score={self.score!r},
                    num_comments={self.num_comments!r},
                    url={self.url!r},
                )
                """


class StockReddit(Base):
    __tablename__ = "stockreddit"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stock.id"), nullable=False)
    redditpost_id = Column(BigInteger, ForeignKey("redditpost.id"), nullable=False)

    def __repr__(self):
        return f"""
                StockReddit(
                    stock_id={self.stock_id!r},
                    redditpost_id={self.redditpost_id!r},
                )
                """


class Indicator(Base):
    __tablename__ = "indicator"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    value = Column(Float, nullable=False)

    def __repr__(self):
        return f"""
                Indicator(
                    id={self.id!r},
                    name={self.name!r},
                    value={self.value!r},
                )
                """


class StockIndicator(Base):
    __tablename__ = "stockindicator"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stock.id"), nullable=False)
    indicator_id = Column(Integer, ForeignKey("indicator.id"), nullable=False)

    def __repr__(self):
        return f"""
                StockIndicator(
                    stock_id={self.stock_id!r},
                    indicator_id={self.indicator_id!r},
                )
                """
