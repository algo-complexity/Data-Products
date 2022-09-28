import os

import nltk
import pandas as pd
import praw
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# retrieve env vars
CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
USER_AGENT = os.environ.get("REDDIT_USER_AGENT")

# instantiate reddit object
reddit = praw.Reddit(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT
)

# download vader lexicon for sentiment analysis
nltk.download("vader_lexicon")


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
    for post in reddit.subreddit(subreddit).search(symb, time_filter=time):
        if post.is_self:
            posts.append(
                [
                    post.title,
                    post.score,
                    post.id,
                    post.subreddit,
                    post.url,
                    post.num_comments,
                    post.selftext,
                    post.created,
                ]
            )
    df = pd.DataFrame(
        posts,
        columns=[
            "title",
            "score",
            "id",
            "subreddit",
            "url",
            "num_comments",
            "body",
            "created",
        ],
    )

    df["timestamp"] = pd.to_datetime(df["created"], unit="s")

    sent = SentimentIntensityAnalyzer()
    b_polarity = [round(sent.polarity_scores(i)["compound"], 2) for i in df["body"]]
    df["body_sentiment_score"] = b_polarity

    t_polarity = [round(sent.polarity_scores(i)["compound"], 2) for i in df["title"]]
    df["title_sentiment_score"] = t_polarity

    return df
