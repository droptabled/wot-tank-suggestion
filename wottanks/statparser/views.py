from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.db import models, transaction, connection
from .models import User, UserStat, Tank, Nation, TankType
from datetime import datetime
import requests, pytz, os, sys, concurrent.futures

def parse(wg_id, username):
    wg_id = str(wg_id)
    response = requests.post(
        'https://api.worldoftanks.com/wot/tanks/stats/',
        { 
            'application_id': os.environ['APP_ID'],
            'account_id': wg_id,
            'extra': 'random',
            'fields': 'tank_id, random'
        }
    )
    if response.status_code == 200:
        try:
            user_data = response.json()['data'][wg_id]
        except KeyError:
            return 'Sorry, account is marked as private'
        
        user, created = User.objects.get_or_create(wg_user = wg_id, name = username)
        
        # only update if the last updated was less than an hour ago
        if created is False and (datetime.now(tz = pytz.utc) - user.updated_at).seconds < 3600:
            return 'Sorry, wait at least 1 hour before requesting a refresh'
        
        # stop if no user found or has no PVP stats
        if user_data is None:
            user.delete()
            return 'Sorry, user has not played any games'
        
        # exclude users that don't have enough ships for comparison purposes
        if len(user_data) < 10:
            user.delete()
            return 'Sorry, user has not played enough different tanks'

        tanks = []
        for tank_stat in user_data:
            if (int(tank_stat['random']['battles'])) > 50:
                # find the tank in the tanks db. if not found, update the db
                try:
                    tank = Tank.objects.get(wg_identifier = tank_stat['tank_id'])
                except Tank.DoesNotExist:
                    name_response = requests.post(
                        'https://api.worldoftanks.com/wot/encyclopedia/vehicles/',
                        {
                            'application_id': os.environ['APP_ID'],
                            'tank_id': tank_stat['tank_id']
                        }
                    ).json()['data']
                    if name_response[str(tank_stat['tank_id'])] is not None:
                        tank_json = name_response[str(tank_stat['tank_id'])]
                        nation = Nation.objects.get_or_create(name = tank_json['nation'])[0]
                        type = TankType.objects.get_or_create(name = tank_json['type'])[0]
                        tank = Tank.objects.create(
                            wg_identifier = tank_stat['tank_id'],
                            name = tank_json['name'],
                            tier = tank_json['tier'],
                            nation = nation,
                            type = type,
                            is_premium = tank_json['is_premium']
                        )
                finally:
                    tanks.append(
                        UserStat(
                            wg_user = user,
                            tank = tank,
                            spotted = tank_stat['random']['spotted'],
                            survived_battles = tank_stat['random']['survived_battles'],
                            hits_percents = tank_stat['random']['hits_percents'],
                            battles = tank_stat['random']['battles'],
                            damage_received = tank_stat['random']['damage_received'],
                            frags = tank_stat['random']['frags'],
                            stun_number = tank_stat['random']['stun_number'],
                            capture_points = tank_stat['random']['capture_points'],
                            hits = tank_stat['random']['hits'],
                            wins = tank_stat['random']['wins'],
                            damage_dealt = tank_stat['random']['damage_dealt']
                        )
                    )
        
        if len(tanks) < 2:
            user.delete()
            return 'Sorry, user has not played enough tanks over 50 games'
            
        UserStat.objects.bulk_create(tanks)
        return 'Done, updated ' + str(len(tanks)) + ' rows'
    else:
        return 'Something went wrong with the server'

def scrapestart(request):
    return render(request, 'statparser/scrapestart.html')

def nextname(name):
    character_set = 'abcdefghijklmnopqrstuvwxyz0123456789_'
    for idx, char in enumerate(name[::-1], start = 1):
        if char != '_':
             break
    next_name = name[:-idx] + character_set[character_set.find(name[-idx]) + 1]
    return next_name.ljust(3,'a')

def scrapeall(request):
    name_start = request.POST['name_start']

    while name_start != '________________':
        try:
            name_data = requests.post(
                'https://api.worldoftanks.com/wot/account/list/',
                {
                    'application_id': os.environ['APP_ID'],
                    'search': name_start
                }
            ).json()['data']
        except Exception as e:
            print(str(e))
            pass
        # if no names are found, move onto the next character
        if name_data == None:
            name_start = nextname(name_start)
            continue
        # if 100 names are found (max returned by wg), increase specificity 
        if len(name_data) == 100:
            name_start = name_start + 'a'
        # if less than 100 names are found, move onto the next character
        else:
            name_start = nextname(name_start)
        
        # wg doesn't allow concurrent requests for client apps so this is temporarily out
        # iterate through the names found
        # def worker(name):
        #    print("Account: " + name['nickname'] + " Result:" + parse(name['account_id'], name['nickname']), file = sys.stderr)

        #pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        for name in name_data:
            #pool.submit(worker, (name))
            try:
                print("Account: " + name['nickname'] + " Result:" + parse(name['account_id'], name['nickname']), file = sys.stderr)
            except Exception as e:
                print(e)

    return HttpResponse("Placeholder")
