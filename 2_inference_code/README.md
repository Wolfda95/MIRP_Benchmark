# Inference

### Prerequisite: 
- Downloaded MIRP Benchmark Dataset (Instructions: [`1_dataset_guide/`](https://github.com/Wolfda95/MIRP_Benchmark/tree/main/1_dataset_guide))
- For open models: Nvidia GPU with sufficient memory to run the model (We used A6000 48GB) || For closed model: OpenAI API key

### Run Inference: 
Each model is executed via a separate script.  <br>
Each script passes one image-question pair after another throught the model. The model answers are saved in a json file. <br>
You find detailed instructions on how to run the script for each model either in the docstring of the python file or below in the toggel bars. 

### Next Step: 


This directory contains the inference scripts for GPT4o, JanusPro, Llama3.2 and Pixtral, each executed via separate scripts. 



## Dependencies

In addition to standard Python packages (`os`, `sys`, `json`, `random`, `time`, `torch`), some scripts require additional model-specific dependencies, e.g. `openai`, `vllm`, `transformers`

## Documentation

Each inference script includes a **detailed docstring** with relevant information, such as required dependencies and further instructions. Additionally, all scripts are extensively documented with **comments, docstrings, and descriptions** to ensure clarity and usability.
