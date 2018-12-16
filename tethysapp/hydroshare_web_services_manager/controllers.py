from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests


@login_required()
def home(request):
	#914bf4757ebf49f3abd4f4097e6e7150
	#1f9c71a9cee34420a7ffb739505b2b16
    #url = 'http://127.0.0.1:8080/apps/hydroshare-web-services-manager/api/update-services/?res_id=1f9c71a9cee34420a7ffb739505b2b16'
    #headers = {'Authorization': 'Token 932aebc70b5924dd31da63f8d80e7c62db18c02c'}
    #response = requests.post(url, headers=headers)

    context = {}

    return render(request, 'hydroshare_web_services_manager/home.html', context)