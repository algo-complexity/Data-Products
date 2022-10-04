import uuid

import numpy as np
import pandas as pd
import praw
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from config import Config, config

# retrieve env vars
config: Config
CLIENT_ID = config.reddit_client_id
CLIENT_SECRET = config.reddit_client_secret
USER_AGENT = config.reddit_user_agent

# instantiate reddit object
reddit = praw.Reddit(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT
)

# download vader lexicon for sentiment analysis
# nltk.download("vader_lexicon")


def get_posts(subreddit, symb, time="week"):
    """Fetches reddit posts and relevant information sentiment score.

    Args:
        subreddit (str): name of subreddit eg. "wallstreetbets"
        symb (str): symbol to search for eg. "BBBY"
        time (str, optional): Time period for fetching posts. Defaults to "week".

    Returns:
        DataFrame: Pandas df
    """
    posts = []
    sent = SentimentIntensityAnalyzer()
    for post in reddit.subreddit(subreddit).search(symb, time_filter=time):
        if post.is_self:
            # FIXME: BigInteger allows for 65bit, but still not 128
            id = uuid.uuid1().int >> 64
            posts.append(
                [
                    id,
                    post.title,
                    post.selftext,
                    pd.to_datetime(post.created, unit="s"),
                    post.author.name,
                    round(sent.polarity_scores(post.selftext)["compound"], 2),
                    post.score,
                    post.num_comments,
                    post.url,
                    post.id,
                ]
            )
    df = pd.DataFrame(
        posts,
        columns=[
            "id",
            "title",
            "content",
            "timestamp",
            "author",
            "sentiment",
            "score",
            "num_comments",
            "url",
            "api_id",
        ],
    )
    # remove rows with empty strings/null
    df.replace("", np.nan, inplace=True)
    df.dropna(inplace=True)
    return df
