import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from farms.models import Farm
from .models import DiseaseReport
from advisory.rules_engine import PEST_ADVICE

SYMPTOM_RULES = {
    ('yellow','maize'):    ('Gray Leaf Spot', 'Medium', 'Apply Mancozeb fungicide; remove infected leaves'),
    ('hole','maize'):      ('Stem Borer', 'High',   'Apply Furadan granules in leaf whorl immediately'),
    ('wilt','tomato'):     ('Fusarium Wilt', 'High', 'Remove infected plants; improve drainage; rotate crops'),
    ('spot','tomato'):     ('Early Blight', 'Medium','Apply Copper fungicide; remove lower leaves'),
    ('mosaic','cassava'):  ('Cassava Mosaic Virus', 'High', 'Destroy infected plants; use virus-free cuttings'),
    ('rot','yam'):         ('Yam Storage Rot', 'Medium', 'Improve ventilation; apply wood ash to cuts'),
    ('stripe','rice'):     ('Rice Blast', 'High',   'Apply Tricyclazole fungicide; drain field temporarily'),
    ('aphid',''):          ('Aphid Infestation', 'Medium', 'Apply Neem oil or Imidacloprid spray'),
    ('worm',''):           ('Caterpillar/Worm', 'High',   'Apply Chlorpyrifos or Cypermethrin early morning'),
}

def diagnose_symptoms(symptoms, crop):
    sym = symptoms.lower()
    best = None
    for (keyword, crop_hint), result in SYMPTOM_RULES.items():
        if keyword in sym and (not crop_hint or crop_hint in crop.lower()):
            best = result
            break
    if not best:
        if 'yellow' in sym:
            best = ('Nutrient Deficiency / Early Disease', 'Low-Medium', 'Check soil nutrients; apply foliar fertilizer; monitor closely')
        elif 'brown' in sym or 'dark' in sym:
            best = ('Fungal Infection', 'Medium', 'Apply broad-spectrum fungicide (Mancozeb); improve air circulation')
        else:
            best = ('Unknown — Manual Inspection Needed', 'Unknown', 'Consult local agricultural extension officer; take a sample for laboratory testing')
    return {'diagnosis': best[0], 'severity': best[1], 'treatment': best[2]}

@login_required
def diagnosis_view(request, farm_id):
    farm = get_object_or_404(Farm, id=farm_id, owner=request.user)
    reports = DiseaseReport.objects.filter(farm=farm)
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        data     = json.loads(request.body)
        symptoms = data.get('symptoms','')
        crop     = data.get('crop', farm.name)
        result   = diagnose_symptoms(symptoms, crop)
        DiseaseReport.objects.create(
            farmer=request.user, farm=farm, crop=crop, symptoms=symptoms,
            diagnosis=result['diagnosis'], severity=result['severity'], treatment=result['treatment']
        )
        return JsonResponse({'status':'ok', 'result': result})
    common_signs = [
        ('Yellow leaves','Nitrogen deficiency or early fungal infection'),
        ('Brown spots on leaves','Fungal blight — apply fungicide'),
        ('Wilting at midday','Root rot, drought stress, or Fusarium wilt'),
        ('Holes in leaves','Caterpillars, beetles, or grasshoppers'),
        ('White powder on leaves','Powdery mildew — apply Sulphur fungicide'),
        ('Mosaic/mottled pattern','Viral infection — remove and destroy plants'),
        ('Stem tunneling','Stem borer — apply Furadan granules'),
        ('Root galls/knots','Root-knot nematode — crop rotation needed'),
    ]
    return render(request, 'disease/diagnosis.html', {'farm': farm, 'reports': reports, 'common_signs': common_signs})
