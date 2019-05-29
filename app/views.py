from rest_framework import viewsets
from .serializers import ResultSerializer
from .models import Result


class ResultView(viewsets.ModelViewSet):

    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    http_method_names = ['get', 'head', 'options', 'post']
