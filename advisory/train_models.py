#!/usr/bin/env python3
"""
AgroGuide AI — ML Model Training Script
Run: python advisory/train_models.py
Trains: RandomForestClassifier (crop), RandomForestRegressor (yield),
        GradientBoostingClassifier (pest), RandomForestClassifier (fertilizer)
"""
import pandas as pd, numpy as np, joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, r2_score
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DSET = BASE / 'datasets'
MOD  = BASE / 'ml_models'
MOD.mkdir(exist_ok=True)

def train_crop():
    df = pd.read_csv(DSET/'crop_recommendation.csv')
    le = LabelEncoder()
    df['label_enc'] = le.fit_transform(df['label'])
    feat = ['N','P','K','temperature','humidity','ph','rainfall']
    X,y  = df[feat], df['label_enc']
    Xt,Xe,yt,ye = train_test_split(X,y,test_size=.2,random_state=42)
    m = RandomForestClassifier(n_estimators=200,random_state=42,n_jobs=-1)
    m.fit(Xt,yt)
    acc = accuracy_score(ye,m.predict(Xe))
    joblib.dump(m,  MOD/'crop_model.pkl')
    joblib.dump(le, MOD/'crop_label_encoder.pkl')
    print(f"  Crop Recommendation   Accuracy: {acc:.4f}  ({int(acc*100)}%)")

def train_yield():
    df = pd.read_csv(DSET/'yield_dataset.csv')
    le = LabelEncoder()
    df['crop_enc'] = le.fit_transform(df['crop'])
    feat = ['crop_enc','area_ha','rainfall','temperature','fertilizer_level','soil_quality','irrigation']
    X,y  = df[feat], df['yield_per_ha']
    Xt,Xe,yt,ye = train_test_split(X,y,test_size=.2,random_state=42)
    m = RandomForestRegressor(n_estimators=200,random_state=42,n_jobs=-1)
    m.fit(Xt,yt)
    r2 = r2_score(ye,m.predict(Xe))
    joblib.dump(m,  MOD/'yield_model.pkl')
    joblib.dump(le, MOD/'yield_crop_encoder.pkl')
    print(f"  Yield Prediction      R²: {r2:.4f}  ({int(r2*100)}% variance explained)")

def train_pest():
    df   = pd.read_csv(DSET/'pest_dataset.csv')
    lec  = LabelEncoder(); lep = LabelEncoder()
    df['crop_enc'] = lec.fit_transform(df['crop'])
    df['pest_enc'] = lep.fit_transform(df['pest_disease'])
    feat = ['crop_enc','temperature','humidity','rainfall','growth_stage']
    X,yp,yr = df[feat], df['pest_enc'], df['risk_level']
    Xt,Xe,yt,ye   = train_test_split(X,yp,test_size=.2,random_state=42)
    Xtr,Xer,ytr,yer = train_test_split(X,yr,test_size=.2,random_state=42)
    m  = GradientBoostingClassifier(n_estimators=150,random_state=42)
    mr = RandomForestClassifier(n_estimators=100,random_state=42,n_jobs=-1)
    m.fit(Xt,yt); mr.fit(Xtr,ytr)
    acc = accuracy_score(ye,m.predict(Xe))
    joblib.dump(m,  MOD/'pest_model.pkl');   joblib.dump(mr, MOD/'pest_risk_model.pkl')
    joblib.dump(lec,MOD/'pest_crop_encoder.pkl'); joblib.dump(lep,MOD/'pest_label_encoder.pkl')
    print(f"  Pest & Disease        Accuracy: {acc:.4f}  ({int(acc*100)}%)")

def train_fertilizer():
    df   = pd.read_csv(DSET/'fertilizer_dataset.csv')
    lec  = LabelEncoder(); lef = LabelEncoder()
    df['crop_enc'] = lec.fit_transform(df['crop'])
    df['fert_enc'] = lef.fit_transform(df['fertilizer'])
    feat = ['crop_enc','N','P','K','ph','growth_stage']
    X,y  = df[feat], df['fert_enc']
    Xt,Xe,yt,ye = train_test_split(X,y,test_size=.2,random_state=42)
    m = RandomForestClassifier(n_estimators=200,random_state=42,n_jobs=-1)
    m.fit(Xt,yt)
    acc = accuracy_score(ye,m.predict(Xe))
    joblib.dump(m,  MOD/'fertilizer_model.pkl')
    joblib.dump(lec,MOD/'fert_crop_encoder.pkl'); joblib.dump(lef,MOD/'fert_label_encoder.pkl')
    print(f"  Fertilizer Advisory   Accuracy: {acc:.4f}  ({int(acc*100)}%)")

if __name__ == '__main__':
    print("🤖 Training AgroGuide AI Machine Learning Models...")
    print("="*55)
    train_crop()
    train_yield()
    train_pest()
    train_fertilizer()
    print("="*55)
    print("✅ All models saved to ml_models/")
