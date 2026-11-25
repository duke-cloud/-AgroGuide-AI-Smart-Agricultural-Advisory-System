#!/usr/bin/env python3
"""
AgroGuide AI — Synthetic Dataset Generator
Generates training data for all 4 ML models.
Run: python datasets/generate_datasets.py
"""
import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)
OUT = Path(__file__).parent

CROPS = ['maize','rice','cassava','yam','millet','sorghum','tomato','cowpea','groundnut','soybean']

# ── 1. Crop Recommendation (2200 rows) ───────────────────────────────────────
crop_ranges = {
    'rice':      dict(N=(60,110),P=(40,80),K=(35,70),temp=(22,32),hum=(70,95),ph=(5.0,7.0),rain=(100,250)),
    'maize':     dict(N=(30,100),P=(20,60),K=(20,70),temp=(18,32),hum=(45,80),ph=(5.5,7.5),rain=(50,200)),
    'cassava':   dict(N=(10,50), P=(10,45),K=(40,90),temp=(22,35),hum=(40,75),ph=(5.0,7.0),rain=(20,100)),
    'yam':       dict(N=(30,80), P=(30,70),K=(50,100),temp=(25,35),hum=(55,85),ph=(5.0,7.5),rain=(60,160)),
    'millet':    dict(N=(10,50), P=(10,40),K=(10,50),temp=(25,40),hum=(20,55),ph=(5.5,8.0),rain=(10,70)),
    'sorghum':   dict(N=(15,60), P=(10,50),K=(15,55),temp=(23,38),hum=(25,60),ph=(5.5,8.0),rain=(15,90)),
    'tomato':    dict(N=(50,100),P=(40,80),K=(40,80),temp=(18,28),hum=(55,80),ph=(6.0,7.0),rain=(40,130)),
    'cowpea':    dict(N=(10,40), P=(15,50),K=(15,45),temp=(22,35),hum=(40,75),ph=(5.5,7.5),rain=(40,120)),
    'groundnut': dict(N=(15,55), P=(20,60),K=(20,60),temp=(22,35),hum=(40,75),ph=(5.5,7.0),rain=(50,150)),
    'soybean':   dict(N=(20,70), P=(25,65),K=(20,65),temp=(20,35),hum=(40,80),ph=(6.0,7.5),rain=(50,180)),
}
rows = []
for _ in range(2200):
    c  = np.random.choice(CROPS)
    r  = crop_ranges[c]
    rows.append({
        'N':           round(np.random.uniform(*r['N']),1),
        'P':           round(np.random.uniform(*r['P']),1),
        'K':           round(np.random.uniform(*r['K']),1),
        'temperature': round(np.random.uniform(*r['temp']),1),
        'humidity':    round(np.random.uniform(*r['hum']),1),
        'ph':          round(np.random.uniform(*r['ph']),2),
        'rainfall':    round(np.random.uniform(*r['rain']),1),
        'label':       c,
    })
pd.DataFrame(rows).to_csv(OUT/'crop_recommendation.csv', index=False)
print(f"✅ crop_recommendation.csv  ({len(rows)} rows)")

# ── 2. Yield (1500 rows) ──────────────────────────────────────────────────────
base_yields = dict(maize=4.5,rice=5.0,cassava=18.0,yam=12.0,millet=2.5,
                   sorghum=3.0,tomato=25.0,cowpea=1.5,groundnut=2.0,soybean=2.5)
y_rows = []
for _ in range(1500):
    c  = np.random.choice(CROPS)
    rain=np.random.uniform(20,300); fert=np.random.randint(0,4)
    soil=np.random.randint(0,4);    irrig=np.random.randint(0,2)
    m  = 1.0
    if 100<=rain<=200: m+=.15
    elif rain<50:       m-=.25
    m += fert*.08 + soil*.10 + irrig*.15 + np.random.uniform(-.1,.1)
    y_rows.append({'crop':c,'area_ha':round(np.random.uniform(.5,20),1),
        'rainfall':round(rain,1),'temperature':round(np.random.uniform(18,40),1),
        'fertilizer_level':fert,'soil_quality':soil,'irrigation':irrig,
        'yield_per_ha':round(max(.1,base_yields[c]*m),2)})
pd.DataFrame(y_rows).to_csv(OUT/'yield_dataset.csv', index=False)
print(f"✅ yield_dataset.csv        ({len(y_rows)} rows)")

# ── 3. Pest/Disease (1800 rows) ───────────────────────────────────────────────
pest_map = {
    'maize':   ['armyworm','gray_leaf_spot','stem_borer','northern_blight','low_risk'],
    'rice':    ['brown_planthopper','blast','sheath_blight','neck_rot','low_risk'],
    'tomato':  ['late_blight','early_blight','aphids','whitefly','low_risk'],
    'cassava': ['cassava_mosaic_virus','mealybug','spider_mites','bacterial_blight','low_risk'],
    'yam':     ['yam_mosaic','anthracnose','nematodes','storage_rot','low_risk'],
}
def_pests = ['aphids','stem_rot','leaf_spot','whitefly','low_risk']
p_rows = []
for _ in range(1800):
    c   = np.random.choice(CROPS)
    tmp = round(np.random.uniform(18,40),1)
    hum = round(np.random.uniform(20,100),1)
    rai = round(np.random.uniform(0,250),1)
    stg = np.random.randint(0,5)
    pl  = pest_map.get(c, def_pests)
    if hum>70 and tmp>25 and rai>30: pest,risk = np.random.choice(pl[:4]), np.random.choice([2,3])
    elif hum>55:                      pest,risk = np.random.choice(pl[:4]), np.random.randint(1,3)
    else:                             pest,risk = 'low_risk', 0
    p_rows.append({'crop':c,'temperature':tmp,'humidity':hum,'rainfall':rai,
                   'growth_stage':stg,'pest_disease':pest,'risk_level':risk})
pd.DataFrame(p_rows).to_csv(OUT/'pest_dataset.csv', index=False)
print(f"✅ pest_dataset.csv         ({len(p_rows)} rows)")

# ── 4. Fertilizer (1200 rows) ─────────────────────────────────────────────────
ferts = ['Urea','NPK_15_15_15','SSP','MOP','DAP','CAN','Lime_Urea','NPK_20_10_10','Organic_only']
f_rows = []
for _ in range(1200):
    c  = np.random.choice(CROPS)
    N,P,K = round(np.random.uniform(5,130),1),round(np.random.uniform(5,130),1),round(np.random.uniform(5,130),1)
    ph = round(np.random.uniform(4.0,9.0),2)
    stg= np.random.randint(0,6)
    if ph<5.5:          fert='Lime_Urea'
    elif N<30 and P<30 and K<30: fert='NPK_15_15_15'
    elif N<30:          fert='Urea' if P>=30 else 'DAP'
    elif P<30:          fert='SSP'
    elif K<30:          fert='MOP'
    elif N<50:          fert='CAN'
    elif c in ('cassava','yam') and K>60: fert='MOP'
    else:               fert='NPK_20_10_10'
    f_rows.append({'crop':c,'N':N,'P':P,'K':K,'ph':ph,'growth_stage':stg,'fertilizer':fert})
pd.DataFrame(f_rows).to_csv(OUT/'fertilizer_dataset.csv', index=False)
print(f"✅ fertilizer_dataset.csv   ({len(f_rows)} rows)")
print("\n✅ All datasets generated!")
