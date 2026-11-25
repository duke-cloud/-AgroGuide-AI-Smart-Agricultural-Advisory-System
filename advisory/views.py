import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from farms.models import Farm
from .ml_engine import predict_crop, predict_yield, predict_pest, predict_fertilizer
from .rules_engine import planting_advice, fertilizer_advice, weather_advisory
from .weather_service import get_weather, get_forecast
from .models import AdvisoryRequest, ChatMessage

# ── CROP ADVISORY ─────────────────────────────────────────────────────────────
@login_required
def crop_advisory(request, farm_id):
    farm    = get_object_or_404(Farm, id=farm_id, owner=request.user)
    weather = get_weather(farm.latitude, farm.longitude)
    context = {'farm': farm, 'weather': weather, 'page': 'crop'}
    if request.method == 'POST':
        data = json.loads(request.body)
        N    = float(data.get('N',    farm.nitrogen))
        P    = float(data.get('P',    farm.phosphorus))
        K    = float(data.get('K',    farm.potassium))
        temp = float(data.get('temperature', weather['temp']))
        hum  = float(data.get('humidity',    weather['humidity']))
        ph   = float(data.get('ph',          farm.soil_ph))
        rain = float(data.get('rainfall',    weather['rainfall_1h']))

        primary, top3, probs = predict_crop(N, P, K, temp, hum, ph, rain)
        from datetime import date
        plant = planting_advice(primary, rain, temp, date.today().month)

        result = {
            'primary_crop': primary,
            'top3_crops': top3,
            'probabilities': {c: probs.get(c,0) for c in top3},
            'planting_advice': plant,
        }
        AdvisoryRequest.objects.create(
            farmer=request.user, farm=farm, advisory_type='crop',
            input_data={'N':N,'P':P,'K':K,'temperature':temp,'humidity':hum,'ph':ph,'rainfall':rain},
            result_data=result
        )
        return JsonResponse({'status':'ok', 'result': result})
    return render(request, 'advisory/crop_advisory.html', context)

# ── FERTILIZER ADVISORY ───────────────────────────────────────────────────────
@login_required
def fertilizer_advisory(request, farm_id):
    farm = get_object_or_404(Farm, id=farm_id, owner=request.user)
    context = {'farm': farm, 'page': 'fertilizer'}
    if request.method == 'POST':
        data  = json.loads(request.body)
        crop  = data.get('crop', 'maize')
        N     = float(data.get('N',    farm.nitrogen))
        P     = float(data.get('P',    farm.phosphorus))
        K     = float(data.get('K',    farm.potassium))
        ph    = float(data.get('ph',   farm.soil_ph))
        stage = int(data.get('growth_stage', 0))
        area  = float(data.get('area', farm.size_hectares))

        ml_fert, conf = predict_fertilizer(crop, N, P, K, ph, stage)
        rule_recs, typical = fertilizer_advice(crop, N, P, K, ph, area)

        result = {
            'ml_recommendation': ml_fert,
            'ml_confidence': conf,
            'rule_recommendations': rule_recs,
            'typical_program': typical,
        }
        AdvisoryRequest.objects.create(
            farmer=request.user, farm=farm, advisory_type='fertilizer',
            input_data={'crop':crop,'N':N,'P':P,'K':K,'ph':ph,'stage':stage,'area':area},
            result_data=result
        )
        return JsonResponse({'status':'ok', 'result': result})
    return render(request, 'advisory/fertilizer_advisory.html', context)

# ── YIELD PREDICTION ─────────────────────────────────────────────────────────
@login_required
def yield_prediction(request, farm_id):
    farm = get_object_or_404(Farm, id=farm_id, owner=request.user)
    context = {'farm': farm, 'page': 'yield'}
    if request.method == 'POST':
        data    = json.loads(request.body)
        crop    = data.get('crop', 'maize')
        area    = float(data.get('area',  farm.size_hectares))
        rain    = float(data.get('rainfall', 80))
        temp    = float(data.get('temperature', 28))
        fert_lv = int(data.get('fertilizer_level', 2))
        soil_q  = int(data.get('soil_quality', 2))
        irrig   = bool(data.get('irrigation', farm.irrigation_available))

        yph, total = predict_yield(crop, area, rain, temp, fert_lv, soil_q, irrig)

        PRICES = {'maize':85000,'rice':120000,'cassava':45000,'yam':150000,
                  'tomato':200000,'millet':60000,'sorghum':65000,
                  'cowpea':180000,'groundnut':160000,'soybean':140000}
        price   = PRICES.get(crop, 100000)
        revenue = round(total * price)

        result = {'crop':crop,'area':area,'yield_per_ha':yph,'total_yield':total,
                  'est_revenue_ngn': revenue, 'price_per_ton': price}
        AdvisoryRequest.objects.create(
            farmer=request.user, farm=farm, advisory_type='yield',
            input_data=data, result_data=result
        )
        return JsonResponse({'status':'ok', 'result': result})
    return render(request, 'advisory/yield_prediction.html', context)

# ── PEST ADVISORY ─────────────────────────────────────────────────────────────
@login_required
def pest_advisory(request, farm_id):
    farm    = get_object_or_404(Farm, id=farm_id, owner=request.user)
    weather = get_weather(farm.latitude, farm.longitude)
    context = {'farm': farm, 'weather': weather, 'page': 'pest'}
    if request.method == 'POST':
        from .rules_engine import PEST_ADVICE
        data  = json.loads(request.body)
        crop  = data.get('crop', 'maize')
        temp  = float(data.get('temperature', weather['temp']))
        hum   = float(data.get('humidity',    weather['humidity']))
        rain  = float(data.get('rainfall',    weather['rainfall_1h']))
        stage = int(data.get('growth_stage',  2))

        risks = predict_pest(crop, temp, hum, rain, stage)
        for r in risks:
            key = r['pest'].lower().replace(' ','_')
            advice = PEST_ADVICE.get(key, PEST_ADVICE.get('low_risk'))
            r['action']     = advice['action']
            r['prevention'] = advice['prevention']
        w_adv = weather_advisory(temp, hum, rain, weather.get('wind_speed',0), crop)

        result = {'risks': risks, 'weather_advisories': w_adv}
        AdvisoryRequest.objects.create(
            farmer=request.user, farm=farm, advisory_type='pest',
            input_data=data, result_data=result
        )
        return JsonResponse({'status':'ok', 'result': result})
    return render(request, 'advisory/pest_advisory.html', context)

# ── WEATHER ADVISORY ─────────────────────────────────────────────────────────
@login_required
def weather_advisory_view(request, farm_id):
    farm     = get_object_or_404(Farm, id=farm_id, owner=request.user)
    weather  = get_weather(farm.latitude, farm.longitude)
    forecast = get_forecast(farm.latitude, farm.longitude)
    advisories = weather_advisory(
        weather['temp'], weather['humidity'],
        weather['rainfall_1h'], weather.get('wind_speed', 0)
    )
    weather_stats = [
        ('Humidity', f"{weather['humidity']}%"),
        ('Rainfall', f"{weather['rainfall_1h']}mm"),
        ('Wind', f"{weather.get('wind_speed',0)} km/h"),
        ('Pressure', f"{weather.get('pressure',1013)} hPa"),
    ]
    context = {
        'farm': farm, 'weather': weather,
        'forecast': forecast, 'advisories': advisories,
        'forecast_json': json.dumps(forecast),
        'weather_stats': weather_stats,
        'page': 'weather'
    }
    return render(request, 'advisory/weather_advisory.html', context)

# ── CHAT ASSISTANT ─────────────────────────────────────────────────────────────
@login_required
def chat_assistant(request, farm_id):
    farm     = get_object_or_404(Farm, id=farm_id, owner=request.user)
    history  = ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:20]
    quick_questions = [
        'What crop should I plant this season?',
        'What fertilizer is best for my soil?',
        'How do I control armyworm?',
        'Should I irrigate today?',
        'What are current crop prices?',
        "My maize leaves are yellowing — what is wrong?",
    ]
    context  = {'farm': farm, 'history': reversed(list(history)), 'page': 'chat', 'quick_questions': quick_questions}
    return render(request, 'advisory/chat_assistant.html', context)

@login_required
@require_POST
def chat_api(request, farm_id):
    farm    = get_object_or_404(Farm, id=farm_id, owner=request.user)
    data    = json.loads(request.body)
    message = data.get('message','').strip()
    if not message:
        return JsonResponse({'error':'Empty message'}, status=400)

    ChatMessage.objects.create(user=request.user, role='user', content=message)
    reply = _rule_based_chat(message, farm, request.user)
    ChatMessage.objects.create(user=request.user, role='assistant', content=reply)
    return JsonResponse({'reply': reply})

def _rule_based_chat(message, farm, user):
    """Intelligent rule-based chatbot with farm context awareness."""
    msg = message.lower()
    name = user.first_name or user.username

    # Crop recommendation triggers
    if any(w in msg for w in ['what crop','which crop','plant','grow','recommend crop']):
        from .ml_engine import predict_crop
        p, top3, _ = predict_crop(farm.nitrogen, farm.phosphorus, farm.potassium, 30, 65, farm.soil_ph, 80)
        return (f"Based on your farm's soil data (N={farm.nitrogen}, P={farm.phosphorus}, "
                f"K={farm.potassium}, pH={farm.soil_ph}), I recommend:\n\n"
                f"🌾 **Primary:** {p.capitalize()}\n"
                f"🌱 **Alternatives:** {', '.join(top3[1:])}\n\n"
                f"Your {farm.soil_type} soil in {farm.state} is well-suited for {p}. "
                f"Use the Crop Advisory tool for detailed planting windows and soil inputs.")

    if any(w in msg for w in ['fertilizer','npk','urea','nutrient']):
        from .rules_engine import FERTILIZER_RATES
        return (f"For {farm.soil_type} soil with N={farm.nitrogen}, P={farm.phosphorus}, K={farm.potassium}:\n\n"
                f"📦 Typical program: NPK 15-15-15 at 300–400 kg/ha at planting\n"
                f"📦 Top-dress with Urea (46%) at 4–6 weeks after germination\n"
                f"💡 Since your pH is {farm.soil_ph}, {'apply Agricultural Lime first.' if farm.soil_ph < 5.5 else 'pH is in good range.'}\n\n"
                f"Open the Fertilizer Advisory for exact quantities per hectare.")

    if any(w in msg for w in ['pest','disease','insect','blight','armyworm','worm','yellow','leaf']):
        return (f"Common pests in your region ({farm.state}) include:\n\n"
                f"🦟 Armyworm — Scout at dawn, apply Chlorpyrifos or Cypermethrin\n"
                f"🍃 Stem Borer — Use Furadan granules in leaf whorl\n"
                f"🍄 Late Blight (high humidity) — Apply Mancozeb fungicide\n"
                f"🐛 Aphids — Spray Neem extract or Imidacloprid\n\n"
                f"Open Pest & Disease Advisory for a risk assessment based on today's weather.")

    if any(w in msg for w in ['weather','rain','temperature','forecast','irrigat']):
        from .weather_service import get_weather
        wx = get_weather(farm.latitude, farm.longitude)
        return (f"Current weather at {farm.name}:\n\n"
                f"🌡️ Temperature: {wx['temp']}°C (feels like {wx['feels_like']}°C)\n"
                f"💧 Humidity: {wx['humidity']}%\n"
                f"🌧️ Rainfall: {wx['rainfall_1h']}mm\n"
                f"💨 Wind: {wx['wind_speed']} km/h\n"
                f"{'⚠️ High humidity — watch for fungal disease.' if wx['humidity'] > 70 else '✅ Conditions are generally favourable today.'}\n\n"
                f"See the full 7-day forecast in the Weather Advisory module.")

    if any(w in msg for w in ['yield','harvest','produce','output','ton']):
        from .ml_engine import predict_yield
        yph, total = predict_yield('maize', farm.size_hectares, 80, 28, 2, 2, farm.irrigation_available)
        return (f"Based on your farm data ({farm.size_hectares} ha, {farm.soil_type} soil):\n\n"
                f"🌾 Estimated maize yield: {yph} tons/hectare\n"
                f"📦 Total expected harvest: {total} tons\n"
                f"💰 Est. revenue: ₦{round(total * 85000):,} (at ₦85,000/ton)\n\n"
                f"Open the Yield Prediction module to model other crops and conditions.")

    if any(w in msg for w in ['hello','hi','good morning','good afternoon','good evening','hey']):
        return (f"Hello {name}! 👋 I'm AgroGuide AI, your smart farming assistant.\n\n"
                f"I can help you with:\n"
                f"🌱 Crop recommendations for {farm.state}\n"
                f"🧪 Fertilizer plans for your {farm.soil_type} soil\n"
                f"🦟 Pest & disease risk alerts\n"
                f"📊 Yield prediction\n"
                f"🌤️ Weather-based farm advisories\n\n"
                f"What would you like help with today?")

    if any(w in msg for w in ['price','market','sell','money','revenue']):
        return ("Current crop price estimates in Nigerian markets:\n\n"
                "🌽 Maize: ₦85,000 – ₦100,000/ton\n"
                "🌾 Rice: ₦120,000 – ₦145,000/ton\n"
                "🍠 Cassava: ₦40,000 – ₦55,000/ton\n"
                "🥔 Yam: ₦140,000 – ₦180,000/ton\n"
                "🍅 Tomato: ₦180,000 – ₦250,000/ton\n\n"
                "💡 Tip: Prices are highest at the start of dry season (Nov–Jan). "
                "Consider storage or cooperative marketing.")

    # Default
    return (f"I understand you're asking about: '{message[:60]}'\n\n"
            f"As your farm advisor for {farm.name} in {farm.state}, I can help with:\n"
            f"• Crop selection and planting windows\n"
            f"• Fertilizer recommendations and soil management\n"
            f"• Pest and disease identification\n"
            f"• Yield estimation and market prices\n"
            f"• Weather-based farming advice\n\n"
            f"Try asking: 'What should I plant?' or 'What fertilizer do I need?' or 'How do I treat armyworm?'")
