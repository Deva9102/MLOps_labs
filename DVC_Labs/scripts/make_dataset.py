import argparse, numpy as np, pandas as pd
# Set a fixed seed
rng = np.random.default_rng(42)

def synth(n=1000):
    # Random day of week
    dows = rng.integers(0, 7, size=n)
    # Simulate daily steps
    steps = rng.normal(8000, 2500, size=n).clip(0)
    # Simulate active minutes
    mins  = rng.normal(45, 20, size=n).clip(0)
    # Calories is a noisy linear combo of steps and active minutes
    cal   = 0.04*steps + 6.0*mins + rng.normal(0, 80, size=n)
    # Pack into a DataFrame
    return pd.DataFrame({"steps": steps, "minutes_active": mins, "day_of_week": dows, "calories": cal})

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    # Generate 1,000 synthetic rows and save
    df = synth(1000)
    df.to_csv(args.out, index=False)
    # Quick success message
    print(f"Wrote {args.out} ({len(df)} rows)")
