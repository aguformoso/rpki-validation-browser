from rest_framework import viewsets
from .serializers import ResultSerializer
from .models import Result
from .libs import MattermostClient


class ResultView(viewsets.ModelViewSet):

    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    http_method_names = ['get', 'head', 'options', 'post']

    def perform_create(self, serializer):
        super(ResultView, self).perform_create(serializer)

        # check if this is a new (rpki-valid=true, rpki-invalid=false, asns) tuple
        signal = {
            "rpki-valid-passed": True,
            "rpki-invalid-passed": False,
        }

        asns = serializer.instance.json['asns']

        # there's a new AS doing RPKI if the new Result is_doing_rpki=true and there's
        # only 1 object in db (this one, has just been saved)

        new = serializer.instance.is_doing_rpki() and Result.objects.filter(
            json__contains=signal,
        ).filter(
            json__contains={"asns": asns}
        ).count() == 1

        if new:
            msg = "{asns} {verb} just been seen with rpki-valid=true, rpki-invalid=false".format(
                asns=asns,
                verb='have' if ',' in asns else 'has'
            )

            MattermostClient().send_msg(msg=msg)
