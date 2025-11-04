# MLOps Lab — DVC Data & Model Versioning (Fitness Calories)

This project uses **DVC** to version-control a synthetic **fitness** dataset and compare two regression models that predict **calories** burned.

- **Model v1:** `LinearRegression`
- **Model v2:** `RandomForestRegressor (n_estimators=150, max_depth=12)`

DVC orchestrates the pipeline and tracks large artifacts (data & models). Small metric JSONs are tracked so we can diff results across runs/commits.  
An HTML report summarizes the comparison.

---

## Results & Metric Comparison

From a recent run (your numbers may differ slightly due to randomness):

| Model | RMSE | MAE | R² |
|---|---:|---:|---:|
| **v1 (LinearRegression)** | **86.3704** | **68.4350** | **0.7047** |
| **v2 (RandomForest)** | **96.2524** | **74.6912** | **0.6333** |

In our synthetic setup (target is linear + noise), the **linear model** appropriately outperforms the random forest.

Artifacts:
- `metrics/metrics_v1.json`
- `metrics/metrics_v2.json`
- `reports/fitness.html`

---

## What Happens in This Project (End-to-End)

1) **Synthetic dataset is generated**
   - `scripts/make_dataset.py` creates **`data/fitness.csv`** with 1,000 rows:
     - `steps`, `minutes_active`, `day_of_week` (0–6), and target **`calories`** (a linear combo + noise).
   - This keeps the lab self-contained—no external downloads needed.

2) **Feature engineering & (optional) scaling**
   - `scripts/features.py` reads `data/fitness.csv` and writes **`data/fitness.feat.csv`**.
   - What it adds/does:
     - **`is_weekend`** flag (from `day_of_week`) if enabled in `params.yaml`.
     - **Standardization** of features if `features.scale: true` in `params.yaml`.

3) **Model training (two versions)**
   - `scripts/train_v1.py` trains **LinearRegression** → saves **`models/model_v1.pkl`**.
   - `scripts/train_v2.py` trains **RandomForestRegressor** → saves **`models/model_v2.pkl`**.
   - Each script also writes a **metrics JSON**:
     - **`metrics/metrics_v1.json`**, **`metrics/metrics_v2.json`**
     - Contains **RMSE**, **MAE**, **R²**, feature count, sample count, model name.

4) **HTML comparison report**
   - `scripts/report.py` reads both metric files and generates:
     - **`reports/fitness.html`** with a clean table comparing **RMSE / MAE / R²** and deltas (↑/↓).

5) **DVC tracks & orchestrates**
   - `dvc repro` runs the full pipeline and updates `dvc.lock`.
   - Large artifacts (data & models) can be **pushed to your DVC remote (GCS)** with `dvc push`.
   - Small files like metrics JSON are committed to Git so you can `dvc metrics diff` across versions.

### TL;DR Artifacts Produced

- **Data:** `data/fitness.csv`, `data/fitness.feat.csv`
- **Models:** `models/model_v1.pkl`, `models/model_v2.pkl`
- **Metrics:** `metrics/metrics_v1.json`, `metrics/metrics_v2.json`
- **Report:** `reports/fitness.html`

## Project Workflow

### Pipeline (via `dvc.yaml`)
1. **make_dataset** → `data/fitness.csv`
2. **features** → `data/fitness.feat.csv` (adds `is_weekend`, optional scaling from `params.yaml`)
3. **train_v1** → `models/model_v1.pkl`, `metrics/metrics_v1.json`
4. **train_v2** → `models/model_v2.pkl`, `metrics/metrics_v2.json`
5. **report** → `reports/fitness.html`

## How to Run

1) **Install dependencies**
```bash
pip install -r requirements.txt
# or minimally:
# pip install dvc[gs] pandas numpy scikit-learn joblib pyyaml

