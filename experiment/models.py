from django.db import models
from djangotoolbox.fields import ListField


# it's unclear to me if classmethods work with mongo...
class User(models.Model):
    username = models.CharField(max_length=30, blank=False, unique=True, db_index=True)
    score = models.IntegerField(default=0, blank=False, db_index=True)
