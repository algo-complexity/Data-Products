from . import models, services
from django.db.models.signals import post_save
from django.dispatch import receiver
import pandas as pd


@receiver(post_save, sender=models.Stock)
def handle_stock_post_save(instance: models.Stock, created: bool, **kwargs):
    if created:
        # Add Reddit
        df = pd.DataFrame()
        for subreddit in ["wallstreetbets", "superstonk"]:
            data = services.get_reddit_posts(subreddit, instance.ticker)
            df = pd.concat([df, data])
        for args in df.itertuples(index=False):
            models.Reddit.objects.update_or_create(
                api_id=args.api_id,
                defaults=dict(
                    title=args.title,
                    content=args.content,
                    timestamp=args.timestamp,
                    author=args.author,
                    sentiment=args.sentiment,
                    score=args.score,
                    num_comments=args.num_comments,
                    url=args.url,
                    stock=instance,
                ),
            )

        # Add Twitter
        df = pd.DataFrame()
        data = services.get_tweets(instance.ticker)
        df = pd.concat([df, data])
        for args in df.itertuples(index=False):
            models.Tweet.objects.update_or_create(
                api_id=0, # TODO make api_id schema unique in models.py
                defaults=dict(
                    content = args.text,
                    timestamp = args.created_at,
                    author = args.author_id,
                    url = args.url,
                    sentiment = args.sentiment,
                    retweets = args.retweet_count,
                    replies = args.reply_count,
                    likes = args.like_count,
                    quotes = args.quote_count,
                    pub_score = args.pub_score,
                    hashtags = args.hashtags,
                    stock = instance
                ),
            )
