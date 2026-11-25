import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from farms.models import Farm
from advisory.models import AdvisoryRequest

@login_required
def dashboard(request):
    farms     = Farm.objects.filter(owner=request.user)
    if not farms.exists():
        return redirect('farm_add')
    farm      = farms.first()
    advisories = AdvisoryRequest.objects.filter(farmer=request.user).order_by('-created_at')[:10]
    stats = {
        'total_farms':     farms.count(),
        'total_advisories': AdvisoryRequest.objects.filter(farmer=request.user).count(),
        'crop_count':      AdvisoryRequest.objects.filter(farmer=request.user, advisory_type='crop').count(),
        'pest_count':      AdvisoryRequest.objects.filter(farmer=request.user, advisory_type='pest').count(),
    }
    return render(request, 'reports/dashboard.html', {
        'farms': farms, 'farm': farm,
        'advisories': advisories, 'stats': stats,
    })

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')
