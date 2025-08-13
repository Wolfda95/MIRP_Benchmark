# Inference

### 📋 Prerequisites
- **MIRP Benchmark Dataset** — make sure it’s downloaded first  
  → Instructions: [`1_dataset_guide/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/1_dataset_guide)  
- **Hardware/Access**:  
  - <img src="https://huggingface.co/front/assets/huggingface_logo-noborder.svg" alt="Hugging Face" height="20"/> **Open models** → NVIDIA GPU with enough memory to run the model  
    *(We used an A6000 with 48 GB VRAM)*  
  - 🔑 **Proprietary models** → valid API key

<br/>

### ▶️ Running Inference
Each model is run using its **own script**.  

- The script takes **one image–question pair at a time** and sends it to the model.  
- The model’s answers are saved to a `.json` file.  

💡 You’ll find detailed step-by-step instructions for each model in the toggle menus below.

<br/>

### ⏭️ Next Step
Once inference is done and the answers are saved in the `.json` file, continue to:  
[`3_evaluation_code/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/3_evaluation_code)  
Here you can check **how many answers are correct** and **compute the statistics**.

<br/> <br/>

---
# Instructions
## <img src="https://huggingface.co/front/assets/huggingface_logo-noborder.svg" alt="Hugging Face" height="20"/> How to run the Open Models on a local GPU

<details>
<summary><h3>Pixtral</h3></summary>

1. **Download the model**  
   Get [Pixtral-12B-2409](https://huggingface.co/mistralai/Pixtral-12B-2409) from Hugging Face.  
   - On Hugging Face, click the **three dots** on the right → **Clone repository** → follow the listed steps.

2. **Place the model in the repository**  
   - Store it inside a subdirectory named `models` (no additional subfolders).

3. **Install required Python packages**  
   - **Built-in:** `os`, `sys`, `json`, `random`, `time`, `base64`, `io`  
   - **External:** `torch`, `PIL` (Pillow), `vllm`

4. **Configure `pixtral.py`**  
   - Open `pixtral.py` and scroll to the main block `if __name__ == "__main__":`
   - In the **"Paths and Experiment Selection"** section:  
     - Set `dataset_dir` → path to your downloaded MIRP dataset  
     - Set `RESULTS_ROOT` → directory where results should be saved  
     - Select the Research Question in the `experiments` list (e.g., `['RQ2']` to run RQ2)  
       - The script makes **3 runs for each marker type**  
       - If running `['RQ3']`, note this corresponds to **RQ3(2)**  
       - For **RQ3(1)**, use `['RQ1']` (RQ1 and RQ3(2) share the same dataset)  
         → Then, in [`3_evaluation_code/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/3_evaluation_code), choose the matching evaluation script.

5. **Run the script**  
   ```bash
   python pixtral.py

6. **Output**  
   - Model answers are saved as separate .json files — one per marker type and run.
   - The three runs for a setup are named:
      - `..._run_0.json`
      - `..._run_1.json`
      - `..._run_2.json`

<br/><br/>

**_Use this Code with other Models of the vLLM Libary_** <br/>
To run a different Hugging Face model that is compatible with the **vLLM** library:  
- Open the script and scroll to the main block `if __name__ == "__main__":`
- In the **"Model"** section, replace the current model name with the desired Hugging Face model name.
- Dpending on the model, you might have to change more 

<br/><br/>
 
</details>


<details>
<summary><h3>Llama3.2</h3></summary>
  
 1. **Download the model**  
   Get [Llama-3.2-11B-Vision-Instruct](https://huggingface.co/meta-llama/Llama-3.2-11B-Vision-Instruct) from Hugging Face.  
     - On Hugging Face, click the **three dots** on the right → **Clone repository** → follow the listed steps.

2. **Place the model in the repository**  
   - Store it inside a subdirectory named `models` (no additional subfolders).

3. **Install required Python packages**  
   - **Built-in:** `os`, `sys`, `json`, `random`, `time`  
   - **External:** `torch`, `PIL` (Pillow), `transformers`

4. **Configure `llama.py`**  
   - Open `llama.py` and scroll to the main block `if __name__ == "__main__":`  
   - In the **"Paths and Experiment Selection"** section:  
     - Set `dataset_dir` → path to your downloaded MIRP dataset  
     - Set `RESULTS_ROOT` → directory where results should be saved  
     - Select the Research Question in the `experiments` list (e.g., `['RQ2']` to run RQ2)  
       - The script makes **3 runs for each marker type**  
       - If running `['RQ3']`, note this corresponds to **RQ3(2)**  
       - For **RQ3(1)**, use `['RQ1']` (RQ1 and RQ3(2) share the same dataset)  
         → Then, in [`3_evaluation_code/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/3_evaluation_code), choose the matching evaluation script.

5. **Run the script**  
   ```bash
   python llama.py

6. **Output**  
   - Model answers are saved as separate .json files — one per marker type and run.
   - The three runs for a setup are named:
      - `..._run_0.json`
      - `..._run_1.json`
      - `..._run_2.json`

<br/><br/>

**_Use this Code with other Models of the Transformer Libary_** <br/>
To run a different Hugging Face model that is compatible with the **Transformer** library:  
- Open the script and scroll to the main block `if __name__ == "__main__":`
- In the **"Model"** section, replace the current model name with the desired Hugging Face model name.
- Dpending on the model, you might have to change more

 <br/><br/>
 
</details>


<details>
<summary><h3>JanusPro</h3></summary>
  
  1. **Download the model**  
   Get [Janus-Pro-7B](https://huggingface.co/deepseek-ai/Janus-Pro-7B) from Hugging Face.  
     - On Hugging Face, click the **three dots** on the right → **Clone repository** → follow the listed steps.

2. **Place the model in the repository**  
   - Store it inside a subdirectory named `models` (no additional subfolders).

3. **Install required Python packages**  
   - **Built-in:** `os`, `sys`, `json`, `random`, `time`  
   - **External:** `torch`, `PIL` (Pillow), `transformers`, `janus`

4. **Configure `januspro.py`**  
   - Open `januspro.py` and scroll to the main block `if __name__ == "__main__":`  
   - In the **"Paths and Experiment Selection"** section:  
     - Set `dataset_dir` → path to your downloaded MIRP dataset  
     - Set `RESULTS_ROOT` → directory where results should be saved  
     - Select the Research Question in the `experiments` list (e.g., `['RQ2']` to run RQ2)  
       - The script makes **3 runs for each marker type**  
       - If running `['RQ3']`, note this corresponds to **RQ3(2)**  
       - For **RQ3(1)**, use `['RQ1']` (RQ1 and RQ3(2) share the same dataset)  
         → Then, in [`3_evaluation_code/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/3_evaluation_code), choose the matching evaluation script.

5. **Run the script**  
   ```bash
   python januspro.py

6. **Output**  
   - Model answers are saved as separate .json files — one per marker type and run.
   - The three runs for a setup are named:
      - `..._run_0.json`
      - `..._run_1.json`
      - `..._run_2.json`

 
</details>


<details>
<summary><h3>Run other open models from Hugging Face</h3></summary>

If you want to run **other open models** from Hugging Face:

- **Based on the vLLM library** → Use `pixtral.py` and its instructions as your starting point.  
- **Based on the Transformers library** → Use `llama.py` and its instructions as your starting point.  

### 🔧 Adapting the code
1. Open the script and scroll to the main block `if __name__ == "__main__":`
2. In the **"Model"** section, replace the current model name with the desired Hugging Face model name.  
3. Depending on the model, you may need to adjust additional code to ensure compatibility.

<br/>

### 🆕 If starting a new script

Below are the **initial prompts** we used: 


RQ1, RQ2, RQ3
```python
"The image is a 2D axial slice of an abdominal CT scan with soft tissue windowing. "
"Answer strictly with '1' for Yes or '0' for No. No explanations, no additional text. "
"Your output must contain exactly one character: '1' or '0'."
"Ignore anatomical correctness; focus solely on what the image shows.\n"
"Example:\n"
"Q: \"Is the aorta above the spleen?\" A: 1\n"
"Now answer the real question:\n\n"
f"Q: {question_from_json}"
```

AS (Ablation Study)
```python
"Answer strictly with '1' for Yes or '0' for No. No explanations, no additional text. "
"Your output must contain exactly one character: '1' or '0'."
"Focus solely on what the image shows.\n"
"Example:\n"
"Q: \"Is the red dot above the blue dot\" A: 1\n"
"Now answer the real question:\n\n"
f"Q: {question_from_json}"
```

Here is an **example of the output `.json`** structure

```json
{
    "file_name": "amos_0221.nii_slice-279_classes-27_perc-14.png",
    "results_call": [
        {
            "question": "Is the left lung upper lobe (10) to the right of the left clavicula (73)?",
            "model_answer": "0",
            "expected_answer": 1,
            "entire_prompt": "The image is a 2D axial slice of an abdominal CT scan with soft tissue windowing. Answer strictly with '1' for Yes or '0' for No. No explanations, no additional text. Your output must contain exactly one character: '1' or '0'.Ignore anatomical correctness; focus solely on what the image shows.\nExample:\nQ: Is the right iliopsoas (89) to the left of the left gluteus maximus (80)? A: 1\nNow answer the real question:\n\nQ: Is the left lung upper lobe (10) to the right of the left clavicula (73)?"
        }
    ]
},
{
    "file_name": "amos_0482.nii_slice-234_classes-26_perc-19.png",
    "results_call": [
        {
            "question": "Is the right scapula (72) above the left scapula (71)?",
            "model_answer": "1",
            "expected_answer": 1,
            "entire_prompt": "The image is a 2D axial slice of an abdominal CT scan with soft tissue windowing. Answer strictly with '1' for Yes or '0' for No. No explanations, no additional text. Your output must contain exactly one character: '1' or '0'.Ignore anatomical correctness; focus solely on what the image shows.\nExample:\nQ: Is the left autochthon (86) to the right of the liver (5)? A: 1\nNow answer the real question:\n\nQ: Is the right scapula (72) above the left scapula (71)?"
        }
    ]
}
```

</details>



## 🔑 How to run the Proprietary Models via API

<details>
<summary><h3>GPT4o</h3></summary>
  
This code sends the image-question pairs via the API to OpenAI's GPT-4o model. You don`t need a GPU to run this code. You pay per token. 

Here you can sign up for an OpenAI API: [OpenAI Platform](https://platform.openai.com/docs/overview) 

1. **Install required Python packages**  
   - **Built-in:** `os`, `sys`, `json`, `random`, `time`, `io`, `base64`  
   - **External:** `openai`, `PIL` (from Pillow)

2. **Configure `gpt4o.py`**  
   - Open `gpt4o.py` and scroll to the main block `if __name__ == "__main__":`  
   - In the **"Paths and Experiment Selection"** section:  
     - Set `dataset_dir` → path to your downloaded MIRP dataset  
     - Set `RESULTS_ROOT` → directory where results should be saved  
     - Select the Research Question in the `experiments` list (e.g., `['RQ2']` to run RQ2)  
       - The script makes **3 runs for each marker type**  
       - If running `['RQ3']`, note this corresponds to **RQ3(2)**  
       - For **RQ3(1)**, use `['RQ1']` (RQ1 and RQ3(2) share the same dataset)  
         → Then, in [`3_evaluation_code/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/3_evaluation_code), choose the matching evaluation script.
         
3. **Add OpenAI API Key**  
   Add your API key as the environment variable `OPENAI_API_KEY`  

5. **Run the script**  
   ```bash
   python gpt4o.py

6. **Output**  
   - Model answers are saved as separate .json files — one per marker type and run.
   - The three runs for a setup are named:
      - `..._run_0.json`
      - `..._run_1.json`
      - `..._run_2.json`

<br/><br/>

**_Use this Code with other Models from OpenAI_** <br/> 
- Open the `gpt4o.py` and scroll to "# Model":
- Replace the current model name (gpt-4o-2024-08-06) with the desired model name.
- Here you can find all openAI Models: [OpenAI Platform Models](https://platform.openai.com/docs/models) 

 <br/><br/>
 
</details>


<details>
<summary><h3>Run other Proprietary Models</h3></summary>
  
 ### Other Models from OpenAI: 
- Open the `gpt4o.py` and scroll to "# Model":
- Replace the current model name (gpt-4o-2024-08-06) with the desired model name.
- Here you can find all openAI Models: [OpenAI Platform Models](https://platform.openai.com/docs/models)

### Models from other companies: 
Search for tutorials on how to run their models via the API. <br>
If you start with a new code, make sure to use the **initial prompts**: 

RQ1, RQ2, RQ3
```python
"The image is a 2D axial slice of an abdominal CT scan with soft tissue windowing. "
"Answer strictly with '1' for Yes or '0' for No. No explanations, no additional text. "
"Your output must contain exactly one character: '1' or '0'."
"Ignore anatomical correctness; focus solely on what the image shows.\n"
"Example:\n"
"Q: \"Is the aorta above the spleen?\" A: 1\n"
"Now answer the real question:\n\n"
f"Q: {question_from_json}"
```

AS (Ablation Study)
```python
"Answer strictly with '1' for Yes or '0' for No. No explanations, no additional text. "
"Your output must contain exactly one character: '1' or '0'."
"Focus solely on what the image shows.\n"
"Example:\n"
"Q: \"Is the red dot above the blue dot\" A: 1\n"
"Now answer the real question:\n\n"
f"Q: {question_from_json}"
```

Here is an **example of the output `.json`** structure

```json
{
    "file_name": "amos_0221.nii_slice-279_classes-27_perc-14.png",
    "results_call": [
        {
            "question": "Is the left lung upper lobe (10) to the right of the left clavicula (73)?",
            "model_answer": "0",
            "expected_answer": 1,
            "entire_prompt": "The image is a 2D axial slice of an abdominal CT scan with soft tissue windowing. Answer strictly with '1' for Yes or '0' for No. No explanations, no additional text. Your output must contain exactly one character: '1' or '0'.Ignore anatomical correctness; focus solely on what the image shows.\nExample:\nQ: Is the right iliopsoas (89) to the left of the left gluteus maximus (80)? A: 1\nNow answer the real question:\n\nQ: Is the left lung upper lobe (10) to the right of the left clavicula (73)?"
        }
    ]
},
{
    "file_name": "amos_0482.nii_slice-234_classes-26_perc-19.png",
    "results_call": [
        {
            "question": "Is the right scapula (72) above the left scapula (71)?",
            "model_answer": "1",
            "expected_answer": 1,
            "entire_prompt": "The image is a 2D axial slice of an abdominal CT scan with soft tissue windowing. Answer strictly with '1' for Yes or '0' for No. No explanations, no additional text. Your output must contain exactly one character: '1' or '0'.Ignore anatomical correctness; focus solely on what the image shows.\nExample:\nQ: Is the left autochthon (86) to the right of the liver (5)? A: 1\nNow answer the real question:\n\nQ: Is the right scapula (72) above the left scapula (71)?"
        }
    ]
}
```


 
 
</details>




