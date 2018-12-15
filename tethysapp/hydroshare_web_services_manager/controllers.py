from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests


@login_required()
def home(request):

    url = ''
    headers = {}
    #response = requests.get(url, headers=headers)

    context = {}

    return render(request, 'hydroshare_web_services_manager/home.html', context)