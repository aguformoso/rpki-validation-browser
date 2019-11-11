from rest_framework import viewsets
from .serializers import ResultSerializer
from .models import Result
from .libs import MattermostClient, RipestatClient
from jsonschema import validate


class ResultView(viewsets.ModelViewSet):

    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    http_method_names = ['get', 'head', 'options', 'post']

    def create(self, request, *args, **kwargs):

        schema = {
            "type": "object",
            "properties": {
                "json": {
                    "type": "object"
                },
                # "date": {
                #     "type": "date-time"
                # }
            },
            "required": ["json"]  # "date"
        }

        validate(
            instance=request.data,
            schema=schema
        )

        schema = {
            "type": "object",
            "properties": {
                "asn": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "pfx": {
                    "type": "string"
                }
            },
            "required": ["asn", "pfx"]
        }

        validate(
            instance=request.data["json"],
            schema=schema
        )

        return super(ResultView, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Notify the rpki-smiley Mattermost channel on new ASes doing RPKI
        """

        super(ResultView, self).perform_create(serializer)

        asns = serializer.instance.json['asn']
        pfx = serializer.instance.json['pfx']

        # We're seeing this AS doing RPKI for the first time if
        # the new Result is_doing_rpki=true and there's
        # only 1 object in db (this one, has just been saved)

        new = serializer.instance.is_doing_rpki() and Result.objects.ases_are_new_to_rov(asns)

        if new:

            names = []
            for asn in asns:

                holder = RipestatClient().fetch_info(resource="AS{asn}".format(asn=asn))['data']['holder']
                names.append(
                    "[AS {asn}](https://stat.ripe.net/AS{asn}) ({holder})".format(
                        asn=asn,
                        holder=holder
                    )
                )

            msg = "{names} {verb} just been seen with rpki-valid=true, rpki-invalid=false, pfx={pfx}.".format(
                names=', '.join(names),
                verb='have' if len(names) > 1 else 'has',
                pfx="[{pfx}](https://stat.ripe.net/{pfx})".format(pfx=pfx)
            )

            # We've previously seen this ASNs not doing ROV
            if Result.objects.ases_have_been_seen_not_doing_rov(asns):

                last_result = Result.objects.results_seen_not_doing_rov(
                    ).filter(
                        json__asn__contains=asns
                    ).order_by('date').last()

                msg += " We saw {subject} previously not doing Route Origin Validation (last seen: {last_seen}).".format(
                    subject='them' if len(names) > 1 else 'it',
                    last_seen=last_result.date.strftime("%b %d %Y %H:%M:%S")
                )

            if 'events' in serializer.instance.json.keys():
                initialized = [x for x in serializer.instance.json['events'] if x["stage"] == "initialized"][0]
                if initialized["data"]["originLocation"].split('/')[2] != "sg-pub.ripe.net":
                    msg += " This result comes from a 3rd party site (not sg-pub.ripe.net)."

            MattermostClient().send_msg(msg=msg)

        # If any of the ASNs is part of the documentation range, then
        # don't persist, as it'll be used for testing
        # https://tools.ietf.org/html/rfc5398#section-4
        if any([Result.objects.is_documentation_asn(asn) for asn in asns]):
            serializer.instance.delete()


