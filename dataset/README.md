# Dataset
Here are 10 example cases for each experimental setup that we present in the paper.<br>
If accepted, we will provide a download link for the full dataset here.

Each subfolder for the Research Questions RQ1, RQ2, RQ3 and the Ablation Study AS, contains: 
- Image folders with 10 rotated/flipped CT slices
- Json files with the question answer pair (qa) for each CT slice


### Folders
- RQ1:
    - `images`: CT slices
    - `qa.json`: question answer pairs
- RQ2:
   - `image_dots`: CT slices with dot markers
   - `image_letters`: CT slices with image markers
   - `image_numbers`: CT slices with number markers
   - `qa_dots.json`: qa for dot markers
   - `qa_letters.json`: qa for letter markers
   - `qa_numbers.json`: qa for number markers
- RQ3:
   - `image_dots`: CT slices with dot markers
   - `image_letters`: CT slices with image markers
   - `image_numbers`: CT slices with number markers
   - `qa_dots.json`: qa for dot markers
   - `qa_letters.json`: qa for letter markers
   - `qa_numbers.json`: qa for number markers
 - AS:
   - `image_dots`: white images with dot markers
   - `image_letters`: white images with image markers
   - `image_numbers`: white images with number markers
   - `qa_dots.json`: qa for dot markers
   - `qa_letters.json`: qa for letter markers
   - `qa_numbers.json`: qa for number markers
 

## Fixed Prompt: 
The json files contain the questions that we pass to the model. 

In addition to the question, we add a fixed text prompt: 

#### RQ1, RQ2, RQ3: 
```
"The image is a 2D axial slice of an abdominal CT scan with soft tissue windowing. "
"Answer strictly with '1' for Yes or '0' for No. No explanations, no additional text. "
"Your output must contain exactly one character: '1' or '0'."
"Ignore anatomical correctness; focus solely on what the image shows.\n"
"Example:\n"
"Q: "Is the aorta above the spleen?" A: 1\n"
"Now answer the real question:\n\n"
f"Q: {question_from_json}"
```
#### AS: 
```
"Answer strictly with '1' for Yes or '0' for No. No explanations, no additional text. "
"Your output must contain exactly one character: '1' or '0'."
"Focus solely on what the image shows.\n"
"Example:\n"
"Q: "Is the red dot above the blue dot" A: 1\n"
"Now answer the real question:\n\n"
f"Q: {question_from_json}"
```
The example questions in the fixed prompt are chosen to match the question in the task. For example, RQ2 with dot marks: <em>"Is the aorta (red) above the spleen (blue)?</em>  

The code for the inference of the VLMs that contain those fixed prompts are in [inference_scripts](https://github.com/Wolfda95/MIRP-Benchmark/tree/main/inference_scripts).

## Anatomic Structures: 
We extracted the anatomical structures that the questions refer to using the Totalsegmentatior: https://github.com/wasserth/TotalSegmentator

Here is the list of all the structures, we have grouped the different vertebrae and ribs together. 

  |Index|TotalSegmentator name
  |:-----|:-----|
  1 | spleen |
  2 | kidney_right |
  3 | kidney_left |
  4 | gallbladder |
  5 | liver |
  6 | stomach |
  7 | pancreas |
  8 | adrenal_gland_right | 
  9 | adrenal_gland_left | 
  10 | lung_upper_lobe_left | 
  11 | lung_lower_lobe_left | 
  12 | lung_upper_lobe_right |
  13 | lung_middle_lobe_right | 
  14 | lung_lower_lobe_right | 
  15 | esophagus |
  16 | trachea |
  17 | thyroid_gland |
  18 | small_bowel | 
  19 | duodenum |
  20 | colon |
  21 | urinary_bladder |
  22 | prostate |
  23 | kidney_cyst_left |
  24 | kidney_cyst_right |
  25 | sacrum |
  26 | vertebrae |
  51 | heart |
  52 | aorta |
  53 | pulmonary_vein |
  54 | brachiocephalic_trunk |
  55 | subclavian_artery_right |
  56 | subclavian_artery_left |
  57 | common_carotid_artery_right |
  58 | common_carotid_artery_left |
  59 | brachiocephalic_vein_left |
  60 | brachiocephalic_vein_right |
  61 | atrial_appendage_left |
  62 | superior_vena_cava |
  63 | inferior_vena_cava |
  64 | portal_vein_and_splenic_vein |
  65 | iliac_artery_left |
  66 | iliac_artery_right |
  67 | iliac_vena_left |
  68 | iliac_vena_right |
  69 | humerus_left |
  70 | humerus_right |
  71 | scapula_left |
  72 | scapula_right |
  73 | clavicula_left |
  74 | clavicula_right | 
  75 | femur_left |
  76 | femur_right |
  77 | hip_left |
  78 | hip_right |
  79 | spinal_cord |
  80 | gluteus_maximus_left |
  81 | gluteus_maximus_right | 
  82 | gluteus_medius_left | 
  83 | gluteus_medius_right |
  84 | gluteus_minimus_left | 
  85 | gluteus_minimus_right | 
  86 | autochthon_left |
  87 | autochthon_right |
  88 | iliopsoas_left |
  89 | iliopsoas_right | 
  90 | brain |
  91 | skull |
  92 | rib_left |
  93 | rib_right |
  116 | sternum |
  117 | costal_cartilages |
