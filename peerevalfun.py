"""
Collate peer/self-evaluation scores, flag late submissions,
and sort the final table alphabetically by LAST name.
"""
import datetime as dt
from pathlib import Path
import pandas as pd

# ── EDIT THESE TWO LINES ────────────────────────────────────────────────────
CSV_PATH     = Path("Self_Peer Evaluation for Reproductive Health Presentations - Spring 2025 (Responses) - Form Responses 1 (1).csv")
SUMMARY_OUT  = Path("peer_evaluation_summary.csv")
# ────────────────────────────────────────────────────────────────────────────

CUTOFF_DATE = dt.datetime(2025, 4, 23)
LIKERT_MAP  = {
    "strongly disagree": 1,
    "disagree":           2,
    "neutral":            3,
    "agree":              4,
    "strongly agree":     5,
}

def collect_scores(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    self_cols      = [c for c in df.columns if c.startswith("Self Evaluation")]
    teammate_cols  = {n: [c for c in df.columns
                          if c.startswith(f"Teammate {n} Evaluation")]
                      for n in range(1, 5)}

    scores, late_flag = {}, {}

    # Update the late_flag logic to check for "4/24" in the Timestamp column
    for _, row in df.iterrows():
        evaluator = str(row["Your Name"]).strip()

        if evaluator not in late_flag:
            late_flag[evaluator] = "4/24" in row["Timestamp"]

        # self-evaluation
        for col in self_cols:
            val = str(row[col]).strip().lower()
            if val in LIKERT_MAP:
                scores.setdefault(evaluator, []).append(LIKERT_MAP[val])

        # teammate evaluations
        for n in range(1, 5):
            name_col = f"Teammate {n}"
            if name_col not in row or pd.isna(row[name_col]):
                continue
            student = str(row[name_col]).strip()
            for col in teammate_cols[n]:
                val = str(row[col]).strip().lower()
                if val in LIKERT_MAP:
                    scores.setdefault(student, []).append(LIKERT_MAP[val])

    summary = pd.DataFrame(
        {
            "Student": list(scores.keys()),
            "Average Score": [round(sum(v)/len(v), 2) for v in scores.values()],
            "Late Submission": [late_flag.get(s, False) for s in scores.keys()],
        }
    )

    # ── NEW: sort by last name ────────────────────────────────────────────
    summary["LastName"] = summary["Student"].str.split().str[-1].str.lower()
    summary = (summary
               .sort_values(["LastName", "Student"])
               .drop(columns="LastName")
               .reset_index(drop=True))
    # ───────────────────────────────────────────────────────────────────────

    return summary

if __name__ == "__main__":
    summary_df = collect_scores(CSV_PATH)
    summary_df.to_csv(SUMMARY_OUT, index=False)
    print(f"✓ Saved summary to {SUMMARY_OUT}\n")
    print(summary_df.head(10).to_string(index=False))
