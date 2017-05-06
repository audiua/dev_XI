from rest_framework import serializers
from voting import models


class CounsilSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Counsil
        fields = ['id', 'title', 'sessions', 'created', 'updated']


class CounsilSessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.CounsilSession
        fields = ['id', 'title', 'counsil', 'laws', 'created', 'updated']


class LawSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Law
        fields = ['id', 'text', 'session', 'law_file_name',
                  'resolution', 'voting_number', 'voting_result', 'name_voting', 'created', 'updated']


class DeputySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Deputy
        fields = ['id', 'name', 'law_voting', 'created', 'updated']

class LawVotingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.LawVoting
        fields = ['id', 'deputy', 'law', 'vote', 'created', 'updated']