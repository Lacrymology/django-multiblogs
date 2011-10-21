from django.db import models
from datetime import datetime

class PublishedManager(models.Manager):

    def get_query_set(self):
        return super(PublishedManager, self).get_query_set().filter(published=True)

class PublishedPostManager(models.Manager):
    def get_query_set(self):
        now = datetime.now()
        return super(PublishedPostManager, self).get_query_set().filter(publish_date__lte=now, is_active=True)

