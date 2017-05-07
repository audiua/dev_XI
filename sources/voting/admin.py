from django.contrib import admin
from .models import *


@admin.register(Counsil)
class CounsilAdmin(admin.ModelAdmin):
    fields = ['title']
    list_display = ['id', 'title']


@admin.register(CounsilSession)
class CounsilSessionAdmin(admin.ModelAdmin):
    fields = ['title', 'counsil', 'from_date', 'number', 'voting_result_file']
    raw_id_fields = ['counsil']
    list_display = ['id', 'title', 'counsil', 'from_date', 'number', 'voting_result_file']


@admin.register(Law)
class LawAdmin(admin.ModelAdmin):
    fields = ['text', 'session', 'voting_result', 'resolution', 'voting_number', 'law_file_name']
    raw_id_fields = ['session']
    list_display = ['id', 'text', 'session', 'voting_result', 'resolution', 'voting_number', 'law_file_name']


@admin.register(Deputy)
class DeputyAdmin(admin.ModelAdmin):
    fields = ['name', 'counsil']
    raw_id_fields = ['counsil']
    list_display = ['id', 'name', 'counsil']


@admin.register(LawVoting)
class LawVotingAdmin(admin.ModelAdmin):
    fields = ['law', 'deputy', 'vote']
    raw_id_fields = ['law', 'deputy']
    list_display = ['id', 'law', 'deputy', 'vote']
