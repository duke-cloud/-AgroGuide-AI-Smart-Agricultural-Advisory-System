"""
AgroGuide AI — Machine Learning Engine
RandomForest + GradientBoosting models for crop, yield, pest, fertilizer prediction.
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

ML_DIR = Path(__file__).resolve().parent.parent / 'ml_models'

_models = {}

def _load():
    if _models:
        return
    _models['crop']       = joblib.load(ML_DIR / 'crop_model.pkl')
    _models['crop_le']    = joblib.load(ML_DIR / 'crop_label_encoder.pkl')
    _models['yield']      = joblib.load(ML_DIR / 'yield_model.pkl')
    _models['yield_le']   = joblib.load(ML_DIR / 'yield_crop_encoder.pkl')
    _models['pest']       = joblib.load(ML_DIR / 'pest_model.pkl')
    _models['pest_risk']  = joblib.load(ML_DIR / 'pest_risk_model.pkl')
    _models['pest_cle']   = joblib.load(ML_DIR / 'pest_crop_encoder.pkl')
    _models['pest_le']    = joblib.load(ML_DIR / 'pest_label_encoder.pkl')
    _models['fert']       = joblib.load(ML_DIR / 'fertilizer_model.pkl')
    _models['fert_cle']   = joblib.load(ML_DIR / 'fert_crop_encoder.pkl')
    _models['fert_le']    = joblib.load(ML_DIR / 'fert_label_encoder.pkl')


def predict_crop(N, P, K, temperature, humidity, ph, rainfall):
    """Returns (primary_crop, top3_crops, probabilities_dict)."""
    _load()
    X = pd.DataFrame([[N, P, K, temperature, humidity, ph, rainfall]],
                     columns=['N','P','K','temperature','humidity','ph','rainfall'])
    proba   = _models['crop'].predict_proba(X)[0]
    top3_i  = np.argsort(proba)[::-1][:3]
    top3    = _models['crop_le'].inverse_transform(top3_i).tolist()
    prob_dict = {cls: round(float(p)*100, 1)
                 for cls, p in zip(_models['crop_le'].classes_, proba)}
    return top3[0], top3, prob_dict


def predict_yield(crop, area_ha, rainfall, temperature,
                  fertilizer_level, soil_quality, irrigation):
    """Returns (yield_per_ha, total_yield)."""
    _load()
    le = _models['yield_le']
    try:
        crop_enc = int(le.transform([crop])[0])
    except ValueError:
        crop_enc = 0
    X = pd.DataFrame([[crop_enc, area_ha, rainfall, temperature,
                        fertilizer_level, soil_quality, int(irrigation)]],
                     columns=['crop_enc','area_ha','rainfall','temperature',
                               'fertilizer_level','soil_quality','irrigation'])
    yph   = round(float(_models['yield'].predict(X)[0]), 2)
    total = round(yph * area_ha, 2)
    return yph, total


def predict_pest(crop, temperature, humidity, rainfall, growth_stage):
    """Returns list of dicts [{pest, risk_label, risk_level, probability, action, prevention}]."""
    _load()
    try:
        crop_enc = int(_models['pest_cle'].transform([crop])[0])
    except ValueError:
        crop_enc = 0
    X = pd.DataFrame([[crop_enc, temperature, humidity, rainfall, growth_stage]],
                     columns=['crop_enc','temperature','humidity','rainfall','growth_stage'])
    probas   = _models['pest'].predict_proba(X)[0]
    risk_enc = int(_models['pest_risk'].predict(X)[0])
    top3_i   = np.argsort(probas)[::-1][:3]
    top3     = _models['pest_le'].inverse_transform(top3_i).tolist()
    risk_labels = {0:'Low', 1:'Low', 2:'Medium', 3:'High'}
    results = []
    for i, pest in enumerate(top3):
        r = max(0, risk_enc - i)
        results.append({
            'pest':        pest.replace('_',' ').title(),
            'risk_level':  r,
            'risk_label':  risk_labels.get(r, 'Low'),
            'probability': round(float(probas[top3_i[i]]) * 100, 1),
        })
    return results


def predict_fertilizer(crop, N, P, K, ph, growth_stage):
    """Returns (fertilizer_name, confidence_pct)."""
    _load()
    try:
        crop_enc = int(_models['fert_cle'].transform([crop])[0])
    except ValueError:
        crop_enc = 0
    X = pd.DataFrame([[crop_enc, N, P, K, ph, growth_stage]],
                     columns=['crop_enc','N','P','K','ph','growth_stage'])
    fert_enc   = int(_models['fert'].predict(X)[0])
    proba      = _models['fert'].predict_proba(X)[0]
    fert_name  = _models['fert_le'].inverse_transform([fert_enc])[0]
    confidence = round(float(proba[fert_enc]) * 100, 1)
    return fert_name.replace('_', ' '), confidence
