# Inference

### Prerequisite: 
- Downloaded MIRP Benchmark Dataset (Instructions: [`1_dataset_guide/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/1_dataset_guide))
- For open models: Nvidia GPU with sufficient memory to run the model (We used A6000 48GB) || For proprietary models: API key

<br/>

### Run Inference: 
Each model is executed via a separate script.  <br>
Each script passes one image-question pair after another throught the model. The model answers are saved in a json file. <br>
You find detailed instructions on how to run the script for each model below in the toggel bars. 

<br/>

### Next Step: 
After inference is completed and the model answers are saved in the json file, proceed to [`3_evaluation_code/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/3_evaluation_code) to evaluate how many answers are correct and to calculate the statistics. 

<br/> <br/>
# How to run the Open Models

<details>
<summary><h2>Pixtral</h2></summary>

1. Download the model [Pixtral-12B-2409](https://huggingface.co/mistralai/Pixtral-12B-2409) from Hugging Face.
    * In Hugging Face click on the 3 dots on the right side, then on Clone repository, then do the steps listed there
2.  Place the downloaded model in a subdirectory called `models` without subfolders.
3. Required Python packages:
    - Built-in: `os`, `sys`, `json`, `random`, `time`, `base64`, `io`
    - External: `torch`, `PIL` (Pillow), `vllm`
4.  Open `pixtral.py` and scroll to the main block (`if __name__ == "__main__":`) and locate the section: "Paths and Experiment Selection".
    * Set `dataset_dir` to the path where the downloaded MIRP dataset is stored.
    * Set `RESULTS_ROOT` to the directory where you want to save the results.
    * Specify the experiments you want to run in the `experiments` list (e.g., ['RQ2'] if you only want to run Research Question 2) *(The code will make 3 runs for each selected Research Question and marker type.)*
5. Run `pixtral.py`.

-> For each task, a dedicated results folder will be created, and responses will be saved in JSON format for each run (3 runs per selected Research Question and marker type)
  
 
</details>


<details>
<summary><h2>Llama3.2</h2></summary>
  
 ### Test
 
</details>


<details>
<summary><h2>JanusPro</h2></summary>
  
 ### Test
 
</details>


<details>
<summary><h2>How to run other open Models from Hugging Face</h2></summary>
  
 ### Test
 
</details>



# How to run the Proprietary Models

<details>
<summary><h2>GPT4o</h2></summary>
  
 ### Test
 
</details>


<details>
<summary><h2>How to run other Proprietary Models from Hugging Face</h2></summary>
  
 ### Test
 
</details>




