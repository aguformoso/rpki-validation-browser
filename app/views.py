from rest_framework import viewsets
from .serializers import ResultSerializer
from .models import Result
from .libs import MattermostClient, RipestatClient


class ResultView(viewsets.ModelViewSet):

    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    http_method_names = ['get', 'head', 'options', 'post']

    def perform_create(self, serializer):
        """
        Notify the rpki-smiley Mattermost channel on new ASes doing RPKI
        """

        super(ResultView, self).perform_create(serializer)

        # check if this is a new (rpki-valid=true, rpki-invalid=false, asns) tuple
        signal = {
            "rpki-valid-passed": True,
            "rpki-invalid-passed": False,
        }

        asns = serializer.instance.json['asns']
        pfx = serializer.instance.json['pfx']

        # there's a new AS doing RPKI if the new Result is_doing_rpki=true and there's
        # only 1 object in db (this one, has just been saved)

        new = serializer.instance.is_doing_rpki() and Result.objects.filter(
            json__contains=signal,
        ).filter(
            json__contains={"asns": asns}
        ).count() == 1

        if new:

            documentation_asn = []
            names = []
            for asn in asns.split(','):

                documentation_asn.append(64496 <= int(asn) <= 64511 or 65536 <= int(asn) <= 65551)

                holder = RipestatClient().fetch_info(resource="AS{asn}".format(asn=asn))['data']['holder']
                names.append(
                    "[AS {asn}](https://stat.ripe.net/AS{asn}) ({holder})".format(
                        asn=asn,
                        holder=holder
                    )
                )

            msg = "{names} {verb} just been seen with rpki-valid=true, rpki-invalid=false, pfx={pfx}".format(
                names=', '.join(names),
                verb='have' if len(names) > 1 else 'has',
                pfx="[{pfx}](https://stat.ripe.net/{pfx})".format(pfx=pfx)
            )

            MattermostClient().send_msg(msg=msg)

            # If any of the ASNs is part of the documentation range, then
            # don't persist, as it'll be used for testing
            # https://tools.ietf.org/html/rfc5398#section-4
            if any(documentation_asn):
                serializer.instance.delete()


