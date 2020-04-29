from django.db import models
from statparser import models as sm
from collections import defaultdict
import datetime, decimal, time

class TankRelation(models.Model):
    tank1 = models.ForeignKey(sm.Tank, related_name='%(class)s_primary', on_delete=models.CASCADE)
    tank2 = models.ForeignKey(sm.Tank, related_name='%(class)s_secondary',on_delete=models.CASCADE)
    tank1average = models.DecimalField(max_digits=6, decimal_places=5, default=0)
    tank2average = models.DecimalField(max_digits=6, decimal_places=5, default=0)
    playercount = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    
    def extract_stats_primary(self):
        start = time.process_time()
        tank1_stats = sm.UserStat.objects.filter(tank = self.tank1)
        tank2_stats = sm.UserStat.objects.filter(tank = self.tank2)
        primary_ids = set(tank1_stats.values_list('wg_user', flat=True))
        secondary_ids = set(tank2_stats.values_list('wg_user', flat=True))
        
        update_list = list(primary_ids.intersection(secondary_ids))
        
        filtered_tank1_stats = tank1_stats.filter(wg_user__in=update_list)
        filtered_tank2_stats = tank2_stats.filter(wg_user__in=update_list)
        
        primary_wrs = dict(map(lambda x: (x.wg_user_id, (x.wins/x.battles)), filtered_tank1_stats))
        secondary_wrs = dict(map(lambda x: (x.wg_user_id, (x.wins/x.battles)), filtered_tank2_stats))
        
        dd = defaultdict(list)
        for value in primary_wrs.items():
            dd[value[0]].append(value[1])
        for value in secondary_wrs.items():
            dd[value[0]].append(value[1])
        
        #kick out any items that don't have a matching pair
        final_list = list(dd.items())
        for idx, val in enumerate(final_list):
            if len(val[1]) != 2:
                final_list.pop(idx)
        print("time1")
        print(time.process_time() - start)
        return final_list

    def extract_stats_secondary(self):
        start = time.process_time()
        tank1_stats = sm.UserStat.objects.filter(tank = self.tank1)
        tank2_stats = sm.UserStat.objects.filter(tank = self.tank2)
        
        dd = defaultdict(list)
        for stat in tank1_stats:
            dd[stat.wg_user_id].append([stat.wins, stat.battles])
        for stat in tank2_stats:
            dd[stat.wg_user_id].append([stat.wins, stat.battles])
        
        #kick out any items that don't have a matching pair
        dict_list = list(dd.items())
        filtered_list = [i for i in dict_list if len(i[1]) == 2]
        print("time2")
        print(time.process_time() - start)
        return dict_list

    def update_edge(self):
        stats = self.extract_stats_primary()
        stats2 = self.extract_stats_secondary()
        self.playercount = len(stats)
        stats.sort(key=lambda x: x[1][0])
        self.ship1median = stats[round(self.playercount/2)][1][0]
        stats.sort(key=lambda x: x[1][1])
        self.ship2median = stats[round(self.playercount/2)][1][1]
        self.save()
        
    def get_edge(self):
        if datetime.datetime.now(datetime.timezone.utc) - self.updated_at > datetime.timedelta(days = 1):
            self.update_edge()
        #define this as the performance of players who have both ships vs
        #the performance of those who own either/or both ships, averaged between both nodes
        #must cast to decimal since ship1median is a float if generated, decimal if extracted from db
        perfratio = (decimal.Decimal(self.ship1median) / decimal.Decimal(self.ship_primary.median_wr) + decimal.Decimal(self.ship2median) / decimal.Decimal(self.ship_secondary.median_wr))/2
        return {
            'ship1median': self.ship1median,
            'ship2median': self.ship2median,
            'playercount': self.playercount,
            'source': self.ship_primary.pk,
            'target': self.ship_secondary.pk,
            'perfratio': perfratio
        }

