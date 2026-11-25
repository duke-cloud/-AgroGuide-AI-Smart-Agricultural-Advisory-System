"""
AgroGuide AI — Hybrid Rules Engine
Agronomic domain knowledge for Nigerian farming conditions.
"""

CROP_CALENDAR = {
    'maize':    {'wet1':(4,7),'wet2':(8,9)},
    'rice':     {'wet1':(5,8),'wet2':(9,10)},
    'cassava':  {'wet1':(3,6),'wet2':None},
    'yam':      {'wet1':(2,4),'wet2':None},
    'millet':   {'wet1':(6,8),'wet2':None},
    'sorghum':  {'wet1':(6,8),'wet2':None},
    'tomato':   {'wet1':(9,11),'wet2':None},
    'cowpea':   {'wet1':(4,7),'wet2':(8,10)},
    'groundnut':{'wet1':(5,7),'wet2':(8,9)},
    'soybean':  {'wet1':(5,7),'wet2':None},
}

FERTILIZER_RATES = {
    'maize':   {'N':120,'P':60,'K':60,'typical':'NPK 15-15-15 at 400 kg/ha + Urea 150 kg/ha top-dress'},
    'rice':    {'N':150,'P':75,'K':75,'typical':'NPK 20-10-10 at 300 kg/ha + Urea 150 kg/ha'},
    'cassava': {'N':60,'P':60,'K':120,'typical':'NPK 15-15-15 at 200 kg/ha'},
    'yam':     {'N':100,'P':80,'K':120,'typical':'NPK 15-15-15 at 400 kg/ha'},
    'tomato':  {'N':120,'P':100,'K':120,'typical':'NPK 15-15-15 at 400 kg/ha + CAN top-dress'},
    'default': {'N':80,'P':60,'K':80,'typical':'NPK 15-15-15 at 300 kg/ha'},
}

PEST_ADVICE = {
    'armyworm':           {'action':'Apply Cypermethrin or Chlorpyrifos early morning','prevention':'Scout at dawn; use pheromone traps'},
    'gray leaf spot':     {'action':'Apply Mancozeb or Propiconazole fungicide','prevention':'Plant resistant varieties; improve air circulation'},
    'stem borer':         {'action':'Apply Furadan granules in leaf whorl','prevention':'Destroy crop residues; early planting'},
    'late blight':        {'action':'Apply Ridomil Gold or Mancozeb immediately','prevention':'Use certified seed; avoid overhead irrigation'},
    'early blight':       {'action':'Apply Copper-based fungicide','prevention':'Remove infected leaves; practice crop rotation'},
    'aphids':             {'action':'Apply Imidacloprid 200SL or Neem extract','prevention':'Encourage ladybirds; avoid excess nitrogen'},
    'brown planthopper':  {'action':'Apply Malathion 50EC or Imidacloprid','prevention':'Balanced fertilization; resistant varieties'},
    'cassava mosaic virus':{'action':'Remove and destroy infected plants','prevention':'Use virus-free cuttings; control whitefly vector'},
    'low_risk':           {'action':'No immediate treatment needed','prevention':'Continue regular scouting every 3-4 days'},
}


def planting_advice(crop, rainfall, temperature, current_month):
    advice = []
    urgency = 'info'
    if crop == 'maize':
        if rainfall >= 50 and 20 <= temperature <= 32:
            advice.append('✅ Excellent conditions for maize planting.')
            urgency = 'success'
        elif rainfall < 30:
            advice.append('⚠️ Rainfall too low. Delay or irrigate first.')
            urgency = 'warning'
        elif temperature > 35:
            advice.append('⚠️ Temperature too high. Irrigate and plant early morning.')
            urgency = 'warning'
        else:
            advice.append('ℹ️ Borderline conditions. Monitor rainfall before planting.')
    elif crop == 'rice':
        if rainfall >= 100:
            advice.append('✅ Adequate rainfall for rice. Good time to plant.')
            urgency = 'success'
        elif rainfall >= 60:
            advice.append('⚠️ Marginal rainfall — consider irrigated lowland planting.')
            urgency = 'warning'
        else:
            advice.append('❌ Insufficient rainfall for rain-fed rice. Use irrigation or wait.')
            urgency = 'danger'
    elif crop == 'cassava':
        if temperature >= 22 and rainfall >= 30:
            advice.append('✅ Suitable conditions for cassava planting.')
            urgency = 'success'
        else:
            advice.append('⚠️ Cassava prefers warm temperatures and moderate rainfall.')
            urgency = 'warning'
    else:
        if rainfall >= 40 and temperature <= 38:
            advice.append(f'✅ Conditions are generally suitable for {crop} planting.')
            urgency = 'success'
        else:
            advice.append(f'⚠️ Check specific requirements for {crop} before planting.')
            urgency = 'warning'
    advice.append(f'📅 Best months in Nigeria for {crop.capitalize()}: April–July (Season 1), August–October (Season 2).')
    return {'messages': advice, 'urgency': urgency}


def fertilizer_advice(crop, N, P, K, ph, farm_size_ha):
    req   = FERTILIZER_RATES.get(crop, FERTILIZER_RATES['default'])
    recs  = []
    if ph < 5.5:
        recs.append({'product':'Agricultural Lime','rate_per_ha':'2,000 kg/ha',
            'total':f'{round(2000*farm_size_ha):,} kg',
            'timing':'2–4 weeks before planting, incorporate into soil',
            'reason':f'Soil pH ({ph}) too acidic — lime raises pH to optimal range'})
    if N < req['N'] * 0.6:
        ukg = round((req['N'] - N) * 2.17)
        recs.append({'product':'Urea (46-0-0)','rate_per_ha':f'{ukg} kg/ha',
            'total':f'{round(ukg*farm_size_ha)} kg',
            'timing':'1/3 at planting, 2/3 top-dress at 4–6 weeks',
            'reason':f'Nitrogen deficient (current: {N} | min required: {round(req["N"]*0.6)} mg/kg)'})
    if P < req['P'] * 0.6:
        pkg = round((req['P'] - P) * 5.5)
        recs.append({'product':'Single Super Phosphate (0-18-0)','rate_per_ha':f'{pkg} kg/ha',
            'total':f'{round(pkg*farm_size_ha)} kg',
            'timing':'All at planting (basal)',
            'reason':f'Phosphorus deficient (current: {P} | min: {round(req["P"]*0.6)} mg/kg)'})
    if K < req['K'] * 0.6:
        kkg = round((req['K'] - K) * 1.67)
        recs.append({'product':'Muriate of Potash (0-0-60)','rate_per_ha':f'{kkg} kg/ha',
            'total':f'{round(kkg*farm_size_ha)} kg',
            'timing':'50% basal, 50% at flowering',
            'reason':f'Potassium deficient (current: {K} | min: {round(req["K"]*0.6)} mg/kg)'})
    if not recs:
        recs.append({'product':'NPK 15-15-15 (maintenance)','rate_per_ha':'200 kg/ha',
            'total':f'{round(200*farm_size_ha)} kg',
            'timing':'Basal at planting',
            'reason':'Nutrient levels adequate — apply maintenance fertilizer only'})
    return recs, req['typical']


def weather_advisory(temp, humidity, rainfall, wind_speed=0, crop=None):
    advisories = []
    if humidity > 80 and temp > 25:
        advisories.append({'level':'danger','icon':'🦠',
            'msg':'Very high humidity + heat: HIGH fungal disease risk. Inspect crops immediately.'})
    elif humidity > 65:
        advisories.append({'level':'warning','icon':'💧',
            'msg':'Elevated humidity: Monitor for mold, blight, and leaf spots.'})
    if rainfall > 50:
        advisories.append({'level':'warning','icon':'🌧️',
            'msg':'Heavy rainfall: Do NOT apply pesticides or fertilizers — they will wash away.'})
    elif rainfall < 5 and humidity < 40:
        advisories.append({'level':'warning','icon':'☀️',
            'msg':'Dry conditions: Irrigate crops, especially at vegetative and flowering stages.'})
    if temp > 38:
        advisories.append({'level':'danger','icon':'🔥',
            'msg':'Extreme heat: Risk of heat stress. Irrigate early morning. Avoid midday fieldwork.'})
    elif temp < 15:
        advisories.append({'level':'info','icon':'❄️',
            'msg':'Cool temperatures: Growth will slow. Delay planting tropical crops.'})
    if wind_speed and wind_speed > 40:
        advisories.append({'level':'warning','icon':'💨',
            'msg':'High winds: Delay pesticide spraying. Support tall/fragile crops.'})
    if not advisories:
        advisories.append({'level':'success','icon':'✅',
            'msg':'Weather conditions are generally favourable for farm activities today.'})
    return advisories
