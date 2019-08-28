from django.test import TestCase
from rest_framework.test import APITestCase
from app.models import Result


# Create your tests here.

class ResultTestCase(TestCase):
    fixtures = ['no-rov.json']

    def test_add_rov_result(self):
        asn = "3333"

        self.assertTrue(Result.objects.ases_have_been_seen_not_doing_rov(asn))
        self.assertFalse(Result.objects.ases_have_been_seen_doing_rov(asn))
        self.assertEqual(Result.objects.results_seen_doing_rov().count(), 0)

        new = Result(
            json=Result.rov_signal
        )
        new.json.update({"asns": asn})
        new.save()

        # Test the new object is the only one seen doing ROV
        self.assertTrue(Result.objects.ases_are_new_to_rov(asn))

        # Results for this ASN still should report as have seen
        # not doing ROV (previous results)
        self.assertTrue(Result.objects.ases_have_been_seen_not_doing_rov(asn))

        # ...but also report doing ROV now (new result)
        self.assertTrue(Result.objects.ases_have_been_seen_doing_rov(asn))

        # The total amount is 1
        self.assertEqual(Result.objects.results_seen_doing_rov().count(), 1)


class ResultApiTestCase(APITestCase):
    fixtures = ['no-rov.json']

    def test_documentation_asn(self):

        self.assertEqual(Result.objects.count(), 2)

        documentation_asn = "64496"

        self.client.post(
            path='/results/',
            data={
                "json": {
                    "asns": documentation_asn,
                    "pfx": "193.0.20.0/23",
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
                    "rpki-valid-passed": True,
                    "rpki-invalid-passed": True
                },
                "date": "2019-08-27T00:00:00.000Z"},
            format='json'
        )

        self.assertEqual(Result.objects.count(), 2)
