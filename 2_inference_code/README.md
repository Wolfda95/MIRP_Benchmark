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

1. Download the model [Pixtral-12B-2409](https://huggingface.co/mistralai/Pixtral-12B-2409) from Hugging Face.
    * In Hugging Face click on the 3 dots on the right side, then on Clone repository, then do the steps listed there
2.  Place the downloaded model in a subdirectory called `models` without subfolders.
3. Required Python packages:
    - Built-in: `os`, `sys`, `json`, `random`, `time`, `base64`, `io`
    - External: `torch`, `PIL` (Pillow), `vllm`
4.  Open `pixtral.py` and scroll to the main block (`if __name__ == "__main__":`) and locate the section: "Paths and Experiment Selection".
    * Set `dataset_dir` to the path where the downloaded MIRP dataset is stored.
    * Set `RESULTS_ROOT` to the directory where you want to save the results.
    * Select the Research Question you want to run in the `experiments` list (e.g., ['RQ2'] if you want to run Research Question 2) *(The code will make 3 runs for each marker type.)* (If you select ['RQ3'], this will be the data for RQ3(2), if you want RQ3(1), select RQ1 (because RQ1 and RQ3(2) use the same Dataset) and at [`3_evaluation_code/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/3_evaluation_code) select the correct evaluation script. 
5. Run `pixtral.py`.

-> The model answers for each marker type and each run will be saved in a separate json file. The 3 runs of one setup have the ending `..._run_0.json`, `..._run_1.json`, `..._run_3.json`
  
 
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




