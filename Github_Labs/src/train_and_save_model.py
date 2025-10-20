import os, re, json, math
from pathlib import Path
from datetime import datetime
from statistics import mean, median

from dotenv import load_dotenv
import pandas as pd
from google.cloud import storage

import src.registry as registry

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / ".env"
if ENV.exists():
    load_dotenv(ENV)
else:
    load_dotenv()

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
VERSION_FILE_NAME = os.getenv("VERSION_FILE_NAME") or "model_version.txt"

# input CSV path & column name
PASSWORDS_CSV = Path(os.getenv("PASSWORDS_CSV", ROOT / "data" / "passwords.csv"))
PASSWORDS_COL = os.getenv("PASSWORDS_COL", "password")

OUT_DIR = ROOT / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def gcs_client():
    return storage.Client()

def gcs_bucket(name):
    return gcs_client().bucket(name)

def ensure_folder_exists(bucket, folder_name):
    blob = bucket.blob(f"{folder_name}/")
    if not blob.exists(client=gcs_client()):
        blob.upload_from_string("")

def upload_file(bucket, blob_name, local_path: str):
    bucket.blob(blob_name).upload_from_filename(local_path)

def upload_json(bucket, blob_name, data: dict):
    bucket.blob(blob_name).upload_from_string(json.dumps(data, indent=2))

def get_model_version(bucket_name, version_file_name) -> int:
    b = gcs_bucket(bucket_name)
    bl = b.blob(version_file_name)
    if bl.exists(client=gcs_client()):
        try:
            return int(bl.download_as_text().strip())
        except Exception:
            return 0
    return 0

def update_model_version(bucket_name, version_file_name, version: int) -> bool:
    if not isinstance(version, int):
        raise ValueError("Version must be an integer")
    try:
        b = gcs_bucket(bucket_name)
        b.blob(version_file_name).upload_from_string(str(version))
        return True
    except Exception as e:
        print(f"Error updating model version: {e}")
        return False

COMMON = {
    "123456","password","123456789","12345","qwerty","abc123","111111","123123",
    "password1","1234","iloveyou","admin","welcome","monkey","dragon","letmein"
}
LOWER = re.compile(r"[a-z]")
UPPER = re.compile(r"[A-Z]")
DIGIT = re.compile(r"\d")
SYMB  = re.compile(r"[^A-Za-z0-9]")

def char_classes(s: str):
    return {
        "lower": bool(LOWER.search(s)),
        "upper": bool(UPPER.search(s)),
        "digit": bool(DIGIT.search(s)),
        "symbol": bool(SYMB.search(s)),
    }

def has_repeated_sequences(s: str, k: int = 3) -> bool:
    if len(s) < k:
        return False
    for i in range(len(s) - k + 1):
        chunk = s[i:i+k]
        if len(set(chunk)) == 1:
            return True
    if len(s) >= 2 and s[:2] * (len(s)//2) in s:
        return True
    return False

def score_password(pw: str) -> float:
    if not pw or pw.lower() in COMMON:
        return 5.0
    length_pts = min(40.0, len(pw) * 3.5)
    cls = char_classes(pw)
    diversity = sum(cls.values())
    diversity_pts = {0:0, 1:10, 2:20, 3:32, 4:40}[diversity]
    repeat_penalty = 0.0 if not has_repeated_sequences(pw) else -12.0
    uniq = len(set(pw))
    uniq_bonus = min(10.0, max(0.0, (uniq - 5) * 1.2))

    raw = length_pts + diversity_pts + repeat_penalty + uniq_bonus
    return float(max(0.0, min(100.0, raw)))

def load_passwords(csv_path: Path, col: str) -> list[str]:
    if not csv_path.exists():
        raise SystemExit(f"No input CSV found at {csv_path}")
    df = pd.read_csv(csv_path)
    if col not in df.columns:
        raise SystemExit(f"Column '{col}' not found in {csv_path}. Columns: {list(df.columns)}")
    return [str(x) for x in df[col].dropna().tolist()]

def compute_batch_metrics(scores: list[float]) -> dict:
    if not scores:
        return {
            "count": 0, "avg_score": 0.0, "median_score": 0.0,
            "weak_pct": 0.0, "strong_pct": 0.0,
            "p10": 0.0, "p90": 0.0,
        }
    sorted_scores = sorted(scores)
    n = len(scores)
    weak_pct = sum(1 for s in scores if s < 40.0) / n
    strong_pct = sum(1 for s in scores if s >= 80.0) / n
    def percentile(p):  # p in [0,100]
        if n == 1: return sorted_scores[0]
        k = (n-1) * (p/100.0)
        f = math.floor(k); c = math.ceil(k)
        if f == c: return sorted_scores[int(k)]
        return sorted_scores[f] * (c-k) + sorted_scores[c] * (k-f)
    return {
        "count": n,
        "avg_score": float(round(mean(scores), 3)),
        "median_score": float(round(median(scores), 3)),
        "weak_pct": float(round(weak_pct, 4)),
        "strong_pct": float(round(strong_pct, 4)),
        "p10": float(round(percentile(10), 3)),
        "p90": float(round(percentile(90), 3)),
    }

def save_artifacts(passwords: list[str], scores: list[float], out_dir: Path):
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    metrics_path = out_dir / f"metrics_{ts}.json"
    weak_path    = out_dir / f"weak_passwords_{ts}.csv"
    sample_path  = out_dir / f"sample_scored_{ts}.csv"

    metrics = compute_batch_metrics(scores)
    metrics_path.write_text(json.dumps(metrics, indent=2))
    weak = [(pw, sc) for pw, sc in zip(passwords, scores) if sc < 40.0]
    pd.DataFrame(weak, columns=["password", "score"]).to_csv(weak_path, index=False)
    sample = list(zip(passwords, scores))[:100]
    pd.DataFrame(sample, columns=["password", "score"]).to_csv(sample_path, index=False)

    return metrics, metrics_path, weak_path, sample_path, ts

def main():
    assert BUCKET_NAME, "GCS_BUCKET_NAME not set"

    current_version = get_model_version(BUCKET_NAME, VERSION_FILE_NAME)
    new_version = current_version + 1

    passwords = load_passwords(PASSWORDS_CSV, PASSWORDS_COL)
    scores = [score_password(pw) for pw in passwords]
    metrics, metrics_path, weak_path, sample_path, ts = save_artifacts(passwords, scores, OUT_DIR)

    MIN_AVG = float(os.getenv("MIN_AVG_SCORE", "0.0"))
    if metrics["avg_score"] < MIN_AVG:
        raise SystemExit(f"Average score {metrics['avg_score']:.2f} < MIN_AVG_SCORE {MIN_AVG}")

    b = gcs_bucket(BUCKET_NAME)
    ensure_folder_exists(b, "reports")
    metrics_blob = f"reports/metrics_v{new_version}_{ts}.json"
    weak_blob    = f"reports/weak_passwords_v{new_version}_{ts}.csv"
    sample_blob  = f"reports/sample_scored_v{new_version}_{ts}.csv"
    upload_file(b, metrics_blob, str(metrics_path))
    upload_file(b, weak_blob,    str(weak_path))
    upload_file(b, sample_blob,  str(sample_path))
    print(f"Uploaded: gs://{BUCKET_NAME}/{metrics_blob}")
    print(f"Uploaded: gs://{BUCKET_NAME}/{weak_blob}")
    print(f"Uploaded: gs://{BUCKET_NAME}/{sample_blob}")

    man = registry.read_manifest()
    promoted = False
    score = float(metrics["avg_score"])
    prev  = float(man.get("metric", -1.0))
    
    if score > prev:
        registry.write_manifest(new_version, score, metrics_blob)
        promoted = True
    print(f"PROMOTED={promoted}")

    if update_model_version(BUCKET_NAME, VERSION_FILE_NAME, new_version):
        print(f"Version updated to {new_version}")
    else:
        print("Failed to update version")
    print(f"MODEL_VERSION_OUTPUT: {new_version}")
    print(f"METRIC_OUTPUT: {score}")

if __name__ == "__main__":
    main()
