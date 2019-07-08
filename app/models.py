from django.db.models import Model, DateTimeField
from django.contrib.postgres.fields import JSONField
from datetime import datetime


class Result(Model):

    json = JSONField(default=dict)
    date = DateTimeField(default=datetime.now)

    def is_doing_rpki(self):
        return self.json["rpki-valid-passed"] and not self.json["rpki-invalid-passed"]
