from django.core import serializers
from django.shortcuts import render
from django.http import JsonResponse
from suggestions import models as sm
from statparser import models as stm
import requests, os

def maintenance(request):
    # get all tank images
    tanks = stm.Tank.objects.all()
    for tank in tanks:
        response = requests.post(
            'https://api.worldoftanks.com/wot/encyclopedia/vehicles/',
            {
                'application_id': os.environ['APP_ID'],
                'fields': 'images',
                'tank_id': tank.wg_identifier
            }
        ).json()['data']
        tank.img = response[str(tank.wg_identifier)]['images']['big_icon']
        tank.save()
 
def explore(request):
    nations = stm.Nation.objects.all()
    tanks = stm.Tank.objects.all()
    return render(request, 'suggestions/explorer.html', { 'nations': nations, 'tanks': tanks })
    
def root_tank(request):
    nodes = []
    links = []
    nodes.append(stm.Tank.objects.get(pk=1).get_node())
    jsondata = { 'nodes': nodes, 'links': links }
    return JsonResponse(jsondata, safe=False)

def improve_tank(request):
    base_tank = stm.Tank.objects.get(pk = int(request.GET['tank']))
    
    