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
                    stock=instance
                )
            )

        models.Stock.objects.update_or_create(
            ticker=instance.ticker,
            defaults=dict(
                name=instance.name,
                summary=instance.summary,
                image_url=services.get_image_url(instance.name)
            )
        )
