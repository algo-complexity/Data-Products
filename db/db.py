from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from db.base import Base


class Stock(Base):
    __tablename__ = "stock"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    ticker = Column(String(4))
    summary = Column(String)
    exchange_id = Column(Integer, ForeignKey("exchange.id"))

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
    name = Column(String)
    short_name = Column(String(5))
    country = Column(Integer, ForeignKey("country.id"))

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
    name = Column(String)
    code = Column(String(3))

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
    low = Column(Integer)
    high = Column(Integer)
    open = Column(Integer)
    close = Column(Integer)
    # TODO standardize timezone?
    timestamp = Column(DateTime(timezone=True))

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
    stock_id = Column(Integer, ForeignKey("stock.id"))
    price_id = Column(Integer, ForeignKey("price.id"))

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
    headline = Column(String)
    content = Column(String)
    url = Column(String)
    sentiment = Column(String, nullable=True)
    # TODO text summarization
    summary = Column(String)

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
    stock_id = Column(Integer, ForeignKey("stock.id"))
    news_id = Column(Integer, ForeignKey("news.id"))

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
    content = Column(String)
    timestamp = Column(DateTime(timezone=True))
    author = Column(String)
    sentiment = Column(String, nullable=True)
    retweets = Column(Integer)
    comments = Column(Integer)
    hashtags = Column(String)
    likes = Column(Integer)
    url = Column(String)

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
    stock_id = Column(Integer, ForeignKey("stock.id"))
    tweet_id = Column(Integer, ForeignKey("tweet.id"))

    def __repr__(self):
        return f"""
                StockTweet(
                    stock_id={self.stock_id!r},
                    tweet_id={self.tweet_id!r},
                )
                """


class RedditPost(Base):
    __tablename__ = "redditpost"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    timestamp = Column(DateTime(timezone=True))
    author = Column(String)
    sentiment = Column(String, nullable=True)
    score = Column(Integer)
    num_comments = Column(Integer)
    url = Column(String)

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
    stock_id = Column(Integer, ForeignKey("stock.id"))
    redditpost_id = Column(Integer, ForeignKey("redditpost.id"))

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
    name = Column(String)
    value = Column(Float)

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
    stock_id = Column(Integer, ForeignKey("stock.id"))
    indicator_id = Column(Integer, ForeignKey("indicator.id"))

    def __repr__(self):
        return f"""
                StockIndicator(
                    stock_id={self.stock_id!r},
                    indicator_id={self.indicator_id!r},
                )
                """
