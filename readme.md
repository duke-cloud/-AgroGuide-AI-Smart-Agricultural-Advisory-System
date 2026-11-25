# 🌾 AgroGuide AI — Smart Agricultural Advisory System

A full-stack **Django + Python machine-learning** web application that gives Nigerian
farmers data-driven farming advice: crop recommendation, fertilizer planning, yield
prediction, pest-risk assessment, weather advisories, symptom-based disease diagnosis,
and a farm-aware chat assistant. Demo data is centred on **Abuja, FCT**.

---

## ✨ Features

| Module | What it does |
|---|---|
| 🏠 **Dashboard** | Farm overview, NPK charts, advisory history |
| 🌱 **Crop Advisory** | ML crop recommendation + planting-window rules |
| 🧪 **Fertilizer Plan** | ML + rules-based plan with quantities for the farm size |
| 🦟 **Pest Risk** | Gradient-boosting risk assessment + treatment suggestions |
| 📊 **Yield Prediction** | Random-forest regression with scenario comparison charts |
| 🌤️ **Weather** | OpenWeatherMap current + 7-day forecast (simulated if no API key) |
| 🔬 **Disease Diagnosis** | Symptom-to-diagnosis rule matching with a history log |
| 💬 **AI Chat** | Keyword-driven assistant that calls the ML + rules engines using your farm's data |
| 🗺️ **Farm Map** | Leaflet map with draggable pin, click-to-place, GPS button, satellite view |
| 📅 **Crop History** | Season-by-season crop tracking per farm |

---

## 🚀 Quick Start

### Linux / macOS (one command)

```bash
git clone <repo-url> && cd agro_ai_agent
chmod +x setup_and_run.sh
./setup_and_run.sh
```

### Windows (PowerShell)

`setup_and_run.sh` is a bash script, so on Windows either run it from **Git Bash / WSL**,
or follow these steps:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

python manage.py migrate
python datasets/generate_datasets.py      # create synthetic training data
python advisory/train_models.py           # train the 4 ML models
python manage.py createsuperuser
python manage.py runserver
```

Open **http://127.0.0.1:8000**. On the manual path there is no demo farmer, so either
register at `/accounts/register/` or use the demo users below (created by the setup script).

### Demo credentials (created by `setup_and_run.sh`)

| Role | Username | Password |
|---|---|---|
| Farmer (2 demo farms, Kuje & Gwagwalada) | `farmer1` | `farmer123` |
| Admin (`/admin/`) | `admin` | `admin123` |

> ⚠️ These are for local development only. Change or remove them before any real deployment.

---

## ⚙️ Configuration

Copy `.env.example` to `.env` (loaded automatically via `python-dotenv`).

| Variable | Default | Purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | insecure dev key | Django secret key. **Set a long random value in production.** (`SECRET_KEY` is also accepted.) |
| `DEBUG` | `True` | Set to `False` in production |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated hostnames |
| `OPENWEATHER_API_KEY` | *(empty)* | Free key from <https://openweathermap.org/api>. Without it the app uses **simulated** weather so every feature still works. |

---

## 🤖 Machine Learning

| Module | Algorithm | Typical result* |
|---|---|---|
| Crop recommendation | `RandomForestClassifier` | ~75–78 % accuracy |
| Yield prediction | `RandomForestRegressor` | R² ≈ 0.99 |
| Pest & disease risk | `GradientBoostingClassifier` | ~53–60 % accuracy |
| Fertilizer advisory | `RandomForestClassifier` | ~98–99 % accuracy |

\* Training data is **synthetic** and regenerated on each run, so exact figures vary slightly.

**Inputs** — Crop: `N, P, K` (mg/kg), temperature (°C), humidity (%), pH, rainfall (mm).
Yield: crop, area (ha), rainfall, temperature, fertilizer level, soil quality, irrigation.

**Retrain anytime:**

```bash
python datasets/generate_datasets.py   # rebuild CSVs
python advisory/train_models.py        # rebuild ml_models/*.pkl
```

> **Limitations.** Models are trained on synthetic data and the disease diagnosis is
> rule-based, so output is **decision support, not a replacement for an agronomist**.
> For production accuracy, retrain on real, locally sourced field data.

---

## 🗺️ Farm Map

The map uses **Leaflet** with **OpenStreetMap** tiles and needs an internet connection to
fetch tiles. Use the layer switcher (top-right of the map) to choose *Street map*,
*Street (alt)*, or *Satellite*. If OpenStreetMap tiles fail repeatedly, the map
automatically switches to the CARTO street layer.

### Troubleshooting: map tiles say **"Access blocked"**

OpenStreetMap's tile servers reject requests that carry no `Referer` header. Django's
default `Referrer-Policy: same-origin` strips it from cross-origin requests, which blocks
every tile when running locally. This is fixed in three places — keep all three:

1. `agro_ai_agent/settings.py` → `SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'`
2. `templates/base.html` → `<meta name="referrer" content="strict-origin-when-cross-origin">`
3. `static/js/map.js` → tile layer option `referrerPolicy: 'strict-origin-when-cross-origin'`

If you still see a blocked/grey map after pulling these changes, hard-refresh the page
(`Ctrl+Shift+R`) to bypass cached tiles, and confirm you are online.

---

## 🧭 Main Routes

| URL | Description |
|---|---|
| `/` | Landing page |
| `/dashboard/` | Farmer dashboard |
| `/accounts/register/` · `/login/` · `/logout/` · `/profile/` | Authentication & profile |
| `/farms/` · `/farms/add/` · `/farms/<id>/` | Farm list, create, detail (with map) |
| `/advisory/crop/<farm_id>/` | Crop recommendation |
| `/advisory/fertilizer/<farm_id>/` | Fertilizer plan |
| `/advisory/yield/<farm_id>/` | Yield prediction |
| `/advisory/pest/<farm_id>/` | Pest risk |
| `/advisory/weather/<farm_id>/` | Weather & forecast |
| `/advisory/chat/<farm_id>/` | AI chat assistant |
| `/disease/<farm_id>/` | Disease diagnosis |
| `/admin/` | Django admin |

---

## 📁 Project Structure

```
agro_ai_agent/
├── manage.py
├── requirements.txt
├── setup_and_run.sh          # one-command setup (bash)
├── .env.example              # copy to .env
├── agro_ai_agent/            # Django project (settings, urls, wsgi)
├── accounts/                 # auth + farmer profiles
├── farms/                    # farm models, CRUD views, crop history
├── advisory/
│   ├── ml_engine.py          # loads & runs the ML models
│   ├── rules_engine.py       # agronomic domain rules
│   ├── weather_service.py    # OpenWeatherMap + simulated fallback
│   └── train_models.py       # (re)train all models
├── disease/                  # symptom-based diagnosis
├── reports/                  # landing page + dashboard
├── datasets/
│   └── generate_datasets.py  # synthetic training-data generator
├── ml_models/                # trained .pkl files (generated)
├── static/
│   ├── css/style.css
│   └── js/                   # advisory.js · chat.js · map.js
└── templates/base.html       # sidebar layout
```

`datasets/*.csv`, `ml_models/*.pkl`, `db.sqlite3`, `.env`, `staticfiles/` and `media/*`
are **git-ignored** — they are generated or contain secrets/user data (see `.gitignore`).

---

## 🔒 Production Deployment

```bash
# .env
DEBUG=False
DJANGO_SECRET_KEY=<long-random-string>
ALLOWED_HOSTS=yourdomain.com
OPENWEATHER_API_KEY=<your-key>
```

```bash
python manage.py collectstatic --noinput
gunicorn agro_ai_agent.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

- WhiteNoise serves static files; put **Nginx** (with HTTPS) in front of Gunicorn.
- Replace SQLite with **PostgreSQL** for multi-user workloads.
- Remove the demo `admin` / `farmer1` accounts and store `media/` on durable storage.

---

## 🛠️ Troubleshooting

| Symptom | Fix |
|---|---|
| Map shows "Access blocked" | See [Farm Map](#-farm-map) above |
| Weather looks fake | No `OPENWEATHER_API_KEY` set — simulated data is used by design |
| `ModuleNotFoundError: dotenv` | `pip install -r requirements.txt` inside the activated venv |
| Advisory pages error about missing models | Run the two retrain commands under *Machine Learning* |
| `DisallowedHost` error | Add your host to `ALLOWED_HOSTS` in `.env` |

---

## 📄 License

MIT — free to use for educational and commercial agricultural projects.

Built for Nigerian farmers 🇳🇬 · Adaptable to other West African agricultural contexts.