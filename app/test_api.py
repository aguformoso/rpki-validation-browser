from django.test import override_settings
from rest_framework.test import APITestCase
from app.models import Result


class RpkiSmileyTestCase:
    """
    Holds all common info for test cases
    """
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) " \
                 "AppleWebKit/537.36 (KHTML, like Gecko) " \
                 "Chrome/75.0.3770.100 Safari/537.36"


@override_settings(DEBUG=True)
class RpkiAPITestCase(APITestCase):
    fixtures = ['no-rov.json']
    asn = ["3333"]

    def test_invalid_true(self):
        """
        """

        self.assertEqual(
            Result.objects.ases_are_new_to_rov(asn=self.asn),
            False
        )

        # # posting "rpki-invalid-passed": true won't be perceived as ROV
        self.client.post(
            path='/results/',
            data={
                "json": {
                    "asn": self.asn,
                    "pfx": "193.0.20.0/23",
                    "rpki-valid-passed": True,
                    "rpki-invalid-passed": True
                },
                "date": "2019-08-27T00:00:00.000Z"
            },
            format='json'
        )
        self.assertEqual(
            Result.objects.ases_are_new_to_rov(asn=self.asn),
            False
        )

    def test_documentation_asn(self):

        self.assertEqual(Result.objects.count(), 2)

        documentation_asn = ["64496"]

        self.client.post(
            path='/results/',
            data={
                "json": {
                    "asn": documentation_asn,
                    "pfx": "193.0.20.0/23",
                    "rpki-valid-passed": True,
                    "rpki-invalid-passed": True
                },
                "date": "2019-08-27T00:00:00.000Z"},
            format='json'
        )

        self.assertEqual(Result.objects.count(), 2)


@override_settings(DEBUG=True)
class NullTestCase(APITestCase):
    fixtures = ['null-rov.json']
    asn = ["24555"]

    def test_invalid_none(self):
        """
        Some browsers won't fetch the resource behind rpki-invalid-passed, posting

        "rpki-valid-passed": true,
        "rpki-invalid-passed": null
        """

        self.client.post(
            path='/results/',
            data={
                "json": {
                    "asn": self.asn,
                    "pfx": "193.0.20.0/23",
                    "rpki-valid-passed": True,
                    "rpki-invalid-passed": None
                },
                "date": "2019-08-27T00:00:00.000Z"
            },
            format='json'
        )

        self.assertEqual(
            Result.objects.ases_are_new_to_rov(asn=self.asn),
            False
        )

    def test_rov(self):

        self.client.post(
            path='/results/',
            data={
                "json": {
                    "asn": self.asn,
                    "pfx": "193.0.20.0/23",
                    "rpki-valid-passed": True,
                    "rpki-invalid-passed": False
                },
                "date": "2019-08-27T00:00:00.000Z"
            },
            format='json'
        )

        self.assertEqual(
            Result.objects.ases_are_new_to_rov(asn=self.asn),
            True
        )
