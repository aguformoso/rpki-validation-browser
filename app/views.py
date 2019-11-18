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
                },
                "events": {
                    "type": "array"
                },
            },
            "required": ["asn", "pfx"]
        }

        __json = request.data["json"]
        validate(
            instance=__json,
            schema=schema
        )

        # Remove sensitive data we just don't want to store in our DB

        # Remove individual ip address
        if "ip" in __json.keys():
            del __json["ip"]

        # Track if the result finished on time ( t < 5000 )
        __json["finished-on-time"] = False

        # Strip out any trailing strings after /
        if "events" in __json.keys():
            events = __json["events"]

            initialized = [e for e in events if e["stage"] == "initialized"]
            invalid_blocked = [e for e in events if e["stage"] == "invalidBlocked"]
            invalid_received = [e for e in events if e["stage"] == "invalidReceived"]
            invalid_await = [e for e in events if e["stage"] == "invalidAwait"]
            valid_received = [e for e in events if e["stage"] == "validReceived"]
            enrich_received = [e for e in events if e["stage"] == "enrichedReceived"]

            if initialized:
                i = initialized[0]
                i["data"]["originLocation"] = i["data"]["originLocation"].split('/')[2]

            # Remove individual ip address stored in events array
            for ip_event in [e for e in events if "ip" in e["data"].keys()]:
                del ip_event["data"]["ip"]

            # Remove traces of IP in enrichedReceived event
            if enrich_received:
                enrich_received[0]['data']['enrichUrl'] = enrich_received[0]['data']['enrichUrl'].split('resource=')[0]

            # Remove URLs containing hashes
            if initialized:
                for o in initialized[0]['data']['testUrls']:
                    hash = o['url'].split('://')[1].split('.')[0]
                    o['url'] = o['url'].replace(hash, '')
                    del hash  # no trace of hash

            for event in [valid_received, invalid_received, invalid_await, invalid_blocked]:
                if not event:
                    continue
                event = event[0]

                hash = event['data']['testUrl'].split('://')[1].split('.')[0]
                event['data']['testUrl'] = event['data']['testUrl'].replace(hash, '')
                del hash  # no trace of hash

            # Flag this experiment as finished-on-time if
            # time to fetch valid < 5000
            # time to fetch invalid < 5000

            # ROV = True
            if invalid_blocked and valid_received:
                invalid_duration = invalid_blocked[0]["data"]["duration"]
                valid_duration = valid_received[0]["data"]["duration"]

                __json["finished-on-time"] = invalid_duration < 5000 and valid_duration < 5000

            # ROV = False
            elif invalid_received and valid_received:
                invalid_duration = invalid_received[0]["data"]["duration"]
                valid_duration = valid_received[0]["data"]["duration"]

                __json["finished-on-time"] = invalid_duration < 5000 and valid_duration < 5000

            else:
                # other cases are not considered to have finished-on-time
                pass

        return super(ResultView, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Notify the rpki-smiley Mattermost channel on new ASes doing RPKI
        """

        super(ResultView, self).perform_create(serializer)

        result = serializer.instance

        asns = result.json['asn']
        pfx = result.json['pfx']

        # We're seeing this AS doing RPKI for the first time if
        # the new Result is_doing_rpki=true and  it has finished on time
        # and there's only 1 object in db (this one, has just been saved)

        new = result.is_doing_rpki() and result.has_finished_ont_time() and Result.objects.ases_are_new_to_rov(asns)

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

            if 'events' in result.json.keys():
                initialized = [event for event in result.json['events'] if event["stage"] == "initialized"]
                if initialized and initialized[0]["data"]["originLocation"] != "sg-pub.ripe.net":
                    msg += " This result comes from a 3rd party site (not sg-pub.ripe.net)."

            MattermostClient().send_msg(msg=msg)

        # If any of the ASNs is part of the documentation range, then
        # don't persist, as it'll be used for testing
        # https://tools.ietf.org/html/rfc5398#section-4
        if any([Result.objects.is_documentation_asn(asn) for asn in asns]):
            result.delete()


