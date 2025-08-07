"""
Script for Evaluating the Model Outputs on Correctness based on the provided Image.

Overview:
This script evaluates the predictions of a single model on a specific task
across three separate runs. It computes accuracy, F1 score, and counts of correct,
incorrect, and uncertain predictions. The aggregated results are saved to an Excel file.


Usage:
1. Place the model output files (`*_run_0.json`, `*_run_1.json`, `*_run_2.json`) in a folder called `answers/`.
    The pathes should look like this: (alternatively, you can change the paths in the main method of the code)
      Base
      ├── RQ1_RQ2_RQ3-2_calculate_results_image.py
      └── answers/
          ├── <base>_run_0.json
          ├── <base>_run_1.json
          └── <base>_run_2.json
2. Run the requironment.txt file to install the required packages.
3. Run this script.
4. An Excel file with evaluation results will be saved in the parent directory of `answers/`.


Functionality Summary:
- The model answer is parsed using flexible heuristics to extract binary (0/1) or yes/no responses.
- If the answer cannot be parsed, the script assumes it is incorrect (but records it as "unsure").
- Accuracy and F1 scores are computed per run and averaged across all three runs.
"""

import json, os, re
from statistics import mean, stdev
from typing import List, Dict, Any

import openpyxl                    # pip install openpyxl
from openpyxl import Workbook
from sklearn.metrics import accuracy_score, f1_score


# ──────────────────────────────────────────────────────────────────────────────
#  Basic helpers: safe stdev
# ──────────────────────────────────────────────────────────────────────────────
def safe_stdev(x: List[float]) -> float:
    return stdev(x) if len(x) > 1 else 0.0


# ──────────────────────────────────────────────────────────────────────────────
#  Fallback direction parser & answer heuristics
# ──────────────────────────────────────────────────────────────────────────────
def parse_spatial_relation(q: str, a: str) -> int | None:
    ql, al = q.lower(), a.lower()
    for d, opp in [("above", "below"), ("below", "above"),
                   ("left", "right"), ("right", "left")]:
        if d in ql:
            if d in al:   return 1
            if opp in al: return 0
    return None


def parse_model_answer(ans: str, q: str, prompt: str) -> tuple[int | None, str | None]:
    import re

    def sdigit(s: str) -> str | None:
        m = re.fullmatch(r'[\(\[\{\'\"\.\s]*(0|1)[\)\]\}\'\"\.\s]*', s.strip())
        return m.group(1) if m else None

    def syesno(s: str) -> str | None:
        m = re.fullmatch(r'[\(\[\{\'\"\.\s]*(yes|no)[\)\]\}\'\"\.\s]*', s.strip(), re.I)
        return m.group(1).lower() if m else None

    def se_token(s: str) -> str | None:
        m = re.match(r'^[\(\[\{\'\"\.\s]*(0|1|yes|no)', s.strip(), re.I)
        if m: return m.group(1).lower()
        m = re.search(r'(0|1|yes|no)[\)\]\}\'\"\.\s]*$', s.strip(), re.I)
        return m.group(1).lower() if m else None

    txt = ans.strip()

    if (d := sdigit(txt)) in ("0", "1"):
        return int(d), None
    if (yn := syesno(txt)) in ("yes", "no"):
        return 1 if yn == "yes" else 0, None
    if (tok := se_token(txt)) is not None:
        return 1 if tok in ("1", "yes") else 0, None
    if ("\n" not in txt) and (len(re.findall(r'[.!?]', txt)) <= 1) and (len(txt) < 150):
        if (sr := parse_spatial_relation(q, txt)) is not None:
            return sr, None

    # strip prompt lines
    cleaned = txt
    for l in prompt.splitlines():
        ls = l.strip()
        if ls:
            cleaned = cleaned.replace(ls, "")
    m = re.search(r'[^.!?]+[.!?]?', cleaned)
    if m and (sr2 := parse_spatial_relation(q, m.group(0).strip())) is not None:
        return sr2, cleaned
    m = re.search(r'(?:answer|correct answer|final answer|solution|response)'
                  r'(?: is|:)?\s*([10])', cleaned, re.I)
    if m:
        return 1 if m.group(1) == "1" else 0, cleaned
    return None, cleaned


# ──────────────────────────────────────────────────────────────────────────────
#  Evaluate ONE run file
# ──────────────────────────────────────────────────────────────────────────────
def evaluate_run(json_path: str) -> Dict[str, Any]:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    preds, targs = [], []
    correct = incorrect = unsure = 0

    for entry in data:
        for call in entry["results_call"]:
            exp = call["expected_answer"]          # 0/1 ground truth
            pred, _ = parse_model_answer(call["model_answer"],
                                         call.get("question", ""),
                                         call.get("entire_prompt", ""))
            if pred is None:                       # treat unsure as WRONG
                pred = 1 - exp
                unsure += 1
            if pred == exp:
                correct += 1
            else:
                incorrect += 1
            preds.append(pred)
            targs.append(exp)

    acc = accuracy_score(targs, preds)
    f1  = f1_score(targs, preds, zero_division=0)

    return {
        "accuracy":       acc,
        "f1":             f1,
        "correct_count":  correct,
        "incorrect_count": incorrect,
        "unsure_count":   unsure
    }


# ──────────────────────────────────────────────────────────────────────────────
#  Aggregate three runs of the same experiment
# ──────────────────────────────────────────────────────────────────────────────
def process_runs(run_files: List[str]) -> Dict[str, Any]:
    run_metrics = [evaluate_run(fp) for fp in run_files]

    accs = [rm["accuracy"] for rm in run_metrics]
    f1s  = [rm["f1"]       for rm in run_metrics]

    aggregated = {
        "accuracy_mean": mean(accs), "accuracy_std": safe_stdev(accs),
        "f1_mean":       mean(f1s),  "f1_std":       safe_stdev(f1s)
    }
    return {"aggregated": aggregated, "run_metrics": run_metrics}


# ──────────────────────────────────────────────────────────────────────────────
#  Excel helpers
# ──────────────────────────────────────────────────────────────────────────────
HEADER = [
    "Accuracy_Mean", "Accuracy_Std",
    "F1_Mean", "F1_Std",
    "",
    "correct_run1",   "correct_run2",   "correct_run3",
    "incorrect_run1", "incorrect_run2", "incorrect_run3",
    "unsure_run1",    "unsure_run2",    "unsure_run3"
]


def write_excel_row(ws, agg: Dict[str, Any], runs: List[Dict[str, Any]]):
    def rget(idx, key): return runs[idx][key] if len(runs) > idx else ""
    row = [
        agg["accuracy_mean"], agg["accuracy_std"],
        agg["f1_mean"],       agg["f1_std"],
        "",
        rget(0, "correct_count"),   rget(1, "correct_count"),   rget(2, "correct_count"),
        rget(0, "incorrect_count"), rget(1, "incorrect_count"), rget(2, "incorrect_count"),
        rget(0, "unsure_count"),    rget(1, "unsure_count"),    rget(2, "unsure_count")
    ]
    ws.append(row)


# ──────────────────────────────────────────────────────────────────────────────
#  Group run files by their base name
# ──────────────────────────────────────────────────────────────────────────────
def group_by_base(files: List[str]) -> Dict[str, List[str]]:
    grouped: Dict[str, List[str]] = {}
    pat = re.compile(r'^(.*)_run_\d+\.json$', re.I)
    for fp in files:
        base = pat.match(os.path.basename(fp)).group(1)
        grouped.setdefault(base, []).append(fp)
    return grouped


# ──────────────────────────────────────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    # Update the paths below to your local setup
    # ── Paths  ─────────────────────────────────────
    answer_files_dir = "./answers"
    # Needs to contain 3 json files with the model answers for each of the 3 runs. They should end with ..._run_0.json, ..._run_1.json, ..._run_2.json.
    # Each element of all 3 json files should have this structure:
    #  {
    #         "file_name": "amos_0002.nii_slice-20_classes-22_perc-12.png",
    #         "results_call": [
    #             {
    #                 "question": "Is the left kidney below the inferior vena cava?",
    #                 "model_answer": "0",
    #                 "expected_answer": 0,
    #                 "entire_prompt": "The image is a 2D axial slice of an abdominal CT scan with soft tissue windowing. Answer strictly with '1' for Yes or '0' for No. No explanations, no additional text. Your output must contain exactly one character: '1' or '0'.Ignore anatomical correctness; focus solely on what the image shows.\nExample:\nQ: Is the left iliopsoas below the left gluteus maximus? A: 1\nNow answer the real question:\n\nQ: Is the left kidney below the inferior vena cava?"
    #             }
    #         ]
    # ─────────────────────────────────────────────────────────────────────────

    if not os.path.isdir(answer_files_dir):
        raise FileNotFoundError(f"Answers directory not found: {answer_files_dir}")

    json_files = [os.path.join(answer_files_dir, f)
                  for f in os.listdir(answer_files_dir)
                  if f.lower().endswith(".json")]
    if not json_files:
        raise RuntimeError("No *.json files found in the Answers directory.")

    grouped = group_by_base(json_files)
    parent  = os.path.abspath(os.path.join(answer_files_dir, os.pardir))

    for base, run_paths in grouped.items():
        run_paths = sorted(run_paths)  # ensure run_0, run_1, run_2 order
        res = process_runs(run_paths)

        wb = Workbook()
        ws = wb.active
        ws.title = "Results"
        ws.append(HEADER)
        write_excel_row(ws, res["aggregated"], res["run_metrics"])

        out_name = ("Results_Image.xlsx"
                    if len(grouped) == 1
                    else f"Results_{base}_Image.xlsx")
        out_path = os.path.join(parent, out_name)
        wb.save(out_path)
        print(f"✓  {out_path} written")

if __name__ == "__main__":
    main()
