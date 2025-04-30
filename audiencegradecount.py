"""
QP-2 Presentation - Per-student group-appearance score
------------------------------------------------------
1. Put this file next to your CSV (or edit CSV_PATH).
2.  pip install pandas   # only once
3. Click Run.

Output:
    • peer_group_count_normalized.csv   (clean results)
    • quick preview printed to console
"""

from pathlib import Path
import pandas as pd

# ── EDIT THESE THREE LINES ──────────────────────────────────────────────────
CSV_PATH    = Path("QP2 Presentation Peer Evaluation (Responses) - Form Responses 1.csv")
NAME_COL    = "Your Name"            # exact column label in your form export
GROUP_COL   = "Presenting Group Number" # exact column label in your form export
# ────────────────────────────────────────────────────────────────────────────
SUMMARY_OUT = Path("peer_group_count_normalized.csv")

def main():
    df = pd.read_csv(CSV_PATH)

    # Keep just the two columns we need, strip spaces, and drop NAs
    df = (df[[NAME_COL, GROUP_COL]]
            .dropna()
            .assign(**{NAME_COL: lambda d: d[NAME_COL].str.strip()}))

    # Count unique (Name, Group) pairs  ➔  per-name group count
    unique_pairs = df.drop_duplicates(subset=[NAME_COL, GROUP_COL])
    counts = (unique_pairs
              .groupby(NAME_COL)[GROUP_COL]
              .nunique()
              .rename("Group Count"))

    # Normalise by the maximum
    max_cnt = counts.max()
    summary = (counts / max_cnt).rename("Normalised").reset_index()

    # Sort by last name once
    summary["LastName"] = summary[NAME_COL].str.split().str[-1].str.lower()
    summary = (summary
               .sort_values(["LastName", NAME_COL])
               .drop(columns="LastName")
               .reset_index(drop=True))

    # Save + preview
    summary.to_csv(SUMMARY_OUT, index=False)
    print(f"✓ Saved summary to {SUMMARY_OUT}\n")
    print(summary.head(10).to_string(index=False))

if __name__ == "__main__":
    main()
