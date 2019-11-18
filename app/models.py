from django.db.models import Model, Manager, DateTimeField
from django.contrib.postgres.fields import JSONField
from django.utils import timezone


class ResultManager(Manager):

    def results_seen(self, signal):
        return self.filter(
            json__contains=signal,
        )

    def results_seen_not_doing_rov(self):
        return self.results_seen(Result.not_rov_signal)

    def results_seen_doing_rov(self):
        return self.results_seen(Result.rov_signal)

    def ases_have_been_seen_not_doing_rov(self, asns):
        return self.results_seen_not_doing_rov(
        ).filter(
            json__asn__contains=asns
        ).count() >= 1

    def ases_have_been_seen_doing_rov(self, asns):
        return self.results_seen_doing_rov(
        ).filter(
            json__asn__contains=asns
        ).count() >= 1

    def ases_are_new_to_rov(self, asn):
        """
        This method is to be called immediately after saving the object into DB
        :param asn:
        :return:
        """
        return self.results_seen_doing_rov(
        ).filter(
            json__asn__contains=asn
        ).count() == 1

    @staticmethod
    def is_documentation_asn(asn):
        """

        Documentation ASNs are used for testing the production API

        :param asn:
        :return:

        https://tools.ietf.org/html/rfc5398#section-4
        """
        return 64496 <= int(asn) <= 64511 or 65536 <= int(asn) <= 65551


class Result(Model):
    json = JSONField(default=dict)
    date = DateTimeField(default=timezone.now)

    # Signal that this fetch is being performed
    # from a network which is doing Route Origin Validation
    # (rpki-valid=true, rpki-invalid=false, asns)
    rov_signal = {
        "rpki-valid-passed": True,
        "rpki-invalid-passed": False,
    }

    # Signal that this fetch is being performed
    # from a network which is *not* doing Route Origin Validation
    # (rpki-valid=true, rpki-invalid=false, asns)
    not_rov_signal = {
        "rpki-valid-passed": True,
        "rpki-invalid-passed": True,
    }

    objects = ResultManager()

    def __str__(self):
        return f"(AS{self.json['asn'][0] if len(self.json['asn']) >= 1 else 'Unknown AS'}) ROV={self.is_doing_rpki()}"

    def get_events(self):

        if 'events' in self.json.keys():
            return self.json['events']

        return []

    def get_event(self, evt):

        for event in self.get_events():
            if event["stage"] == evt:
                return event

        return {}

    @staticmethod
    def is_event(event):
        """
        :param event: Python dict to be tested for event-ivity
        """

        return "data" in event and "duration" in event["data"]

    def is_doing_rpki(self):
        valid = self.json["rpki-valid-passed"]
        invalid = self.json["rpki-invalid-passed"]

        if type(valid) != bool or type(invalid) != bool:
            return False

        if not self.has_finished_ont_time():
            return False

        # is able to fetch the valid resource and
        # not able to fetch the invalid
        return valid and not invalid

    def has_finished_ont_time(self):

        if self.json.get('finished-on-time'):
            return self.json['finished-on-time']
        else:
            return False
