from django.contrib.postgres.indexes import GinIndex
from django.db import models

from models import FuzzySearchable


class Stock(models.Model):
    class Meta:
        indexes = [
            GinIndex(
                name="stock_name_gin_idx",
                fields=["name"],
                opclasses=["gin_trgm_ops"],
            )
        ]

    objects = FuzzySearchable.as_manager()

    name = models.TextField()
    ticker = models.CharField(max_length=4, unique=True)
    summary = models.TextField()
    image_url = models.URLField(null=True)

    def __str__(self) -> str:
        return f"{self.name}: {self.ticker}"


class Price(models.Model):
    open = models.DecimalField(max_digits=20, decimal_places=5)
    high = models.DecimalField(max_digits=20, decimal_places=5)
    low = models.DecimalField(max_digits=20, decimal_places=5)
    close = models.DecimalField(max_digits=20, decimal_places=5)
    timestamp = models.DateTimeField()
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.stock.name} @ {self.timestamp.strftime('%Y-%m-%d')}: Open {self.open}, High {self.high}, Low {self.low}, Close {self.close}"


class SentimentChoices(models.TextChoices):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class News(models.Model):

    headline = models.TextField()
    url = models.URLField()
    timestamp = models.DateTimeField()
    sentiment = models.TextField(null=True, choices=SentimentChoices.choices)
    source = models.TextField()
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)


class Tweet(models.Model):
    # TODO: figure out how to make this unique?
    api_id = models.PositiveBigIntegerField(null=True)
    content = models.TextField()
    timestamp = models.DateTimeField()
    author = models.TextField()
    url = models.URLField()
    sentiment = models.TextField(null=True, choices=SentimentChoices.choices)
    retweets = models.PositiveIntegerField()
    replies = models.PositiveIntegerField()
    likes = models.PositiveIntegerField()
    quotes = models.PositiveIntegerField()
    pub_score = models.PositiveIntegerField()
    hashtags = models.TextField()
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)


class Reddit(models.Model):

    api_id = models.TextField(unique=True)
    title = models.TextField()
    content = models.TextField()
    timestamp = models.DateTimeField()
    author = models.TextField()
    sentiment = models.TextField(null=True, choices=SentimentChoices.choices)
    score = models.IntegerField()
    num_comments = models.IntegerField()
    url = models.URLField()
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.title}"


class Indicator(models.Model):
    class Meta:
        indexes = [
            GinIndex(
                name="indicator_name_gin_idx",
                fields=["name"],
                opclasses=["gin_trgm_ops"],
            )
        ]

    objects = FuzzySearchable.as_manager()

    name = models.TextField()
    value = models.DecimalField(max_digits=20, decimal_places=5)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.stock.name} @ {self.name}: {self.value}"
