from django.shortcuts import render
from suggestions import models as sm
# Create your views here.
def test(request):
    abc = sm.TankRelation.objects.get(pk=1)
    res2 = abc.extract_stats_secondary()
    res1 = abc.extract_stats_primary()
    breakpoint()
    a = 5