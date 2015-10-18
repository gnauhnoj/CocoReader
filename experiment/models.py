from django.db import models
from djangotoolbox.fields import ListField


# Create your models here.
class Annotation(models.Model):
    models.image_id = models.IntegerField()
    models.category_id = models.IntegerField()
    models.id = models.IntegerField()
    models.bbox = ListField()


class Image(models.Model):
    caption = models.CharField(max_length=200)

    def __str__(self):              # __unicode__ on Python 2
        return self.caption
