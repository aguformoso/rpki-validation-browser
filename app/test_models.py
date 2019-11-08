from django.test import TestCase
from rest_framework.test import APITestCase
from app.models import Result


class RpkiSmileyTestCase:
    """
    Holds all common info for test cases
    """
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) " \
                 "AppleWebKit/537.36 (KHTML, like Gecko) " \
                 "Chrome/75.0.3770.100 Safari/537.36"


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

