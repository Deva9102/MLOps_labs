import argparse, json, os, joblib
import pandas as pd, numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Train a simple Random Forest Regressor model

def guess_target(df: pd.DataFrame) -> str:
    """
    Heuristic to pick the target column
    """
    for cand in ["target", "y", "fitness_score", "label"]:
        if cand in df.columns:
            return cand
    return df.columns[-1]

def main():
    # CLI args: input CSV, output model path, output metrics JSON path
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--metrics", required=True)
    args = p.parse_args()

    # Ensure output folders exist
    os.makedirs(os.path.dirname(args.model), exist_ok=True)
    os.makedirs(os.path.dirname(args.metrics), exist_ok=True)

    # Load data and split into features/target
    df = pd.read_csv(args.inp)
    tgt = guess_target(df)
    X = df.drop(columns=[tgt]); y = df[tgt]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    # Fit Random Forest Regressor
    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=12,
        random_state=42,
        n_jobs=-1
    ).fit(X_tr, y_tr)
    preds = model.predict(X_te)

    # Evaluate
    metrics = {
        "rmse": float(np.sqrt(mean_squared_error(y_te, preds))),
        "mae":  float(mean_absolute_error(y_te, preds)),
        "r2":   float(r2_score(y_te, preds)),
        "n_features": int(X.shape[1]),
        "n_samples": int(len(df)),
        "target": tgt,
        "model": "RandomForestRegressor",
    }

    joblib.dump(model, args.model)
    with open(args.metrics, "w") as f: json.dump(metrics, f, indent=2)
    print(f"Saved model -> {args.model}")
    print(f"Saved metrics -> {args.metrics}")
    print(metrics)

if __name__ == "__main__":
    main()