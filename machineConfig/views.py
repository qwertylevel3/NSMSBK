from django.shortcuts import render
from django.shortcuts import HttpResponse

# Create your views here.

def machineConfigSearch(request):
    return render(request,'machineConfig/machineConfigSearch.html')
