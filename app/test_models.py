from django.test import TestCase, override_settings
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
class ResultTestCase(TestCase):
    fixtures = ['no-rov.json']
    asn = "3333"

    def test_have_been_seen_functions(self):
        """
        """

        self.assertEqual(
            Result.objects.ases_have_been_seen_not_doing_rov(self.asn),
            not Result.objects.ases_have_been_seen_doing_rov(self.asn)
        )

    def test_add_rov_result(self):
        """
        Multi-test
        """

        # conditions I expect from fixture...
        self.assertTrue(Result.objects.ases_have_been_seen_not_doing_rov(self.asn))
        self.assertFalse(Result.objects.ases_have_been_seen_doing_rov(self.asn))
        self.assertEqual(Result.objects.results_seen_doing_rov().count(), 0)

        new = Result(
            json=Result.rov_signal
        )
        new.json.update({"asns": self.asn})
        new.save()

        # Test the new object is the only one seen doing ROV
        self.assertTrue(Result.objects.ases_are_new_to_rov(self.asn))

        # Results for this ASN still should report as have seen
        # not doing ROV (previous results)
        self.assertTrue(Result.objects.ases_have_been_seen_not_doing_rov(self.asn))

        # ...but also report doing ROV now (new result)
        self.assertTrue(Result.objects.ases_have_been_seen_doing_rov(self.asn))

        # The total amount is 1
        self.assertEqual(Result.objects.results_seen_doing_rov().count(), 1)


@override_settings(DEBUG=True)
class ResultTestCaseCompat(TestCase):
    fixtures = ['no-rov.json']
    asn = "3333"

    def test_have_been_seen_functions(self):
        """
        """

        self.assertEqual(
            Result.objects.ases_have_been_seen_not_doing_rov(self.asn),
            not Result.objects.ases_have_been_seen_doing_rov(self.asn)
        )

    def test_add_rov_result(self):
        """
        Multi-test
        """

        # conditions I expect from fixture...
        self.assertTrue(Result.objects.ases_have_been_seen_not_doing_rov(self.asn))
        self.assertFalse(Result.objects.ases_have_been_seen_doing_rov(self.asn))
        self.assertEqual(Result.objects.results_seen_doing_rov().count(), 0)

        new = Result(
            json=Result.rov_signal
        )
        new.json.update({"asn": self.asn})
        new.save()

        # Test the new object is the only one seen doing ROV
        self.assertTrue(Result.objects.ases_are_new_to_rov(self.asn))

        # Results for this ASN still should report as have seen
        # not doing ROV (previous results)
        self.assertTrue(Result.objects.ases_have_been_seen_not_doing_rov(self.asn))

        # ...but also report doing ROV now (new result)
        self.assertTrue(Result.objects.ases_have_been_seen_doing_rov(self.asn))

        # The total amount is 1
        self.assertEqual(Result.objects.results_seen_doing_rov().count(), 1)


@override_settings(DEBUG=True)
class RpkiAPITestCase(APITestCase):
    fixtures = ['no-rov.json']
    asn = "3333"

    def test_invalid_true(self):
        """
        """

        self.assertEqual(
            Result.objects.ases_are_new_to_rov(asns=self.asn),
            False
        )

        # # posting "rpki-invalid-passed": true won't be perceived as ROV
        self.client.post(
            path='/results/',
            data={
                "json": {
                    "asns": [self.asn],
                    "pfx": "193.0.20.0/23",
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
                    "rpki-valid-passed": True,
                    "rpki-invalid-passed": True
                },
                "date": "2019-08-27T00:00:00.000Z"
            },
            format='json'
        )
        self.assertEqual(
            Result.objects.ases_are_new_to_rov(asns=self.asn),
            False
        )


@override_settings(DEBUG=True)
class RpkiAPITestCaseCompat(APITestCase):
    fixtures = ['no-rov.json']
    asn = "3333"

    def test_invalid_true(self):
        """
        """

        self.assertEqual(
            Result.objects.ases_are_new_to_rov(asns=self.asn),
            False
        )

        # # posting "rpki-invalid-passed": true won't be perceived as ROV
        self.client.post(
            path='/results/',
            data={
                "json": {
                    "asn": [self.asn],
                    "pfx": "193.0.20.0/23",
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
                    "rpki-valid-passed": True,
                    "rpki-invalid-passed": True
                },
                "date": "2019-08-27T00:00:00.000Z"
            },
            format='json'
        )
        self.assertEqual(
            Result.objects.ases_are_new_to_rov(asns=self.asn),
            False
        )


@override_settings(DEBUG=True)
class ResultApiTestCase(APITestCase):
    fixtures = ['no-rov.json']

    def test_documentation_asn(self):

        self.assertEqual(Result.objects.count(), 2)

        documentation_asn = "64496"

        self.client.post(
            path='/results/',
            data={
                "json": {
                    "asns": [documentation_asn],
                    "pfx": "193.0.20.0/23",
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
                    "rpki-valid-passed": True,
                    "rpki-invalid-passed": True
                },
                "date": "2019-08-27T00:00:00.000Z"},
            format='json'
        )

        self.assertEqual(Result.objects.count(), 2)


@override_settings(DEBUG=True)
class ResultApiTestCaseCompat(APITestCase):
    fixtures = ['no-rov.json']

    def test_documentation_asn(self):

        self.assertEqual(Result.objects.count(), 2)

        documentation_asn = "64496"

        self.client.post(
            path='/results/',
            data={
                "json": {
                    "asn": [documentation_asn],
                    "pfx": "193.0.20.0/23",
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
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
    asn = "24555"

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
                    "asns": [self.asn],
                    "pfx": "193.0.20.0/23",
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
                    "rpki-valid-passed": True,
                    "rpki-invalid-passed": None
                },
                "date": "2019-08-27T00:00:00.000Z"
            },
            format='json'
        )

        self.assertEqual(
            Result.objects.ases_are_new_to_rov(asns=self.asn),
            False
        )

    def test_rov(self):

        self.client.post(
            path='/results/',
            data={
                "json": {
                    "asns": [self.asn],
                    "pfx": "193.0.20.0/23",
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
                    "rpki-valid-passed": True,
                    "rpki-invalid-passed": False
                },
                "date": "2019-08-27T00:00:00.000Z"
            },
            format='json'
        )

        self.assertEqual(
            Result.objects.ases_are_new_to_rov(asns=self.asn),
            True
        )


@override_settings(DEBUG=True)
class NullTestCaseCompat(APITestCase):
    fixtures = ['null-rov.json']
    asn = "24555"

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
                    "asn": [self.asn],
                    "pfx": "193.0.20.0/23",
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
                    "rpki-valid-passed": True,
                    "rpki-invalid-passed": None
                },
                "date": "2019-08-27T00:00:00.000Z"
            },
            format='json'
        )

        self.assertEqual(
            Result.objects.ases_are_new_to_rov(asns=self.asn),
            False
        )

    def test_rov(self):

        self.client.post(
            path='/results/',
            data={
                "json": {
                    "asn": [self.asn],
                    "pfx": "193.0.20.0/23",
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
                    "rpki-valid-passed": True,
                    "rpki-invalid-passed": False
                },
                "date": "2019-08-27T00:00:00.000Z"
            },
            format='json'
        )

        self.assertEqual(
            Result.objects.ases_are_new_to_rov(asns=self.asn),
            True
        )


@override_settings(DEBUG=True)
class NullTestCaseCompatNew(APITestCase):
    fixtures = ['null-rov.json']
    asn = "24555"

    def test_3rd_party(self):
        """
        Some browsers won't fetch the resource behind rpki-invalid-passed, posting

        "rpki-valid-passed": true,
        "rpki-invalid-passed": null
        """

        self.client.post(
            path='/results/',
            data={
                "json": {
                    "ip": "190.216.137.66",
                      "asn": [
                        "3549"
                      ],
                      "pfx": "190.216.128.0/20",
                      "events": [
                        {
                          "data": {
                            "options": {
                              "enrich": True,
                              "postResult": True,
                              "invalidTimeout": 5000
                            },
                            "testUrls": [
                              {
                                "url": "https://d7ba9fed-c737-46d9-9f33-0d1f7bec2cec.rpki-valid-beacon.meerval.net/valid.json",
                                "addressFamily": 4
                              },
                              {
                                "url": "https://d7ba9fed-c737-46d9-9f33-0d1f7bec2cec.rpki-invalid-beacon.meerval.net/invalid.json",
                                "addressFamily": 4
                              }
                            ],
                            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36",
                            "startDateTime": "2019-11-08T15:25:27.403Z",
                            "originLocation": "https://www.lacnic.net/2398/3/lacnic/categorias-e-quotas-de-membresia"
                          },
                          "error": None,
                          "stage": "initialized",
                          "success": True
                        },
                        {
                          "data": {
                            "testUrl": "https://d7ba9fed-c737-46d9-9f33-0d1f7bec2cec.rpki-invalid-beacon.meerval.net/invalid.json",
                            "duration": 3752,
                            "addressFamily": 4,
                            "rpki-invalid-passed": False
                          },
                          "error": None,
                          "stage": "invalidReceived",
                          "success": False
                        },
                        {
                          "data": {
                            "ip": "190.216.137.66",
                            "testUrl": "https://d7ba9fed-c737-46d9-9f33-0d1f7bec2cec.rpki-valid-beacon.meerval.net/valid.json",
                            "duration": 3752,
                            "addressFamily": 4,
                            "rpki-valid-passed": True
                          },
                          "error": None,
                          "stage": "validReceived",
                          "success": True
                        },
                        {
                          "data": {
                            "ip": "190.216.137.66",
                            "asns": [
                              "3549"
                            ],
                            "prefix": "190.216.128.0/20",
                            "duration": 3921,
                            "enrichUrl": "https://stat.ripe.net/data/network-info/data.json?resource=190.216.137.66"
                          },
                          "error": None,
                          "stage": "enrichedReceived",
                          "success": True
                        }
                      ],
                      "lastError": None,
                      "lastStage": "enrichedReceived",
                      "lastErrorStage": None,
                      "rpki-valid-passed": True,
                      "rpki-invalid-passed": False
                    },
                    "date": "2019-08-27T00:00:00.000Z"
                },
            format='json'
        )

        self.assertEqual(
            Result.objects.ases_are_new_to_rov(asns=self.asn),
            False
        )

    def test_rov(self):

        self.client.post(
            path='/results/',
            data={
                "json": {
                    "asn": [self.asn],
                    "pfx": "193.0.20.0/23",
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
                    "rpki-valid-passed": True,
                    "rpki-invalid-passed": False
                },
                "date": "2019-08-27T00:00:00.000Z"
            },
            format='json'
        )

        self.assertEqual(
            Result.objects.ases_are_new_to_rov(asns=self.asn),
            True
        )

