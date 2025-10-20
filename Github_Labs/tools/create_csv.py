import random, string, argparse, os
from pathlib import Path

WEAK = [
    "password","123456","123456789","qwerty","abc123","letmein",
    "111111","welcome","admin","iloveyou","monkey","dragon"
]

def strong(n=14):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}?~"
    return "".join(random.choice(chars) for _ in range(n))

def medium():
    base = random.choice(["Summer","Winter","Spring","Autumn","Project","Omega","Delta"])
    year = random.choice(["2024","2025","2026"])
    suffix = random.choice(["!","?","","123"])
    return base + year + suffix

def make_passwords(total=500, weak_frac=0.3, medium_frac=0.4, seed=42):
    random.seed(seed)
    weak_n = int(total * weak_frac)
    med_n  = int(total * medium_frac)
    strong_n = total - weak_n - med_n
    out = []
    out += random.choices(WEAK, k=weak_n)
    out += [medium() for _ in range(med_n)]
    out += [strong(random.randint(12,18)) for _ in range(strong_n)]
    random.shuffle(out)
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/passwords.csv")
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--weak", type=float, default=0.3)
    ap.add_argument("--medium", type=float, default=0.4)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    Path(os.path.dirname(args.out) or ".").mkdir(parents=True, exist_ok=True)
    pwds = make_passwords(args.n, args.weak, args.medium, args.seed)
    with open(args.out, "w") as f:
        f.write("password\n")
        for p in pwds:
            f.write(p + "\n")
    print(f"Wrote {len(pwds)} passwords to {args.out}")
