from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework import viewsets
from .serializers import LawSerializer, CounsilSerializer, \
    CounsilSessionSerializer, DeputySerializer, LawVotingSerializer
from .models import Deputy, Counsil, CounsilSession, Law, LawVoting

class CounsilViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint counsil models
    """
    throttle_classes = (AnonRateThrottle, UserRateThrottle)
    queryset = Counsil.objects.all()
    serializer_class = CounsilSerializer

class CounsilSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint counsil_session models
    """
    throttle_classes = (AnonRateThrottle, UserRateThrottle)
    queryset = CounsilSession.objects.all()
    serializer_class = CounsilSessionSerializer


class DeputyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint deputy models
    """
    throttle_classes = (AnonRateThrottle, UserRateThrottle)
    queryset = Deputy.objects.all()
    serializer_class = DeputySerializer


class LawViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint law models
    """
    throttle_classes = (AnonRateThrottle, UserRateThrottle)
    queryset = Law.objects.all()
    serializer_class = LawSerializer

class LawVotingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint law models
    """
    throttle_classes = (AnonRateThrottle, UserRateThrottle)
    queryset = LawVoting.objects.all()
    serializer_class = LawVotingSerializer