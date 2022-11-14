from django.contrib.postgres.search import TrigramWordSimilarity
from django.db import models
from django.db.models import Q


class AccessControlledQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(
            Q(access_policy__isnull=True)
            | Q(access_policy__users=user)
            | Q(access_policy__groups__user=user)
        ).distinct()

    def for_user_active(self, user):
        return self.for_user(user).filter(deleted_at=None)


class FuzzySearchable(models.QuerySet):
    def fuzzy_search(self, query, field="name"):
        if not query:
            return self
        return (
            self.annotate(similarity=TrigramWordSimilarity(query, field))
            .filter(**{f"{field}__trigram_word_similar": query})
            .order_by("-similarity")
        )
