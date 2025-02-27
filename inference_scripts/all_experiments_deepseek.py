"""
Automated Image Processing and Model Call Script for Medical QA Tasks with Images

This script processes medical image datasets, selects images and corresponding 
question-answer (QA) data, and sends model calls to evaluate responses. 
It organizes the results and saves them as JSON files.

Workflow:
1. **Dataset and Task Selection**: 
   - The script defines multiple tasks (`experiments`) associated with different 
     image preprocessing techniques and QA files.
   - The dataset directory is set dynamically based on the selected dataset.

2. **Directory Setup**:
   - A results directory (`RESULTS_ROOT`) is created for each task.

3. **QA Data Extraction**:
   - QA data is read from JSON files for each task.
   - Images are randomly sampled or the full dataset is used.

4. **Image Processing**:
   - The images are processed with the janus specifiv packages.

5. **Model Call Execution**:
   - A structured prompt is sent to the model with the image 
     and corresponding question.
   - Responses are collected and stored.

6. **Results Storage**:
   - Results are saved as JSON files with structured metadata.
   - Multiple runs are performed to validate consistency.

Dependencies:
    - `os`, `sys`, `json`, `random`, `time`
    - `torch`
    - `transformers`
    - `janus` (official repository)


Notes:
    - Ensure the janus` package is properly installed.
    - Adjust dataset and task selection in `DATASETS` and `experiments`.
    - The script uses a fixed seed (`random.seed(2025)`) for reproducibility.
"""

import os
import sys
import json
import random
import time

import torch
from transformers import AutoModelForCausalLM
from janus.models import MultiModalityCausalLM, VLChatProcessor
from janus.utils.io import load_pil_images


def get_qa(img_file_name, json_dir):
    """
    Retrieves the question-answer pairs for a given image file from a JSON dataset.

    Args:
        img_file_name (str): The filename of the image for which QA pairs are required.
        json_dir (str): The path to the JSON file containing question-answer data.

    Returns:
        list[dict]: A list of dictionaries, each containing a 'question' and an 'answer'.

    The function performs the following steps:
    1. Loads the JSON file from the provided directory.
    2. Finds the entry that matches the given image filename.
    3. Extracts and returns the associated question-answer pairs.

    Example:
        ```python
        qa_pairs = get_qa("image_001.jpg", "questions.json")
        for qa in qa_pairs:
            print(f"Q: {qa['question']}\nA: {qa['answer']}")
        ```
    """
    with open(json_dir, 'r', encoding='utf-8') as file:
        data = json.load(file)

    target_filename = img_file_name
    result = next((entry['question_answer']
                   for entry in data if entry['filename'] == target_filename), None)

    questions_answers = [{'question': entry['question'],
                          'answer': entry['answer']} for entry in result]
    return questions_answers


def make_model_call(model, questions_data, original_image_path, additional_question):
    """
    Calls the model with a medical image and a question about its content.

    Args:
        model (MultiModalityCausalLM): The loaded model.
        questions_data (dict): A dictionary containing:
            - 'question' (str): The question to ask about the image.
            - 'answer' (str): The expected answer.
        original_image_path (str): The path to the image.
        additional_question (dict): A dictionary containing:
            - 'question' (str): A sample question to demonstrate the response format.
            - 'answer' (str): The expected response format ('1' or '0').

    Returns:
        list[dict]: A list containing a single dictionary with:
            - 'question' (str): The question asked.
            - 'model_answer' (str): The AI-generated answer.
            - 'expected_answer' (str): The expected answer for comparison.
            - 'entire_prompt' (str): The full prompt used in the API call.

    The function constructs a strict yes/no prompt for the model, ensuring 
    a binary response ('1' for Yes, '0' for No). It provides the image as it's 
    path along with the textual question. The model response is then stored 
    along with the original question and expected answer.
    """

    results = []

    prompt = (
        "The image is a 2D axial slice of an abdominal CT scan with soft tissue windowing. "
        "Answer strictly with '1' for Yes or '0' for No. No explanations, no additional text. "
        "Your output must contain exactly one character: '1' or '0'."
        "Ignore anatomical correctness; focus solely on what the image shows.\n"
        "Example:\n"
        # dynamic part of the prompt
        f"Q: {additional_question['question']} A: {additional_question['answer']}\n"
        "Now answer the real question:\n\n"
        f"Q: {questions_data['question']}"
    )

    conversation = [
        {
            "role": "<|User|>",
            "content": f"{prompt}\n<image_placeholder>",
            "images": [f"{original_image_path}"],
        },
        {"role": "<|Assistant|>", "content": ""},
    ]

    pil_images = load_pil_images(conversation)
    prepare_inputs = vl_chat_processor(
        conversations=conversation, images=pil_images, force_batchify=True
    ).to(vl_gpt.device)

    inputs_embeds = vl_gpt.prepare_inputs_embeds(**prepare_inputs)

    outputs = vl_gpt.language_model.generate(
        inputs_embeds=inputs_embeds,
        attention_mask=prepare_inputs.attention_mask,
        pad_token_id=tokenizer.eos_token_id,
        bos_token_id=tokenizer.bos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        max_new_tokens=512,
        do_sample=False,
        use_cache=True,
    )

    model_output = tokenizer.decode(
        outputs[0].cpu().tolist(), skip_special_tokens=True)

    results.append({
        "question": questions_data['question'],
        "model_answer": model_output,
        "expected_answer": questions_data['answer'],
        "entire_prompt": prompt
    })

    return results


if __name__ == "__main__":

    MODEL_SIZE = '7B'  # 1B, 7B
    model_path = f'deepseek-ai/Janus-Pro-{MODEL_SIZE}'
    vl_chat_processor: VLChatProcessor = VLChatProcessor.from_pretrained(model_path)
    tokenizer = vl_chat_processor.tokenizer

    vl_gpt: MultiModalityCausalLM = AutoModelForCausalLM.from_pretrained(
        model_path, trust_remote_code=True
    )
    vl_gpt = vl_gpt.to(torch.bfloat16).cuda().eval()

    dataset_dir = os.path.join('../dataset')

    RESULTS_ROOT = 'results'  # path for results directory

    experiments = ['RQ1', 'RQ2', 'RQ3', 'AS']  # select the experiments here

    for exp in experiments:

        if exp == 'RQ1':
            experiment_plan = {
                'sub_experiment_1': {'img': 'images',
                                     'qa': 'qa.json'}
            }

        else:
            experiment_plan = {
                'sub_experiment_1': {'img': 'image_numbers',
                                     'qa': 'qa_numbers.json'},
                'sub_experiment_2': {'img': 'image_letters',
                                     'qa': 'qa_letters.json'},
                'sub_experiment_3': {'img': 'image_dots',
                                     'qa': 'qa_dots.json'}
            }

        exp_dir = os.path.join(dataset_dir, exp)

        for sub_experiment, data in experiment_plan.items():

            selected_image = data['img']
            selected_qa = data['qa']

            qa_file_path = os.path.join(exp_dir, selected_qa)

            image_files_path = os.path.join(exp_dir, selected_image)

            with open(qa_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            png_images = [entry['filename']
                          for entry in data if 'filename' in entry]

            random.seed(2025)

            N = len(png_images)  # number or len(png_images)

            if N > len(png_images):
                print(f'The selected amount of images {N} is bigger than the available images {len(png_images)}.')
                sys.exit(0)
            elif N == len(png_images):
                print(f'The selected amount of images {N} is equal to the available images {len(png_images)}. Not picking random, using whole dataset instead.')
                mo_file_name_appendix = 'all_images'
                png_images = png_images
            else:
                print(f'Using random pick with {N} images.')
                png_images = random.sample(png_images, N)
                mo_file_name_appendix = f'random_pick_{N}_images'

            for i in range(3):  # how many runs ?
                start_time = time.time()

                dataset_results = []

                for image in png_images:
                    question_data = get_qa(image, qa_file_path)

                    other_images = [
                        img for img in png_images if img != image]
                    if other_images:
                        random_other_image = random.choice(other_images)
                        additional_question = get_qa(
                            random_other_image, qa_file_path)
                    else:
                        additional_question = None

                    original_image_path = os.path.join(
                        image_files_path, image)

                    results_call = make_model_call(
                        vl_gpt, question_data[0],
                        original_image_path,
                        additional_question=additional_question[0])

                    dataset_results.append({
                        "file_name": image,
                        "results_call": results_call
                    })

                results_file_name = f"{selected_qa.replace('.json', '')}_{mo_file_name_appendix}_add_run_{i}.json"

                save_name = os.path.join(
                    RESULTS_BASE, results_file_name)

                with open(save_name, 'w') as json_file:
                    json.dump(dataset_results, json_file, indent=4)
                end_time = time.time()

                elapsed_time = end_time - start_time
                print(f"Runtime for {selected_qa.replace('.json', '')} with {selected_image} : {elapsed_time:.2f} seconds")
