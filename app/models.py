from django.db.models import Model, Manager, DateTimeField
from django.contrib.postgres.fields import JSONField
from datetime import datetime


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
            json__contains={"asns": asns}
        ).count() >= 1

    def ases_have_been_seen_doing_rov(self, asns):
        return self.results_seen_doing_rov(
        ).filter(
            json__contains={"asns": asns}
        ).count() >= 1

    def ases_are_new_to_rov(self, asns):
        """
        This method is to be called immediately after saving the object into DB
        :param asns:
        :return:
        """
        return self.results_seen_doing_rov(
        ).filter(
            json__contains={"asns": asns}
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
    date = DateTimeField(default=datetime.now)

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
        return "(AS{asns}) ROV={rov}".format(
            asns=self.json['asns'],
            rov=self.is_doing_rpki()
        )

    def is_doing_rpki(self):
        valid = self.json["rpki-valid-passed"]
        invalid = self.json["rpki-invalid-passed"]

        if type(valid) != bool or type(invalid) != bool:
            return False

        # is able to fetch the valid resource and
        # not able to fetch the invalid
        return valid and not invalid
