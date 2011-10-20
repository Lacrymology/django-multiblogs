from django.db import models
from datetime import datetime

class PublishedManager(models.Manager):

    def active(self):
        """
        Retrieves all active posts which have been published.
        
        """
        now = datetime.now()
        return self.get_query_set().filter(published_on__lte=now)

    def live(self, user=None):
        """Retrieves all live posts"""

        qs = self.active()

        if user is not None and user.is_superuser:
            # superusers get to see all entries 
            return qs
        else:
            # only show live entries to regular users
            return qs.filter(published=True)

