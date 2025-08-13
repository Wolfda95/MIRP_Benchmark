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
# 📂 Instructions
## How to run the Open Models

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
   - Open `pixtral.py` and scroll to the main block:  
     ```python
     if __name__ == "__main__":
     ```
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

<br/>

**Output** <br/>
Model answers are saved as separate .json files — one per marker type and run.

The three runs for a setup are named:
- `..._run_0.json`
- `..._run_1.json`
- `..._run_3.json`
  
 
</details>


<details>
<summary><h3>Llama3.2</h3></summary>
  
 ### Test
 
</details>


<details>
<summary><h3>JanusPro</h3></summary>
  
 ### Test
 
</details>


<details>
<summary><h3>Rrun other open Models from Hugging Face</h3></summary>
  
 ### Test
 
</details>



## How to run the Proprietary Models

<details>
<summary><h3>GPT4o</h3></summary>
  
 ### Test
 
</details>


<details>
<summary><h3>How to run other Proprietary Models from Hugging Face</h3></summary>
  
 ### Test
 
</details>




