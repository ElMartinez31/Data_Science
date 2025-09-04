Project Goals:

This project follows the course requirements:

Load a pre-trained model (GPT-2) and evaluate its baseline performance on a sequence classification task.

Perform parameter-efficient fine-tuning (PEFT) using LoRA on the same model.

Evaluate the LoRA-tuned model and compare it to the baseline (e.g., Accuracy, Macro-F1).

Save the trained LoRA adapters and include the notebook showing the whole process.



# Project structure:

# ├─ README.md
# ├─ requirements.txt
# ├─ notebooks/
# │  └─ Udacity_PEFT.ipynb
# ├─ models/
# │  └─ gpt2_lora_adapters/        
# ├─ results/
# │  ├─ baseline_metrics.json
# │  └─ lora_metrics.json
# ├─ .gitignore


# Environment installation:
use a Python virtual environment and install from requirements.txt
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

Dataset & Task:

Dataset: prasadsawant7/sentiment_analysis_preprocessed_dataset (Hugging Face 🤗 Datasets).

Task: Sentiment classification with 3 labels mapped as {0:"BAD", 1:"NEU", 2:"GOOD"}.

Loading: The notebook loads the dataset via datasets.load_dataset(...). No raw data files are stored in this repo.