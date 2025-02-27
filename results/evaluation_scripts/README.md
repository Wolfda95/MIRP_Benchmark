# Evaluation Skrips

## Set up the Environment
- PyTorch 3.10
- pip install -r requirements.txt

### For conda on Linux:
- <code>conda create --name misr_evaluation python==3.10</code> 
- <code>conda activate misr_evaluation</code> 
- <code>cd ...MISR-Benchmark/results/evaluation_scripts/</code> 
- <code>pip install -r requirements.txt</code>

## Run: 
- Results based on the image view: `1_calculate_results_image.py`
- Results based on human anatomy: `2_calculate_results_anatomy.py`

  For both: Change the file names in the main method (end of script) to locate to your folder with all the model answer json files. 
  (Works with the file structure you get when you download the model response json files from GoogleDrive) 
