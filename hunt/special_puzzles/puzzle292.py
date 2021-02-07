import numpy as np
from random import random
from math import sqrt

from django.http import JsonResponse

from spoilr.decorators import *

# Random Hall


def uniform(a,b):
    return random()*(b-a)+a
def normal(a,b):
    return np.random.normal(a,sqrt(b))

def get_nums():
    dresscode_1 = uniform(4,7)
    dresscode_2 = uniform(2,4)
    giant_growth_1 = np.random.exponential(1/2.)
    giant_growth_2 = np.random.exponential(1/6.)
    product_testing = np.random.beta(4,1)
    xbox = np.random.chisquare(1)
    xbox2 = np.random.chisquare(3)
    sole_men = np.random.poisson(4)
    sole_men2 = np.random.poisson(8)
    sole_men3 = np.random.poisson(1)
    conventional = normal(4, 3)
    conventional2 = normal(5, 6)

    return [product_testing, conventional, dresscode_1, conventional2, dresscode_2, giant_growth_1, conventional, conventional2, xbox, sole_men, dresscode_2, product_testing, dresscode_1, sole_men2, giant_growth_2, xbox2, sole_men3]

@require_puzzle_access
def puzzle292_view(request):
    count = request.GET.get('count', '1')
    try:
        count = int(count)
    except:
        count = 1
    datas = ["That's too much!"]
    if count < 10000:
        datas = ["\t".join(f"{x:.3f}" for x in get_nums()) for i in range(count)]
    return JsonResponse(datas, safe=False)
