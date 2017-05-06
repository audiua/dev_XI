from django.shortcuts import render
from django.core.signals import request_finished
from django.dispatch import receiver
import django.dispatch

def index(request):
    return render(request, 'voting/index.html', {})