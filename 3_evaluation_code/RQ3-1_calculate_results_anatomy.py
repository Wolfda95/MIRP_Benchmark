"""
Script for Evaluating the Model Outputs on Correctness based standard human anatomy vs the provided Image.

Overview:
This script evaluates a model's responses to left/right spatial relation questions by comparing:
1. The model’s predictions on medical images (image-based evaluation).
2. The correct spatial relationships based on standard human anatomy, derived from
   labeled object centers (anatomy-based evaluation).
Three runs (`*_run_0.json`, `*_run_1.json`, `*_run_2.json`) are analyzed.
Accuracy and F1 scores are computed for both evaluation strategies and aggregated across runs.
Results are saved to an Excel file.


Usage:
1. Place the model output files (`*_run_0.json`, `*_run_1.json`, `*_run_2.json`) in a folder called `answers/`.
2. Place the `center_of_anatomical_stuctures_in_standard_radiological_orientation.json` file in the same directory as this script.
    (This file is part of the downloaded MIRP Benchmark dataset.)
    The pathes should look like this: (alternatively, you can change the paths in the main method of the code)
      Base
      ├── RQ3-1_calculate_results_anatomy.py
      ├── center_of_anatomical_stuctures_in_standard_radiological_orientation.json
      └── answers/
          ├── <base>_run_0.json
          ├── <base>_run_1.json
          └── <base>_run_2.json
2. Run the requironment.txt file to install the required packages.
3. Run this script.
4. An Excel file with evaluation results will be saved in the parent directory of `answers/`.


Functionality Summary:
- Model Answer Parsing:
    - Flexible extraction of binary answers from digits, yes/no responses, or partial sentences.
- Evaluation Modes:
    - **Image-based**: Compares model prediction to `expected_answer` field (ground truth from image).
    - **Anatomy-based**: Uses 2D coordinates from reference JSON to determine true spatial relationship.
- Metrics:
    - Per-run: Accuracy, F1 score, count of correct and incorrect predictions.
    - Aggregated: Mean and standard deviation across all runs.

Notes:
- Only left/right spatial questions are evaluated.

"""


import json, os, re, math
from statistics import mean, stdev
from typing import List, Dict, Any

import openpyxl                       # pip install openpyxl
from openpyxl import Workbook
from sklearn.metrics import accuracy_score, f1_score


# ──────────────────────────────────────────────────────────────────────────────
#  Helpers: safe stdev
# ──────────────────────────────────────────────────────────────────────────────
def safe_stdev(vals: List[float]) -> float:
    return stdev(vals) if len(vals) > 1 else 0.0


# ──────────────────────────────────────────────────────────────────────────────
#  Direction fallback & answer parser
# ──────────────────────────────────────────────────────────────────────────────
def parse_spatial_relation(question: str, answer: str) -> int | None:
    q, a = question.lower(), answer.lower()
    pairs = [("above", "below"), ("below", "above"),
             ("left",  "right"), ("right", "left")]
    for d, opp in pairs:
        if d in q:
            if d   in a:  return 1
            if opp in a:  return 0
    return None


def parse_model_answer(ans: str, q: str, prompt: str) -> tuple[int | None, str | None]:
    import re

    def sdigit(s: str) -> str | None:
        m = re.match(r'^[\(\[\{\'\"\.\s]*(0|1)[\)\]\}\'\"\.\s]*$', s.strip())
        return m.group(1) if m else None

    def syesno(s: str) -> str | None:
        m = re.match(r'^[\(\[\{\'\"\.\s]*(yes|no)[\)\]\}\'\"\.\s]*$', s.strip(), re.I)
        return m.group(1).lower() if m else None

    def se_token(s: str) -> str | None:
        t = s.strip()
        m = re.match(r'^[\(\[\{\'\"\.\s]*(0|1|yes|no)', t, re.I) or \
            re.search(r'(0|1|yes|no)[\)\]\}\'\"\.\s]*$', t, re.I)
        return m.group(1).lower() if m else None

    txt = ans.strip()
    # A) single digit
    if (d := sdigit(txt)) in ("0", "1"):
        return int(d), None
    # B) yes/no
    if (y := syesno(txt)) == "yes":
        return 1, None
    if y == "no":
        return 0, None
    # C) token at start/end
    if (t := se_token(txt)):
        return 1 if t in ("1", "yes") else 0, None
    # D) short sentence?
    if ("\n" not in txt) and (len(re.findall(r'[.!?]', txt)) <= 1) and (len(txt) < 150):
        if (sr := parse_spatial_relation(q, txt)) is not None:
            return sr, None
    # E) strip prompt repetitions + heuristics
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
#  Load centre coordinates & name conversion
# ──────────────────────────────────────────────────────────────────────────────
def load_centres(path: str) -> Dict[str, Dict[str, tuple]]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    out: Dict[str, Dict[str, tuple]] = {}
    for e in data:
        out[e["filename"]] = {li["class_name"]: (li["center_x"], li["center_y"])
                              for li in e.get("label_info", [])}
    return out


def canon_name(name: str) -> str:
    name = name.lower().strip()
    parts = name.split()
    if not parts:
        return name
    side = parts[0] if parts[0] in ("left", "right") else None
    base = "_".join(parts[1:] if side else parts)
    return f"{base}_{side}" if side else base


# ──────────────────────────────────────────────────────────────────────────────
#  Evaluate one JSON run file
# ──────────────────────────────────────────────────────────────────────────────
def eval_run(json_path: str,
             centre_map: Dict[str, Dict[str, tuple]]) -> Dict[str, Any]:

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    anat_preds, anat_targs = [], []
    img_preds,  img_targs  = [], []

    anat_corr = anat_wrong = anat_tot = 0
    img_corr  = img_wrong  = img_tot  = 0

    for entry in data:
        fn = entry["file_name"]
        for r in entry["results_call"]:
            q  = r.get("question", "")
            if ("left" not in q.lower()) and ("right" not in q.lower()):
                continue  # only left/right subset

            exp = r.get("expected_answer")
            pa, _ = parse_model_answer(r.get("model_answer", ""), q, r.get("entire_prompt", ""))
            if pa is None:                       # treat unsure as wrong
                pa = 1 - (exp if exp is not None else 1)

            # ── Image view ────────────────────
            if exp is not None:
                img_tot += 1
                img_corr += int(pa == exp)
                img_wrong += int(pa != exp)
                img_preds.append(pa)
                img_targs.append(exp)

            # ── Anatomy view ──────────────────
            obj1 = r.get("object1_name")
            obj2 = r.get("object2_name")
            if not obj1 or not obj2:
                m = re.search(r'is the (.+?) to the (left|right) of the (.+?)\?', q, re.I)
                if m:
                    obj1, obj2 = m.group(1).strip(), m.group(3).strip()
            if fn not in centre_map or not obj1 or not obj2:
                continue
            cm = centre_map[fn]
            k1, k2 = canon_name(obj1), canon_name(obj2)
            if k1 not in cm or k2 not in cm:
                continue
            (cx1, _), (cx2, _) = cm[k1], cm[k2]
            real = 1 if (" to the left of " in q.lower() and cx1 > cx2) or \
                         (" to the right of " in q.lower() and cx1 < cx2) else 0
            anat_tot += 1
            anat_corr += int(pa == real)
            anat_wrong += int(pa != real)
            anat_preds.append(pa)
            anat_targs.append(real)

    # Scores
    anat_acc = accuracy_score(anat_targs, anat_preds) if anat_targs else float('nan')
    anat_f1  = f1_score(anat_targs, anat_preds, zero_division=0) if anat_targs else float('nan')
    img_acc  = accuracy_score(img_targs, img_preds)  if img_targs else float('nan')
    img_f1   = f1_score(img_targs, img_preds, zero_division=0)  if img_targs else float('nan')

    return {
        "anat_acc":          anat_acc,
        "anat_f1":           anat_f1,
        "anat_correct":      anat_corr,
        "anat_incorrect":    anat_wrong,
        "anat_total":        anat_tot,
        "img_acc":           img_acc,
        "img_f1":            img_f1,
        "img_correct":       img_corr,
        "img_incorrect":     img_wrong,
        "img_total":         img_tot
    }


# ──────────────────────────────────────────────────────────────────────────────
#  Aggregate the three runs
# ──────────────────────────────────────────────────────────────────────────────
def aggregate_runs(run_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    def m(lst): return mean(lst) if lst else float('nan')
    def sd(lst): return safe_stdev(lst) if lst else float('nan')

    a_accs  = [r["anat_acc"] for r in run_results]
    a_f1s   = [r["anat_f1"]  for r in run_results]
    i_accs  = [r["img_acc"]  for r in run_results]
    i_f1s   = [r["img_f1"]   for r in run_results]

    return {
        "agg": {
            "anat_acc_mean": m(a_accs), "anat_acc_std": sd(a_accs),
            "anat_f1_mean": m(a_f1s),   "anat_f1_std": sd(a_f1s),
            "img_acc_mean":  m(i_accs), "img_acc_std": sd(i_accs),
            "img_f1_mean":   m(i_f1s),  "img_f1_std":  sd(i_f1s)
        },
        "runs": run_results
    }


# ──────────────────────────────────────────────────────────────────────────────
#  Write Excel (single row)
# ──────────────────────────────────────────────────────────────────────────────
def write_excel(res: Dict[str, Any], out_path: str) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Results"

    hdr = [
        "Anatomy_Accuracy_Mean", "Anatomy_Accuracy_Std",
        "Anatomy_F1_Mean", "Anatomy_F1_Std",
        "",
        "Anatomy_correct_run1", "Anatomy_correct_run2", "Anatomy_correct_run3",
        "Anatomy_incorrect_run1", "Anatomy_incorrect_run2", "Anatomy_incorrect_run3",
        "",
        "Image_Accuracy_Mean", "Image_Accuracy_Std",
        "Image_F1_Mean", "Image_F1_Std"
    ]
    ws.append(hdr)

    a = res["agg"]
    runs = res["runs"]

    def rc(idx, key): return runs[idx][key] if len(runs) > idx else ""

    row = [
        a["anat_acc_mean"], a["anat_acc_std"],
        a["anat_f1_mean"],  a["anat_f1_std"],
        "",
        rc(0, "anat_correct"), rc(1, "anat_correct"), rc(2, "anat_correct"),
        rc(0, "anat_incorrect"), rc(1, "anat_incorrect"), rc(2, "anat_incorrect"),
        "",
        a["img_acc_mean"],  a["img_acc_std"],
        a["img_f1_mean"],   a["img_f1_std"]
    ]
    ws.append(row)
    wb.save(out_path)
    print(f"Excel saved → {out_path}")


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
    centres_js = "center_of_anatomical_stuctures_in_standard_radiological_orientation.json"
    # Download this json file.
    # It contains the coordinates of the anatomical structures of the images in standard radiological view.
    # It is used to determine the anatomical correctness of the answers.
    # ─────────────────────────────────────────────────────────────────────────

    if not os.path.isdir(answer_files_dir):
        raise FileNotFoundError(f"Answers directory not found: {answer_files_dir}")
    if not os.path.isfile(centres_js):
        raise FileNotFoundError(f"Centres JSON not found: {centres_js}")

    centre_map = load_centres(centres_js)

    # collect all *_run_<n>.json files inside answer_files_dir
    json_files = [os.path.join(answer_files_dir, f)
                  for f in os.listdir(answer_files_dir)
                  if f.endswith(".json") and not f.startswith("Result_")]
    if not json_files:
        raise RuntimeError("No run JSON files found in the Answers directory.")

    # group by base using "…_run_<n>.json" pattern
    grouped: Dict[str, List[str]] = {}
    pat = re.compile(r'^(.*)_run_(\d+)\.json$', re.I)
    for fp in json_files:
        m = pat.match(os.path.basename(fp))
        if not m:
            raise RuntimeError(f"File does not match '*_run_<n>.json' pattern: {fp}")
        grouped.setdefault(m.group(1), []).append(fp)

    parent_dir = os.path.dirname(answer_files_dir)  # one level up for output

    for base_name, run_paths in grouped.items():
        run_paths = sorted(run_paths)  # ensure run_0, run_1, run_2 order
        run_results = [eval_run(p, centre_map) for p in run_paths]
        agg_res = aggregate_runs(run_results)

        # filename: generic if only one base, else include base name
        if len(grouped) == 1:
            out_name = "Results_Anatomy-vs-Image_Left-Right-Questions.xlsx"
        else:
            out_name = f"Results_{base_name}_Anatomy-vs-Image_Left-Right-Questions.xlsx"

        out_xlsx = os.path.join(parent_dir, out_name)
        write_excel({"agg": agg_res["agg"], "runs": run_results}, out_xlsx)


if __name__ == "__main__":
    main()
