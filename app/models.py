from django.db.models import Model
from django.contrib.postgres.fields import JSONField

# Create your models here.


class Result(Model):

    json = JSONField(default=dict)
