import json
import re
import os
import math
from statistics import mean, stdev
from typing import List, Dict, Any
#import openpyxl
from openpyxl import Workbook
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

###############################################################################
# 1) Spatial Relation Fallback (IDENTICAL TO YOUR ORIGINAL)
###############################################################################
def parse_spatial_relation(question: str, answer: str) -> int or None:
    """
    As a fallback, detect direction words in question & answer.
    We handle these pairs: (above/below) and (left/right).

      - If Q says "above" and A says "above" => 1
      - If Q says "above" and A says "below" => 0
      - If Q says "below" and A says "below" => 1
      - If Q says "below" and A says "above" => 0
      - If Q says "left"  and A says "left"  => 1
      - If Q says "left"  and A says "right" => 0
      - If Q says "right" and A says "right" => 1
      - If Q says "right" and A says "left"  => 0

    Returns 1 or 0 if found, else None if we can't decide.
    """
    q_lower = question.lower()
    a_lower = answer.lower()

    directions = [
        ("above", "below"),
        ("below", "above"),
        ("left", "right"),
        ("right", "left"),
    ]
    for dir_q, dir_opposite in directions:
        if dir_q in q_lower:
            if dir_q in a_lower:
                return 1
            if dir_opposite in a_lower:
                return 0
    return None

###############################################################################
# 2) Main Parser (IDENTICAL TO YOUR ORIGINAL)
###############################################################################
def parse_model_answer(
    model_answer: str,
    question: str,
    entire_prompt: str
) -> (int or None, str or None):
    """
    Returns a tuple: (parse_result, leftover_text_after_prompt_removal)

    parse_result: int (0 or 1) or None
    leftover_text_after_prompt_removal: str or None

    Steps:

    A) If the entire answer is effectively just a single digit '0'/'1'
       ignoring punctuation, return that.

    B) Otherwise, if the entire answer is effectively just "yes" or "no"
       ignoring punctuation/case, return 1 or 0.

    C) Check if the answer starts or ends (ignoring punctuation) with
       '0'/'1' or 'yes'/'no'. If found, return that.

    D) If none of these matched, check if the answer is a "single short sentence"
       with no extra text. If so, we call parse_spatial_relation(question, text).
       If that returns 0 or 1, we use it.

    E) Finally, if none of these matched:
       - Remove repeated lines from entire_prompt if they appear in the answer.
       - Then take the first remaining sentence from the cleaned answer,
         call parse_spatial_relation(question, first_sentence).
         If that returns 0/1, we return it (with leftover_text).
       - If still nothing, look for phrases like "answer is: 1", "correct answer: 0", etc.
         Return 1 or 0 if found, else None => forced incorrect.
       - leftover_text = cleaned_text
    """
    import re

    def single_digit_ignoring_punct(s: str) -> str or None:
        s = s.strip()
        pattern = re.compile(r'^[\(\[\{\'\"\.\s]*(0|1)[\)\]\}\'\"\.\s]*$')
        m = pattern.match(s)
        if m:
            return m.group(1)  # '0' or '1'
        return None

    def single_yes_no_ignoring_punct(s: str) -> str or None:
        s = s.strip().lower()
        pattern = re.compile(r'^[\(\[\{\'\"\.\s]*(yes|no)[\)\]\}\'\"\.\s]*$')
        m = pattern.match(s)
        if m:
            return m.group(1)  # 'yes' or 'no'
        return None

    def starts_or_ends_with_digit_or_yesno(s: str) -> str or None:
        s_stripped = s.strip()
        # starts...
        start_pattern = re.compile(r'^[\(\[\{\'\"\.\s]*(0|1|yes|no)', re.IGNORECASE)
        m_start = start_pattern.match(s_stripped)
        if m_start:
            return m_start.group(1).lower()
        # ends...
        end_pattern = re.compile(r'(0|1|yes|no)[\)\]\}\'\"\.\s]*$', re.IGNORECASE)
        m_end = end_pattern.search(s_stripped)
        if m_end:
            return m_end.group(1).lower()
        return None

    def is_single_short_sentence(s: str) -> bool:
        """Heuristic: one short sentence => no newline, <=1 punctuation [.!?], length <150 chars."""
        s = s.strip()
        if "\n" in s:
            return False

        sentence_punc = re.findall(r'[.!?]', s)
        if len(sentence_punc) > 1:
            return False

        if len(s) > 150:
            return False

        return True

    def parse_spatial_relation_fallback(question: str, answer: str) -> int or None:
        q_lower = question.lower()
        a_lower = answer.lower()
        directions = [
            ("above", "below"),
            ("below", "above"),
            ("left", "right"),
            ("right", "left"),
        ]
        for dir_q, dir_opposite in directions:
            if dir_q in q_lower:
                if dir_q in a_lower:
                    return 1
                if dir_opposite in a_lower:
                    return 0
        return None

    text = model_answer.strip()

    # ================== A ===================
    maybe_digit = single_digit_ignoring_punct(text)
    if maybe_digit in ["0", "1"]:
        return int(maybe_digit), None

    # ================== B ===================
    maybe_yesno = single_yes_no_ignoring_punct(text)
    if maybe_yesno == "yes":
        return 1, None
    if maybe_yesno == "no":
        return 0, None

    # ================== C ===================
    start_end = starts_or_ends_with_digit_or_yesno(text)
    if start_end is not None:
        if start_end in ["0", "no"]:
            return 0, None
        if start_end in ["1", "yes"]:
            return 1, None

    # ================== D ===================
    if is_single_short_sentence(text):
        sr = parse_spatial_relation_fallback(question, text)
        if sr is not None:
            return sr, None

    # ================== E ===================
    cleaned_text = text
    prompt_lines = entire_prompt.splitlines()
    for pline in prompt_lines:
        pline_stripped = pline.strip()
        if pline_stripped:
            while pline_stripped in cleaned_text:
                cleaned_text = cleaned_text.replace(pline_stripped, "")

    first_sentence_match = re.search(r'[^.!?]+[.!?]?', cleaned_text)
    if first_sentence_match:
        first_sentence = first_sentence_match.group(0).strip()
        sr2 = parse_spatial_relation_fallback(question, first_sentence)
        if sr2 is not None:
            return sr2, cleaned_text  # partial leftover

    number_pattern = re.compile(
        r'''
        (?:
          \banswer\b
          | \bcorrect\s+answer\b
          | \bfinal\s+answer\b
          | \bsolution\b
          | \bresponse\b
          | \bthe\s+answer\b
          | \bthe\s+correct\s+answer\b
          | \bthe\s+final\s+answer\b
          | \btherefore\s+the\s+answer\b
          | \bhence\s+the\s+answer\b
        )
        (?:\s+is\s*|\s*\:\s*|\s+)(?:["']?)
        ([10])
        (?:["']?\b)
        ''',
        re.IGNORECASE | re.VERBOSE
    )
    match_any_answer = number_pattern.search(cleaned_text)
    if match_any_answer:
        digit = match_any_answer.group(1)
        return (1 if digit == '1' else 0), cleaned_text

    return None, cleaned_text

###############################################################################
# 3A) Load Non-Rotated Centers & transform object names for left/right logic
###############################################################################
def load_nonrotated_centers(json_path):
    """
    Returns a dict:
      {
        "img0061.nii_slice-100_classes-24_perc-18.png": {
          "kidney_left": (361.17, 317.88),
          "liver":       (193.34, 221.87),
          ...
        },
        ...
      }
    """
    with open(json_path,"r", encoding="utf-8") as f:
        data = json.load(f)

    out_map = {}
    for entry in data:
        fn = entry["filename"]
        label_info = entry.get("label_info", [])
        obj_map = {}
        for li in label_info:
            cname = li["class_name"]  # e.g. "kidney_left"
            cx    = li["center_x"]
            cy    = li["center_y"]
            obj_map[cname] = (cx, cy)
        out_map[fn] = obj_map
    return out_map

def invert_transform_name(name: str) -> str:
    """
    E.g. from question: "left kidney" => "kidney_left"
         from question: "right autochthon" => "autochthon_right"
    We'll guess by scanning for 'left'/'right' as the first word, then
    appending '_left'/'_right'.
    We'll also remove spaces in the remaining portion => e.g. "kidney".
    """
    original = name
    name = name.lower().strip()
    parts = name.split()
    if not parts:
        return original

    side = None
    if parts[0] in ("left","right"):
        side = parts[0]
        parts = parts[1:]

    base = "_".join(parts)
    if side:
        return f"{base}_{side}"
    else:
        return base

###############################################################################
# 3B) Evaluate JSON File => *only left/right* => check real coords
###############################################################################
def evaluate_json_file(
    json_path: str,
    center_map: Dict[str, Dict[str, tuple]]
) -> Dict[str, Any]:
    """
    Evaluate a single JSON file, but we skip everything except LEFT/RIGHT questions.
    1) parse model's answer with parse_model_answer
    2) see if question has 'left' or 'right'
    3) find object1_name, object2_name from the JSON or a naive regex
    4) look up their center_x in the *non-rotated* center_map
    5) bigger x => more left in real body
       => if question is "to the left of", real correct answer => (cx1>cx2)
       => if question is "to the right of", real correct answer => (cx1<cx2)
    6) compare that real correctness with the model's parse => if match => correct
    """
    #from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_predictions = []
    all_targets = []

    correct_count = 0
    incorrect_count = 0
    unsure_count = 0
    unsure_cases = []

    for entry in data:
        file_name = entry["file_name"]
        calls = entry.get("results_call", [])

        for result in calls:
            question = result.get("question","")
            entire_prompt = result.get("entire_prompt","")
            model_answer = result.get("model_answer","")

            # We skip if the question doesn't mention "left" or "right"
            q_lower = question.lower()
            if ("left" not in q_lower) and ("right" not in q_lower):
                # skip => no stats
                continue

            # parse the model's answer => 'parsed' in {0,1} or None
            parsed, leftover = parse_model_answer(
                model_answer, question, entire_prompt
            )
            if parsed is None:
                unsure_count += 1
                sample_dict = {
                    "file_name": file_name,
                    "question": question,
                    "model_answer": model_answer,
                }
                if leftover:
                    sample_dict["step_e_cleaned_text"] = leftover
                unsure_cases.append(sample_dict)
                continue

            obj1_qname = result.get("object1_name")
            obj2_qname = result.get("object2_name")

            if not obj1_qname or not obj2_qname:
                # fallback => naive regex
                pattern = r"is the (.+?) to the (left|right) of the (.+?)\?"
                m = re.search(pattern, question.lower())
                if m:
                    obj1_qname = m.group(1).strip()
                    obj2_qname = m.group(3).strip()
                else:
                    unsure_count += 1
                    continue

            obj1_cname = invert_transform_name(obj1_qname)
            obj2_cname = invert_transform_name(obj2_qname)

            if file_name not in center_map:
                unsure_count += 1
                continue
            if (obj1_cname not in center_map[file_name]) or (obj2_cname not in center_map[file_name]):
                unsure_count += 1
                continue

            (cx1, cy1) = center_map[file_name][obj1_cname]
            (cx2, cy2) = center_map[file_name][obj2_cname]

            q_l = question.lower()
            is_left_q = (" to the left of " in q_l)
            is_right_q= (" to the right of " in q_l)

            if not (is_left_q or is_right_q):
                unsure_count += 1
                continue

            if is_left_q:
                real_truth = 1 if (cx1>cx2) else 0
            else:
                real_truth = 1 if (cx1<cx2) else 0

            is_correct = (real_truth == parsed)
            if is_correct:
                correct_count += 1
            else:
                incorrect_count += 1

            all_targets.append(real_truth)
            all_predictions.append(parsed)

    # Now compute accuracy/f1/auc
    if len(all_targets)==0:
        accuracy = 0.0
        f1 = 0.0
        auc_val = float('nan')
    else:
        accuracy = accuracy_score(all_targets, all_predictions)
        f1 = f1_score(all_targets, all_predictions, zero_division=0)
        # We do not calculate actual AUC; set it to NaN:
        auc_val = float('nan')

    return {
        "accuracy": accuracy,
        "f1_score": f1,
        "auc": auc_val,
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "unsure_count": unsure_count,
        "unparseable_samples": unsure_cases,
        "all_predictions": all_predictions,
        "all_targets": all_targets
    }

###############################################################################
# 4) Summaries, Aggregation, & File Operations (IDENTICAL TO YOUR ORIGINAL)
###############################################################################
def safe_stdev(values: List[float]) -> float:
    """Returns stdev(values) if len(values) > 1, else 0."""
    if len(values) > 1:
        return stdev(values)
    else:
        return 0.0

def process_runs_for_base(
        base_name: str,
        run_files: List[str],
        model_name: str,
        center_map: Dict[str, Dict[str, tuple]]
) -> Dict[str, Any]:
    """
    Evaluates each JSON in run_files (all belong to the same base_name),
    collects the metrics, then computes mean & stdev for Accuracy, F1, AUC.
    We pass 'center_map' to evaluate_json_file so it can do left/right checking.
    """
    from statistics import mean

    run_metrics = []
    for jf in run_files:
        res = evaluate_json_file(jf, center_map)
        run_metrics.append({
            "file_path": jf,
            **res
        })

    accs = [rm["accuracy"] for rm in run_metrics]
    f1s = [rm["f1_score"] for rm in run_metrics]
    aucs = [rm["auc"] for rm in run_metrics]

    if len(accs)>0:
        accuracy_mean = mean(accs)
        accuracy_std = safe_stdev(accs)
    else:
        accuracy_mean = 0.0
        accuracy_std = 0.0

    if len(f1s)>0:
        f1_mean = mean(f1s)
        f1_std = safe_stdev(f1s)
    else:
        f1_mean = 0.0
        f1_std = 0.0

    valid_aucs = [a for a in aucs if not math.isnan(a)]
    if len(valid_aucs) == 0:
        auc_mean = float('nan')
        auc_std = float('nan')
    else:
        auc_mean = mean(valid_aucs)
        if len(valid_aucs) > 1:
            auc_std = stdev(valid_aucs)
        else:
            auc_std = 0.0

    return {
        "base_name": base_name,
        "run_metrics": run_metrics,
        "aggregated": {
            "accuracy_mean": accuracy_mean,
            "accuracy_std": accuracy_std,
            "f1_mean": f1_mean,
            "f1_std": f1_std,
            "auc_mean": auc_mean,
            "auc_std": auc_std
        }
    }

def save_combined_json(
        s1: str,
        s2: str,
        base_name: str,
        model_name: str,
        combined_data: Dict[str, Any],
        out_dir: str
) -> None:
    """
    Saves a single JSON file with all runs + aggregated stats into
    'out_dir' (but let's place them in an extra subfolder).
      The file name => Result_<model_name>_<base_name>_summary.json
    """
    import os

    # create an extra subfolder in out_dir = e.g. out_dir + "/LeftRightEval"
    extra_folder = os.path.join(out_dir, "LeftRightEval")
    os.makedirs(extra_folder, exist_ok=True)

    output = {
        "subfolder_one": s1,
        "subfolder_two": s2,
        "base_name": base_name,
        "model_name": model_name,
        "run_metrics": combined_data["run_metrics"],
        "aggregated": combined_data["aggregated"]
    }

    filename = f"Result_{model_name}_{base_name}_summary.json"
    out_path = os.path.join(extra_folder, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

def gather_json_files(
        base_path: str,
        subfolder_one: List[str],
        subfolder_two: List[str]
) -> Dict[tuple, List[str]]:
    """
    Returns a dict mapping (s1, s2) -> list of JSON file paths in that subfolder.
    We skip those that start with "Result_".
    """
    collected = {}
    for s1 in subfolder_one:
        for s2 in subfolder_two:
            path = os.path.join(base_path, s1, s2)
            if not os.path.isdir(path):
                continue
            json_files = []
            for fn in os.listdir(path):
                if fn.lower().endswith(".json") and not fn.startswith("Result_"):
                    json_files.append(os.path.join(path, fn))
            collected[(s1, s2)] = json_files
    return collected

def group_by_run(json_files: List[str]) -> Dict[str, List[str]]:
    """
    Groups JSON files by their 'base name' ignoring a pattern _run_x.
    Example:
       my_experiment_run_1.json -> base_name = 'my_experiment'
       my_experiment_run_2.json -> same base_name = 'my_experiment'
    """
    grouped = {}
    pattern = re.compile(r'^(.*)_run_(\d+)\.json$', re.IGNORECASE)

    for file_path in json_files:
        fn = os.path.basename(file_path)
        match = pattern.match(fn)
        if match:
            base = match.group(1)
        else:
            base = fn[:-5] if fn.lower().endswith(".json") else fn

        if base not in grouped:
            grouped[base] = []
        grouped[base].append(file_path)

    return grouped

###############################################################################
# 5) Excel Summary (IDENTICAL TO YOUR ORIGINAL, except for requested changes)
###############################################################################
def write_excel_summary(
        results_summary: List[Dict[str, Any]],
        output_excel_path: str
) -> None:
    """
    Writes all aggregated results into a single Excel file.
    One row per (subfolder_one, subfolder_two, base_name).
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Results"

    # Remove subfolder_one, subfolder_two, base_name, AUC columns;
    # Only 3 runs and add an empty column before correct/incorrect/unsure.
    # Now we also remove the unsure columns entirely.
    header = [
        "subfolder_one",
        "Accuracy_Mean", "Accuracy_Std",
        "F1_Mean", "F1_Std",
        "",  # empty column
        "correct_run1", "correct_run2", "correct_run3",
        "incorrect_run1", "incorrect_run2", "incorrect_run3",
    ]
    ws.append(header)

    for item in results_summary:
        row = [
            item["subfolder_one"],
            item["aggregated"]["accuracy_mean"],
            item["aggregated"]["accuracy_std"],
            item["aggregated"]["f1_mean"],
            item["aggregated"]["f1_std"],
            "",  # empty column
        ]

        run_metrics = item["run_metrics"]
        run_count = len(run_metrics)

        # correct
        for i in range(3):
            if i < run_count:
                row.append(run_metrics[i]["correct_count"])
            else:
                row.append("")
        # incorrect
        for i in range(3):
            if i < run_count:
                row.append(run_metrics[i]["incorrect_count"])
            else:
                row.append("")

        ws.append(row)

    wb.save(output_excel_path)
    print(f"Excel summary saved at: {output_excel_path}")

###############################################################################
# 6) MAIN
###############################################################################
def main():

    # ToDo: Adjust the Pathes: 
    # 1) Path to the json with the center-of-masses of the non-rotated images
    nonrotated_centers_json_path = "./2_evaluation_anatomy//Anatomy_Center-of_Mass.json"
    # 2) where the model answers are (In there should be 4 subfolders: AS, RQ1, RQ2, RQ3)
    base_path = "./2_evaluation_anatomy/model_answers/"

    # We load the center map once
    center_map = load_nonrotated_centers(nonrotated_centers_json_path)

    # We gather all model answer JSON files from subfolders
    subfolder_one = ['GPT4o', 'JanusPro', 'Llama', 'Pixtral']
    # example subfolders:
    subfolder_two = ['None']

    all_json_files = gather_json_files(base_path, subfolder_one, subfolder_two)

    # We'll store a list of aggregated results to write into Excel
    excel_summary_rows = []

    # For each (s1, s2) subfolder pair => group by base_name => evaluate
    for (s1, s2), json_list in all_json_files.items():
        if not json_list:
            continue

        grouped = group_by_run(json_list)
        for base_name, run_files in grouped.items():
            combined_data = process_runs_for_base(base_name, run_files, model_name=f"{s1}_{s2}", center_map=center_map)
            out_dir = os.path.dirname(run_files[0])
            # We keep the call below commented as in the original flow;
            # it is unchanged. Uncomment if needed:
            # save_combined_json(s1, s2, base_name, f"{s1}_{s2}", combined_data, out_dir)

            summary_row = {
                "subfolder_one": s1,
                "subfolder_two": s2,
                "base_name": base_name,
                "aggregated": combined_data["aggregated"],
                "run_metrics": combined_data["run_metrics"]
            }
            excel_summary_rows.append(summary_row)

    # Finally write the Excel summary
    excel_path = os.path.join(base_path, "Results_Annatomy.xlsx")
    write_excel_summary(excel_summary_rows, excel_path)

if __name__ == "__main__":
    main()
