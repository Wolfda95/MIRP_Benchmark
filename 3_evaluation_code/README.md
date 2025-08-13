# Evaluation

### 📋 Prerequisites
- **MIRP Benchmark Dataset**  
  → Instructions to Download: [`1_dataset_guide/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/1_dataset_guide)  
- **Model Answer JSON Files**:  
  → Instructions to run Inference: [`2_inference_code/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/2_inference_code)  

<br/>

### ▶️ Running Evaluation 

1. **Model Answer JSON Files**
   - Place the model output files (`*_run_0.json`, `*_run_1.json`, `*_run_2.json`) in a folder called `answers/`.
2. **Standard Orientation JSON File**
   - Place the `center_of_anatomical_stuctures_in_standard_radiological_orientation.json` file in the same directory as this script. (This file is part of the downloaded MIRP Benchmark dataset.)
   - The pathes should look like this: (alternatively, you can change the paths in the main method of the code)
      ```
        Base
          ├── RQ1_RQ2_RQ3-2_calculate_results_image.py
          ├── RQ3-1_calculate_results_anatomy.py
          ├── center_of_anatomical_stuctures_in_standard_radiological_orientation.json
          └── answers/
              ├── <base>_run_0.json
              ├── <base>_run_1.json
              └── <base>_run_2.json
      ```
3. **Requirements**
   ```
   requirements.txt
   ```
4. **Run Evaluation**
   - **Image-Based** (Research Question 1, 2, 3(2))
      ```
       python run RQ1_RQ2_RQ3-2_calculate_results_image.py
      ```
  - **Image-Based** (Research Question 1, 2, 3(2))
  ```
   python run RQ1_RQ2_RQ3-2_calculate_results_image.py
  ```

   
<br/>

### ⏭️ Next Step
Once inference is done and the answers are saved in the `.json` file, continue to:  
[`3_evaluation_code/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/3_evaluation_code)  
Here you can check **how many answers are correct** and **compute the statistics**.
