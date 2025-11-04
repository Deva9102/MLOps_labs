import argparse, pandas as pd, yaml
from sklearn.preprocessing import StandardScaler

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    # Read feature flags from params.yaml
    params = yaml.safe_load(open("params.yaml"))
    add_weekend = params["features"]["add_weekend_flag"]
    do_scale = params["features"]["scale"]

    # Load dataset
    df = pd.read_csv(args.inp)

    if add_weekend:
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # Select the feature columns
    feat_cols = ["steps", "minutes_active"] + (["is_weekend"] if add_weekend else [])
    X = df[feat_cols].copy()
    y = df["calories"].copy()

     # Optional standardization so features are on the same scale
    if do_scale:
        scaler = StandardScaler()
        X[feat_cols] = scaler.fit_transform(X[feat_cols])

    # Reassemble features and target
    out = X.copy()
    out["calories"] = y
    out.to_csv(args.out, index=False)

    # Confirmation in the console
    print(f"Wrote {args.out} ({out.shape[0]} rows, {out.shape[1]-1} features)")
