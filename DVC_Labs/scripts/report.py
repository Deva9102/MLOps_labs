import argparse, json, os
from textwrap import dedent

def load_json(p):
    with open(p) as f:
        return json.load(f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m1", required=True)
    ap.add_argument("--m2", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    m1 = load_json(args.m1)
    m2 = load_json(args.m2)

    def row(name, k, better="lower"):
        v1, v2 = m1.get(k), m2.get(k)
        if v1 is None or v2 is None:
            return f"<tr><td>{name}</td><td colspan='2'>n/a</td><td>n/a</td></tr>"
        delta = (v2 - v1) if better == "higher" else (v1 - v2)
        arrow = "↑" if delta < 0 and better=="lower" or delta > 0 and better=="higher" else "↓"
        return f"<tr><td>{name}</td><td>{v1:.4f}</td><td>{v2:.4f}</td><td>{arrow} {abs(delta):.4f}</td></tr>"

    html = dedent(f"""
    <html>
    <head><meta charset="utf-8"><title>Fitness Model Report</title>
    <style>
      body {{ font-family: -apple-system, Segoe UI, sans-serif; margin: 24px; }}
      table {{ border-collapse: collapse; }}
      td, th {{ border: 1px solid #ddd; padding: 8px; }}
      th {{ background: #f2f2f2; }}
      code {{ background:#f7f7f7; padding:2px 4px; }}
    </style></head>
    <body>
      <h1>Model Comparison</h1>
      <p>V1: <code>{m1.get('model')}</code> vs V2: <code>{m2.get('model')}</code></p>
      <table>
        <thead><tr><th>Metric</th><th>V1</th><th>V2</th><th>Δ (better→)</th></tr></thead>
        <tbody>
          {row("RMSE", "rmse", better="lower")}
          {row("MAE",  "mae",  better="lower")}
          {row("R²",   "r2",   better="higher")}
        </tbody>
      </table>
      <p>Samples: {m1.get('n_samples')} — Features: {m1.get('n_features')} — Target: <code>{m1.get('target')}</code></p>
    </body></html>
    """).strip()

    with open(args.out, "w") as f:
        f.write(html)
    print(f"Wrote report -> {args.out}")

if __name__ == "__main__":
    main()
