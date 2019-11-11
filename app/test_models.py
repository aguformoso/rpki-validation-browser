from django.test import TestCase, override_settings
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
    asn = ["3333"]

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
