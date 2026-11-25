from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Farm, CropHistory
from .forms import FarmForm, CropHistoryForm

@login_required
def farm_list(request):
    farms = Farm.objects.filter(owner=request.user, is_active=True)
    return render(request, 'farms/farm_list.html', {'farms': farms})

@login_required
def farm_add(request):
    form = FarmForm(request.POST or None)
    if form.is_valid():
        farm = form.save(commit=False)
        farm.owner = request.user
        farm.save()
        messages.success(request, f'Farm "{farm.name}" added successfully!')
        return redirect('farm_detail', pk=farm.pk)
    return render(request, 'farms/farm_form.html', {'form': form, 'title': 'Add New Farm'})

@login_required
def farm_edit(request, pk):
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    form = FarmForm(request.POST or None, instance=farm)
    if form.is_valid():
        form.save()
        messages.success(request, 'Farm updated successfully.')
        return redirect('farm_detail', pk=pk)
    return render(request, 'farms/farm_form.html', {
        'form': form, 'title': 'Edit Farm', 'farm': farm
    })

@login_required
def farm_delete(request, pk):
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    if request.method == 'POST':
        farm.is_active = False
        farm.save()
        messages.success(request, f'Farm "{farm.name}" removed.')
        return redirect('farm_list')
    return render(request, 'farms/farm_confirm_delete.html', {'farm': farm})

@login_required
def farm_detail(request, pk):
    farm    = get_object_or_404(Farm, pk=pk, owner=request.user)
    history = CropHistory.objects.filter(farm=farm)
    hist_form = CropHistoryForm(request.POST or None)
    if hist_form.is_valid():
        h = hist_form.save(commit=False)
        h.farm = farm
        h.save()
        messages.success(request, 'Crop history record added.')
        return redirect('farm_detail', pk=pk)
    soil_items = [
        ('Soil Type',  farm.get_soil_type_display()),
        ('pH',         farm.soil_ph),
        ('Nitrogen',   f'{farm.nitrogen} mg/kg'),
        ('Phosphorus', f'{farm.phosphorus} mg/kg'),
        ('Potassium',  f'{farm.potassium} mg/kg'),
        ('Size',       f'{farm.size_hectares} ha'),
        ('Irrigation', '✅ Yes' if farm.irrigation_available else '❌ No'),
        ('State',      farm.state),
    ]
    return render(request, 'farms/farm_detail.html', {
        'farm': farm, 'history': history,
        'hist_form': hist_form, 'soil_items': soil_items,
    })
