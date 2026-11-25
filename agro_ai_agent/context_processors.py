from farms.models import Farm

def farm_context(request):
    if not request.user.is_authenticated:
        return {}
    farms = Farm.objects.filter(owner=request.user)
    # Prefer farm from URL kwarg, else first farm
    active_farm = None
    farm_id = request.resolver_match.kwargs.get('farm_id') or \
              request.resolver_match.kwargs.get('pk')
    if farm_id:
        active_farm = farms.filter(id=farm_id).first()
    if not active_farm:
        active_farm = farms.first()
    return {
        'active_farm': active_farm,
        'user_farms':  farms,
    }
