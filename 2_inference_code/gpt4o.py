"""
Script for Running Visual QA Experiments with OpenAI's GPT-4o via API.

Overview:
This script processes images and associated questions, sends them via the API to OpenAI's GPT-4o model,
and saves the model's responses in structured JSON files for further analysis.

Prerequisites:
1. An OpenAI API key must be available as the environment variable `OPENAI_API_KEY`.
2. The MIRP Benchmark dataset must be downloaded locally.
3. Required Python packages:
    - Built-in: `os`, `sys`, `json`, `random`, `time`, `io`, `base64`
    - External: `openai`, `PIL` (from Pillow)


Usage Instructions:
1. Scroll to the main block (`if __name__ == "__main__":`) and locate the section:
   "Paths and Experiment Selection".
   1.1 Set `dataset_dir` to the path where your dataset is stored.
   1.2 Set `RESULTS_ROOT` to the directory where you want to save the results.
   1.3 Select the experiment you want to run in the `experiments` list (e.g., ['RQ2']).
2. Run the script.
3. For each task, a dedicated results folder will be created, and responses will be saved in
   JSON format for each run (3 runs per task by default).


Functionality Summary:
1. QA Data Extraction:
   - Loads question-answer pairs from JSON files for each task.
   - Uses either random sampling or the full dataset, depending on configuration.
2. Image Processing:
   - Converts images to RGB format if necessary.
   - Encodes images in base64 format for API compatibility.
3. API Call Execution:
   - Constructs structured prompts for binary QA tasks.
   - Sends image + question to GPT-4o via OpenAI's API.
   - Collects and records the model’s responses.
4. Results Storage:
   - Responses are saved in structured JSON files.
   - Each experiment is run three times to ensure result consistency.


Notes:
- Ensure the `openai` package is correctly installed and configured with your API key.
- The script uses a fixed random seed (`random.seed(2025)`) for reproducibility.
"""


import base64
import openai
import os
from io import BytesIO
from PIL import Image
import json
import sys
import random
import time

openai.api_key = os.getenv("OPENAI_API_KEY")


def encode_image_from_bytes(image):
    """
    Encodes an image object into a base64-encoded PNG string.

    Args:
        image (PIL.Image.Image): The image to encode.

    Returns:
        str: Base64-encoded string representation of the image.

    Example:
        ```python
        from PIL import Image
        import base64

        img = Image.open("example.png")
        encoded_string = encode_image_from_bytes(img)
        print(encoded_string)
        ```
    """
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def is_grayscale(image):
    """
    Checks if a given image is in grayscale mode.

    Args:
        image (PIL.Image.Image): The image to check.

    Returns:
        bool: True if the image is grayscale, False otherwise.

    The function checks whether the image mode is either "L" (8-bit grayscale) 
    or "I;16" (16-bit grayscale).

    Example:
        ```python
        from PIL import Image

        img = Image.open("example.png")
        if is_grayscale(img):
            print("The image is grayscale.")
        else:
            print("The image is in color.")
        ```
    """
    return image.mode in ["L", "I;16"]


def normalize_16bit_to_8bit(image):
    """
    Normalizes a 16-bit grayscale image to an 8-bit grayscale image.

    Args:
        image (PIL.Image.Image): A 16-bit grayscale image (mode "I;16").

    Returns:
        PIL.Image.Image: An 8-bit grayscale image (mode "L").

    The function scales pixel values from the 16-bit range (0-65535) to the 
    8-bit range (0-255) by dividing each pixel by 256 and then converting 
    the image to mode "L".

    Example:
        ```python
        from PIL import Image

        img_16bit = Image.open("example_16bit.png")
        img_8bit = normalize_16bit_to_8bit(img_16bit)
        img_8bit.save("example_8bit.png")
        ```
    """
    normalized_image = image.point(
        lambda x: (x / 256))
    return normalized_image.convert("L")


def ensure_rgb(image):
    """
    Ensures that the given image is in RGB mode.

    Args:
        image (PIL.Image.Image): The input image.

    Returns:
        PIL.Image.Image: The image converted to RGB mode.

    This function handles different image modes as follows:
    - If the image is in "I;16" mode (16-bit grayscale), it is first normalized 
      to 8-bit grayscale and then converted to RGB.
    - If the image is grayscale ("L") or has an alpha channel ("RGBA"), 
      it is directly converted to RGB.
    - If the image is already in "RGB" mode, a copy is returned.
    - If the image mode is unsupported, a `ValueError` is raised.

    Example:
        ```python
        from PIL import Image

        img = Image.open("example.png")
        rgb_img = ensure_rgb(img)
        rgb_img.show()
        ```

    Raises:
        ValueError: If the image mode is not supported.
    """
    if image.mode == "I;16":
        return normalize_16bit_to_8bit(image).convert("RGB")
    elif is_grayscale(image) or image.mode == "RGBA":
        return image.convert("RGB")
    elif image.mode == "RGB":
        return image.copy()
    else:
        raise ValueError(f"Unsupported image mode: {image.mode}")


def get_clean_image(image_path):
    """
    Loads an image, ensures it is in RGB mode, and encodes it as a base64 string.

    Args:
        image_path (str): The file path to the image.

    Returns:
        str: The base64-encoded representation of the image.

    This function performs the following steps:
    1. Opens the image from the given path.
    2. Converts it to RGB mode if necessary using `ensure_rgb()`.
    3. Encodes the processed image into a base64 string using `encode_image_from_bytes()`.

    Example:
        ```python
        encoded_image = get_clean_image("example.png")
        print(encoded_image)
        ```
    """
    with Image.open(original_image_path) as img:
        rgb_image = ensure_rgb(img)
    base64_image = encode_image_from_bytes(rgb_image)

    return base64_image


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


def make_better_api_call(questions_data, base64_image, additional_question):
    """
    Sends a structured API call to OpenAI's GPT model with a medical image 
    and a question about its content.

    Args:
        questions_data (dict): A dictionary containing:
            - 'question' (str): The question to ask about the image.
            - 'answer' (str): The expected answer.
        base64_image (str): A base64-encoded PNG image of a 2D axial CT scan.
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
    a binary response ('1' for Yes, '0' for No). It sends the image in base64 
    format along with the textual question. The model response is then stored 
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

    messages = [
        {
            "type": "text",
            "text": prompt
        },
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}
        }
    ]

    response = openai.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "user", "content": messages}
        ],
        temperature=0
    )

    model_answer = response.choices[0].message.content

    results.append({
        "question": questions_data['question'],
        "model_answer": model_answer,
        "expected_answer": questions_data['answer'],
        "entire_prompt": prompt
    })

    return results


if __name__ == "__main__":

    # ──────────────────────────────────────────────────────────────────────────────
    #  Paths and Experiment Selection
    # ──────────────────────────────────────────────────────────────────────────────

    dataset_dir = os.path.join('../dataset')

    RESULTS_ROOT = 'results'  # path for results directory

    experiments = ['RQ2']  # select the experiments here: 'RQ1', 'RQ2', 'RQ3', 'AS'

    # ──────────────────────────────────────────────────────────────────────────────

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

                    base64_image = get_clean_image(original_image_path)

                    results_call = make_better_api_call(
                        question_data[0], base64_image, additional_question=additional_question[0])

                    dataset_results.append({
                        "file_name": image,
                        "results_call": results_call
                    })

                results_file_name = f"{selected_qa.replace('.json', '')}_{mo_file_name_appendix}_run_{i}.json"

                save_name = os.path.join(
                    RESULTS_ROOT, results_file_name)

                # Ensure the directory exists
                os.makedirs(os.path.dirname(save_name), exist_ok=True)

                with open(save_name, 'w') as json_file:
                    json.dump(dataset_results, json_file, indent=4)
                end_time = time.time()

                elapsed_time = end_time - start_time
                print(f"Runtime for {selected_qa.replace('.json', '')} with {selected_image} : {elapsed_time:.2f} seconds")

        print('###')
