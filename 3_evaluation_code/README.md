# Evaluation

### 📋 Prerequisites
- **MIRP Benchmark Dataset**  
  → Instructions to Download: [`1_dataset_guide/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/1_dataset_guide)  
- **Model Answer JSON Files**:  
  → Instructions to run Inference: [`2_inference_code/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/2_inference_code)  

<br/>

### ▶️ Running Evaluation 
Those two scripts evaluate the predictions of one model on a specific task across 3 runs. <br>
It computes mean and standard deviation of accuracy and F1 score over the 3 runs. The results are saved to an Excel file.

1. **Place the JSON Files**
   - Place the model output files (`*_run_0.json`, `*_run_1.json`, `*_run_2.json`) in a folder called `answers/`.
   - Place the `center_of_anatomical_stuctures_in_standard_radiological_orientation.json` file in the same directory as this scripts. (This file is part of the downloaded MIRP Benchmark dataset.)
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
2. **Install the Requirements**
   ```
   requirements.txt
   ```
4. **Run the Evaluation**
   - **Image-Based** (Research Question 1, 2, 3(2))
      ```
       python run RQ1_RQ2_RQ3-2_calculate_results_image.py
      ```
      This script evaluates a model's responses to the left/right spatial relation questions by checking if they are correct based on the image orientation. 
   - **Anatomy-Based** (Research Question 3(1))
      ```
       python run RQ3-1_calculate_results_anatomy.py
      ```
      This script evaluates a model's responses to the left/right spatial relation questions by comparing:
        1. The correct spatial relationships based on the image orientation (image-based evaluation).
        2. The correct spatial relationships based on standard human anatomy (anatomy-based evaluation).

   
<br/>

### ⏭️ Next Step
You can compare your resuls with ours:  
[`our_results/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/our_results)  

