import json
import re
import os
import math
from statistics import mean, stdev
from typing import List, Dict, Any
#import openpyxl
from openpyxl import Workbook
from sklearn.metrics import accuracy_score, f1_score


###############################################################################
# 1) Spatial Relation Fallback
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
# 2) Main Parser
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

    def parse_spatial_relation(question: str, answer: str) -> int or None:
        # Copied here for self-containment; or import from above
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
        sr = parse_spatial_relation(question, text)
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
        sr2 = parse_spatial_relation(question, first_sentence)
        if sr2 is not None:
            return sr2, cleaned_text

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
# 3) Evaluate JSON File
###############################################################################
def evaluate_json_file(json_path: str) -> Dict[str, Any]:
    """
    Evaluate a single JSON file, returning a dictionary with
    all metrics + unparseable samples. DOES NOT save results to disk.

    Additionally, we compute partial metrics for:
      - left/right questions
      - above/below questions
    and store them in the returned dictionary as well.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_predictions = []
    all_targets = []

    # For partial sets:
    lr_predictions = []
    lr_targets = []
    ab_predictions = []
    ab_targets = []

    correct_count = 0
    incorrect_count = 0
    unsure_count = 0
    unsure_cases = []

    for entry in data:
        for result in entry["results_call"]:
            model_answer = result["model_answer"]
            question = result.get("question", "")
            entire_prompt = result.get("entire_prompt", "")
            expected = result["expected_answer"]  # 1=yes, 0=no

            parsed, leftover = parse_model_answer(model_answer, question, entire_prompt)

            if parsed is None:
                # forced incorrect
                pred = 1 - expected
                unsure_count += 1

                sample_dict = {
                    "file_name": entry["file_name"],
                    "question": question,
                    "expected_answer": expected,
                    "model_answer": model_answer
                }
                if leftover:
                    sample_dict["step_e_cleaned_text"] = leftover

                unsure_cases.append(sample_dict)
            else:
                pred = parsed
                if leftover:
                    result["step_e_cleaned_text"] = leftover

            all_predictions.append(pred)
            all_targets.append(expected)

            # Check if it's left/right question
            q_lower = question.lower()
            if ("left" in q_lower) or ("right" in q_lower):
                lr_predictions.append(pred)
                lr_targets.append(expected)

            # Check if it's above/below question
            if ("above" in q_lower) or ("below" in q_lower):
                ab_predictions.append(pred)
                ab_targets.append(expected)

            if pred == expected:
                correct_count += 1
            else:
                incorrect_count += 1

    accuracy = accuracy_score(all_targets, all_predictions)
    f1_val = f1_score(all_targets, all_predictions, zero_division=0)

    # Partial: left/right
    if len(lr_targets) == 0:
        accuracy_lr = float('nan')
        f1_lr = float('nan')
    else:
        accuracy_lr = accuracy_score(lr_targets, lr_predictions)
        f1_lr = f1_score(lr_targets, lr_predictions, zero_division=0)

    # Partial: above/below
    if len(ab_targets) == 0:
        accuracy_ab = float('nan')
        f1_ab = float('nan')
    else:
        accuracy_ab = accuracy_score(ab_targets, ab_predictions)
        f1_ab = f1_score(ab_targets, ab_predictions, zero_division=0)

    return {
        "accuracy": accuracy,
        "f1_score": f1_val,

        "accuracy_lr": accuracy_lr,
        "f1_lr": f1_lr,

        "accuracy_ab": accuracy_ab,
        "f1_ab": f1_ab,

        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "unsure_count": unsure_count,
        "unparseable_samples": unsure_cases,
        "all_predictions": all_predictions,
        "all_targets": all_targets
    }


###############################################################################
# 4) Summaries, Aggregation, & File Operations
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
        model_name: str
) -> Dict[str, Any]:
    """
    Evaluates each JSON in run_files (all belong to the same base_name),
    collects the metrics, then computes mean & stdev for Accuracy, F1.

    Also does the same for partial sets:
      - left/right questions
      - above/below questions
    """
    run_metrics = []
    for jf in run_files:
        res = evaluate_json_file(jf)
        run_metrics.append({
            "file_path": jf,
            **res
        })

    # Gather arrays for the overall metrics
    accs = [rm["accuracy"] for rm in run_metrics]
    f1s = [rm["f1_score"] for rm in run_metrics]

    # left/right partial
    accs_lr = [rm["accuracy_lr"] for rm in run_metrics]
    f1s_lr = [rm["f1_lr"] for rm in run_metrics]

    # above/below partial
    accs_ab = [rm["accuracy_ab"] for rm in run_metrics]
    f1s_ab = [rm["f1_ab"] for rm in run_metrics]

    # Overall
    accuracy_mean = mean(accs) if accs else float('nan')
    accuracy_std = safe_stdev(accs) if accs else float('nan')
    f1_mean = mean(f1s) if f1s else float('nan')
    f1_std = safe_stdev(f1s) if f1s else float('nan')

    # Left/Right partial
    valid_accs_lr = [a for a in accs_lr if not math.isnan(a)]
    if len(valid_accs_lr) == 0:
        accuracy_lr_mean = float('nan')
        accuracy_lr_std = float('nan')
    else:
        accuracy_lr_mean = mean(valid_accs_lr)
        accuracy_lr_std = safe_stdev(valid_accs_lr)

    valid_f1s_lr = [f for f in f1s_lr if not math.isnan(f)]
    if len(valid_f1s_lr) == 0:
        f1_lr_mean = float('nan')
        f1_lr_std = float('nan')
    else:
        f1_lr_mean = mean(valid_f1s_lr)
        f1_lr_std = safe_stdev(valid_f1s_lr)

    # Above/Below partial
    valid_accs_ab = [a for a in accs_ab if not math.isnan(a)]
    if len(valid_accs_ab) == 0:
        accuracy_ab_mean = float('nan')
        accuracy_ab_std = float('nan')
    else:
        accuracy_ab_mean = mean(valid_accs_ab)
        accuracy_ab_std = safe_stdev(valid_accs_ab)

    valid_f1s_ab = [f for f in f1s_ab if not math.isnan(f)]
    if len(valid_f1s_ab) == 0:
        f1_ab_mean = float('nan')
        f1_ab_std = float('nan')
    else:
        f1_ab_mean = mean(valid_f1s_ab)
        f1_ab_std = safe_stdev(valid_f1s_ab)

    return {
        "base_name": base_name,
        "run_metrics": run_metrics,
        "aggregated": {
            # Overall
            "accuracy_mean": accuracy_mean,
            "accuracy_std": accuracy_std,
            "f1_mean": f1_mean,
            "f1_std": f1_std,

            # Left/Right
            "accuracy_lr_mean": accuracy_lr_mean,
            "accuracy_lr_std": accuracy_lr_std,
            "f1_lr_mean": f1_lr_mean,
            "f1_lr_std": f1_lr_std,

            # Above/Below
            "accuracy_ab_mean": accuracy_ab_mean,
            "accuracy_ab_std": accuracy_ab_std,
            "f1_ab_mean": f1_ab_mean,
            "f1_ab_std": f1_ab_std,
        }
    }


def save_combined_json(
        s1: str,
        s2: str,
        s3: str,
        base_name: str,
        model_name: str,
        combined_data: Dict[str, Any],
        unsure_base: str
) -> None:
    """
    Saves a single JSON file with all runs + aggregated stats into
    a separate 'Unsure_Cases' folder, with the same 3-level folder structure.
    The file is named:
      Result_<model_name>_<base_name>_summary.json
    """
    output = {
        "subfolder_one": s1,
        "subfolder_two": s2,
        "subfolder_three": s3,
        "base_name": base_name,
        "model_name": model_name,
        "run_metrics": combined_data["run_metrics"],
        "aggregated": combined_data["aggregated"]
    }

    out_dir = os.path.join(unsure_base, s1, s2, s3)
    os.makedirs(out_dir, exist_ok=True)

    filename = f"Result_{model_name}_{base_name}_summary.json"
    out_path = os.path.join(out_dir, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)


def gather_json_files_3level(
        base_path: str
) -> Dict[tuple, List[str]]:
    """
    Recursively walk 'base_path', picking up any .json files that do NOT start with "Result_".
    We treat the path structure as:
       base_path / subfolder_one / subfolder_two / subfolder_three

    We also gather *all* 3-level subfolders even if they contain no JSON,
    so we can produce empty rows in the Excel for them.
    """
    collected = {}

    for root, dirs, files in os.walk(base_path):
        rel_path = os.path.relpath(root, base_path)
        parts = rel_path.split(os.sep)
        if len(parts) == 3:
            s1, s2, s3 = parts
            if s1.startswith('.') or s2.startswith('.') or s3.startswith('.'):
                continue
            if (s1, s2, s3) not in collected:
                collected[(s1, s2, s3)] = []
            for fn in files:
                if fn.lower().endswith(".json") and not fn.startswith("Result_"):
                    collected[(s1, s2, s3)].append(os.path.join(root, fn))

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
# 5) Excel Summary
###############################################################################
def write_excel_summary(
        results_summary: List[Dict[str, Any]],
        output_excel_path: str
) -> None:
    """
    Writes all aggregated results into a single Excel file.
    One row per (subfolder_one, subfolder_two, subfolder_three).

    We rename the first columns to:
      "Research Question", "Model", "Markers",
    then we do NOT save the base_name.
    Then we save these columns:

      "Accuracy_Mean", "Accuracy_Std",
      "F1_Mean", "F1_Std",
      "Accuracy_LeftRight_Mean", "Accuracy_LeftRight_Std",
      "F1_LeftRight_Mean", "F1_LeftRight_Std",
      "Accuracy_AboveBelow_Mean", "Accuracy_AboveBelow_Std",
      "F1_AboveBelow_Mean", "F1_AboveBelow_Std"

    Then we add an empty column.

    Then only 3 runs for correct, incorrect, unsure:

      "correct_run1", "correct_run2", "correct_run3",
      "incorrect_run1", "incorrect_run2", "incorrect_run3",
      "unsure_run1", "unsure_run2", "unsure_run3".

    The user wants s1 in the order RQ1, RQ2, RQ3, AS1, AS2, then anything else.
    We also include rows for empty subfolders (no JSON).
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Results"

    # We do NOT save base_name in the Excel. We remove AUC entirely.
    header = [
        "Research Question", "Model", "Markers",
        "Accuracy_Mean", "Accuracy_Std",
        "F1_Mean", "F1_Std",
        "Accuracy_LeftRight_Mean", "Accuracy_LeftRight_Std",
        "F1_LeftRight_Mean", "F1_LeftRight_Std",
        "Accuracy_AboveBelow_Mean", "Accuracy_AboveBelow_Std",
        "F1_AboveBelow_Mean", "F1_AboveBelow_Mean_Std",
        # We add an empty column
        "",
        # Then 3 runs for correct, incorrect, unsure
        "correct_run1", "correct_run2", "correct_run3",
        "incorrect_run1", "incorrect_run2", "incorrect_run3",
        "unsure_run1", "unsure_run2", "unsure_run3"
    ]
    ws.append(header)

    # The user wants s1 in the order: RQ1, RQ2, RQ3, AS1, AS2, then anything else
    priority = {
        "RQ1": 0,
        "RQ2": 1,
        "RQ3": 2,
        "AS1": 3,
        "AS2": 4
    }

    def sort_key(item: Dict[str, Any]):
        s1 = item["subfolder_one"]
        prio = priority.get(s1, 999)
        return (prio, s1, item["subfolder_two"], item["subfolder_three"])

    results_summary_sorted = sorted(results_summary, key=sort_key)

    for item in results_summary_sorted:
        agg = item["aggregated"]

        # We do not display base_name or AUC.
        row = [
            item["subfolder_one"],
            item["subfolder_two"],
            item["subfolder_three"],

            agg.get("accuracy_mean", float('nan')),
            agg.get("accuracy_std", float('nan')),
            agg.get("f1_mean", float('nan')),
            agg.get("f1_std", float('nan')),

            agg.get("accuracy_lr_mean", float('nan')),
            agg.get("accuracy_lr_std", float('nan')),
            agg.get("f1_lr_mean", float('nan')),
            agg.get("f1_lr_std", float('nan')),

            agg.get("accuracy_ab_mean", float('nan')),
            agg.get("accuracy_ab_std", float('nan')),
            agg.get("f1_ab_mean", float('nan')),
            agg.get("f1_ab_std", float('nan')),

            # Empty column
            ""
        ]

        run_metrics = item.get("run_metrics", [])
        run_count = len(run_metrics)

        # We only have 3 runs.
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
        # unsure
        for i in range(3):
            if i < run_count:
                row.append(run_metrics[i]["unsure_count"])
            else:
                row.append("")

        ws.append(row)

    wb.save(output_excel_path)
    print(f"Excel summary saved at: {output_excel_path}")


###############################################################################
# 6) MAIN
###############################################################################
def main():

    # ToDo: Adjust the Path 
    # Path where the model answers are (In there should be 4 subfolders: AS, RQ1, RQ2, RQ3)
    base_path = "./1_model_answers/"
    
    unsure_base = "./Unsure_Cases/"
    os.makedirs(unsure_base, exist_ok=True)

    all_json_files = gather_json_files_3level(base_path)

    excel_summary_rows = []
    for (s1, s2, s3), json_list in all_json_files.items():
        grouped = group_by_run(json_list)
        if not grouped:
            summary_row = {
                "subfolder_one": s1,
                "subfolder_two": s2,
                "subfolder_three": s3,
                "aggregated": {},
                "run_metrics": []
            }
            excel_summary_rows.append(summary_row)
        else:
            for base_name, run_files in grouped.items():
                combined_data = process_runs_for_base(base_name, run_files, model_name=f"{s1}_{s2}_{s3}")
                save_combined_json(
                    s1, s2, s3,
                    base_name, f"{s1}_{s2}_{s3}",
                    combined_data,
                    unsure_base
                )
                summary_row = {
                    "subfolder_one": s1,
                    "subfolder_two": s2,
                    "subfolder_three": s3,
                    "aggregated": combined_data["aggregated"],
                    "run_metrics": combined_data["run_metrics"]
                }
                excel_summary_rows.append(summary_row)

    excel_path = os.path.join(base_path, "Results_Images.xlsx")
    write_excel_summary(excel_summary_rows, excel_path)


if __name__ == "__main__":
    main()
