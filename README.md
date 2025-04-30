# Peer‑Evaluation Analytics Toolkit

A small collection of Python utilities for cleaning, summarising and visualising **teaching‑evaluation Google‑Form exports**.

| File | Purpose |
|------|---------|
| **`peerevalfun.py`** | Collate *self/peer* evaluation scores (Likert 1–5), compute a per‑student average, mark late submissions and output a tidy CSV. |
| **`audiencegradecount.py`** | For QP‑2 presentations, count how many unique presenting‑groups each evaluator graded, normalise by the max, and output a single score per student. |
| **`test1qp2insights.py`** | End‑to‑end exploratory report generator: high‑DPI box‑plots, phrase word‑clouds, radar charts, bump charts and comment “buzz” metrics – one mini‑report per presenting group. |
| **`Self_Peer Evaluation … (Responses)‑1.csv`** | Google‑Forms export for **self/peer evaluation** assignment. |
| **`QP2 Presentation Peer Evaluation … (Responses)‑1.csv`** | Google‑Forms export for **QP‑2 presentation audience feedback**. |

---

## 1  Quick Start

```bash
# Clone / download this repo
cd peer‑evaluation‑toolkit

python -m venv .venv && source .venv/bin/activate  # optional but recommended
pip install -r requirements.txt                     # install libraries

# --- 1) Self/Peer averages ------------------------------------------------
python peerevalfun.py       # writes peer_evaluation_summary.csv

# --- 2) Audience coverage score ------------------------------------------
python audiencegradecount.py  # writes peer_group_count_normalized.csv

# --- 3) Full QP‑2 insight pack -------------------------------------------
python test1qp2insights.py    # creates group_reports/** per‑group figures
```

All scripts ship with **editable constants** at the top (CSV paths, output folders, date cut‑offs, column labels).  Most users can simply drop their own Google‑Form exports beside the scripts and tweak those few lines.

> **Tip:** Filenames containing spaces work fine – they are wrapped in quotes in each script’s default path.

---

## 2  Project Structure

```
peer‑evaluation‑toolkit/
├── peerevalfun.py                     # Self/Peer evaluator
├── audiencegradecount.py              # Audience‑coverage scorer
├── test1qp2insights.py                # Visual insight generator
├── QP2 Presentation … .csv            # QP‑2 audience responses
├── Self_Peer Evaluation … .csv        # Self/peer responses
└── group_reports/                     # (auto‑generated) one folder per group
```

`group_reports/<group‑slug>` contains:

* `*_boxplot.png`   Horizontal box‑plot of all seven score categories
* `*_phrase_wordcloud.png`   Word‑cloud built from high‑frequency phrases in comment text (bigrams/trigrams)
* `*_radar.png`   Spider chart of group‑average scores
* `*_bump_chart.png`   Bump chart comparing category rankings across all groups
* …plus any extra exploratory charts added over time.

---

## 3  Dependencies

All required Python packages are available on PyPI:

```text
pandas
numpy
matplotlib
wordcloud
scipy
scikit‑learn
```

A convenience `requirements.txt` is provided; install with `pip install -r requirements.txt`.

The visual script (`test1qp2insights.py`) also uses **`wordcloud`** and **Matplotlib’s `WordCloud`** backend – make sure a working font is present on your system (the default DejaVu Sans is bundled with Matplotlib, so it usually “just works”).

---

## 4  Script Details

### 4.1  `peerevalfun.py`

* **Input:** `Self_Peer Evaluation … (Responses).csv`
* **Logic**  
  1. Map every “Strongly Disagree → Strongly Agree” answer to 1‑5.  
  2. Aggregate across *all* questions for each recipient (self included).  
  3. If the evaluator’s timestamp is after **2025‑04‑23**, mark their own evaluation as **late**.  
  4. Sort alphabetically by last name and write `peer_evaluation_summary.csv`.
* **Config knobs:** `CSV_PATH`, `SUMMARY_OUT`, `CUTOFF_DATE`, `LIKERT_MAP`.

### 4.2  `audiencegradecount.py`

* **Input:** `QP2 Presentation Peer Evaluation (Responses).csv`
* **Logic**  
  1. Drop duplicate (Name, Group) pairs so each evaluator/group combination counts once.  
  2. Count unique groups per evaluator.  
  3. Divide by the *maximum* count observed → range [0, 1].  
  4. Sort by last name and write `peer_group_count_normalized.csv`.
* **Config knobs:** `CSV_PATH`, `NAME_COL`, `GROUP_COL`, `SUMMARY_OUT`.

### 4.3  `test1qp2insights.py`

A richer exploratory notebook distilled into a script.  For **every distinct “Presenting Group Number”** it:

| Step | Output | Notes |
|------|--------|-------|
| 1 | `*_boxplot.png` | 7 horizontal box‑plots (one per rubric category), sans fliers. |
| 2 | `*_phrase_wordcloud.png` | Word‑cloud from 2‑3‑word phrases extracted with `sklearn`’s `CountVectorizer`. |
| 3 | `*_radar.png` | Radar chart of average scores (closing the polygon). |
| 4 | `overall_bump_chart.png` | Cross‑group bump chart showing relative ranking per category. |
| 5 | Comment “buzz” metrics | Experimental; calculates comment richness & length stats (saved to CSV, coming soon). |

* **Config knobs:** `INPUT_CSV`, `OUTPUT_DIR`, plus an internal `target_cats` list detected dynamically right after the *Presenting Group Number* column.

---

## 5  Extending the Toolkit

* **Different Likert scales?**  Modify `LIKERT_MAP` in `peerevalfun.py` or override with a CLI flag (PR welcome!).
* **Non‑English feedback?**  Swap in a language‑specific stop‑word list for the word‑cloud step.
* **Additional plots or metrics** are easy to slot into `test1qp2insights.py`; it already groups by `Presenting Group Number` – just append your Matplotlib/Seaborn plot and save to the same `folder`.

Feel free to open issues or submit pull‑requests – especially for *automated PDF report collation* (one next‑step idea).

---

## 6  License

This repository is released under the **MIT License** – see `LICENSE` for details.  Feel free to reuse, modify and share with attribution.

---

## 7  Citation / Acknowledgements

If this toolkit helps your teaching analytics, please cite it in your course documentation:

> *Alexander G. (2025). Peer‑Evaluation Analytics Toolkit (Version 1.0). GitHub repository.*

Big thanks to the Spring‑2025 **Reproductive Health** cohort for providing rich data to iterate on!  
Extra shout‑out to the entire QP‑2 presentation teams for the engaging sessions that inspired the visual reports.

---

Happy analysing, and may your box‑plots be ever normal!


---

## 8  Google‑Form Design Reference

Below is a reconstruction of the **two Google Forms** that generate the CSV exports shipped in this repo. If you ever need to recreate the forms (e.g. in a different Google Workspace or semester) copy‑paste the wording below and use the suggested *question types*.

### 8.1  Self & Peer Evaluation  (10‑item rubric × N people)

| # | Prompt (Question type) |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | **Timestamp** *(automatic)* |
| 2 | **Your Name** *(Short answer)* |
| 3‑6 | **Teammate 1‑4** – "Enter full name of teammate #X" *(Short answer; questions 3 & 4 optional for smaller groups)* |
| 7 | **Do you have five total people in your group?** *(Multiple choice → Yes / No)* |
| 8‑17 | **Self Evaluation – 10 statements** *(Multiple‑choice grid, 5 columns: Strongly Disagree → Strongly Agree)*<br>• Took initiative in defining the presentation’s objectives and scope.<br>• Contributed original ideas or creative approaches to the presentation content.<br>• Actively sought and incorporated feedback from group members.<br>• Helped resolve disagreements or conflicts constructively.<br>• Demonstrated leadership in organizing meetings, milestones, or resources.<br>• Explained their portion of the material clearly and confidently during the presentation.<br>• Supported the team’s use of visuals, data, or examples to enhance understanding.<br>• Met deadlines for drafts, rehearsals, and slide revisions without reminders.<br>• Adapted flexibly when plans or tasks had to change.<br>• Showed respect for all group members’ opinions and suggestions. |
| 18 | **Any comments or special circumstances that should be considered for this evaluation** *(Paragraph)* |
| 19‑(…repeat) | **Teammate N Evaluation – same 10‑item grid** (duplicated once per teammate; prepend block title "Teammate N Evaluation" so column headers stay unique). |

> **Implementation tip:** In Google Forms choose **“Multiple‑choice grid”** so all 10 statements share the same Likert columns. This yields predictable headers consumed by `peerevalfun.py`.

### 8.2  QP‑2 Presentation Audience Feedback  (one group per submit)

| # | Prompt | Question type |
|---|---------|---------------|
| 1 | **Timestamp** | *(automatic)* |
| 2 | **Your Name** | Short answer |
| 3 | **Presenting Group Number** | *Dropdown* (Group 1, Group 2, …) |
| 4‑10 | **7‑item rating block** *(Multiple‑choice grid, 5 columns: Poor → Excellent or Strongly Disagree → Strongly Agree)*<br>• Background on the known physiology of the problem<br>• Current methods of monitoring / screening / diagnosis and management / treatment in high‑resource and low‑resource settings<br>• Unmet needs for these conditions in high‑ and low‑resource settings<br>• New BME‑related innovations<br>• Quality / innovation of proposed BME solution<br>• Use of schematics and/or pictures<br>• Presentation delivery |
| 11 | **Feedback / Questions** | Paragraph |

Allow **multiple responses** so audience members can submit once per presenting group.

### 8.3  Data‑Processing Assumptions

* All rating grids use the *same 5‑point Likert scale*. The scripts map them case‑insensitively to integers 1–5 (`LIKERT_MAP`).
* Each submission is treated independently; duplicate evaluator names simply indicate multiple evaluations (e.g.
  an audience member rating several groups).
* Timestamps remain in Google Forms’ default "MM/DD/YYYY HH:MM:SS" format, enabling the late‑submission cut‑off to work without edits.

Re‑using this wording verbatim guarantees the exported CSV headers match the patterns expected by **`peerevalfun.py`** and **`audiencegradecount.py`** – so you can copy the forms and *nothing else* in the code needs to change.

---
