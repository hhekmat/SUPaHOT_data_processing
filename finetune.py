import os
import json
from transformers import AutoTokenizer, AutoModelForCausalLM, Seq2SeqTrainer, Seq2SeqTrainingArguments

def load_input_output_pairs(base_dir):
    input_output_pairs = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.jsonl'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    for line in f:
                        data = json.loads(line)
                        input_prompt = data.get("input_prompt")
                        output_text = data.get("output_text")
                        input_output_pairs.append((input_prompt, output_text))
    return input_output_pairs

def fine_tune_model(train_data, val_data, model_name, output_dir):
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        logging_dir='./logs',
        logging_steps=100,
        eval_steps=500,
        save_steps=500,
        evaluation_strategy="steps",
        save_total_limit=5,
        num_train_epochs=3,
        predict_with_generate=True,
        fp16=True,
        dataloader_num_workers=4,
        logging_first_step=True,
    )

    model = AutoModelForCausalLM.from_pretrained(model_name)

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_data,
        eval_dataset=val_data,
        tokenizer=tokenizer,
    )

    trainer.train()
    trainer.save_model(output_dir)

    print("Training completed!")

# Example usage
train_data_dir = './ft_datasets/task_1_train.jsonl'
val_data_dir = './ft_datasets/task_1_val.jsonl'
model_name = 'epfl-llm/meditron-7b'
output_dir = 'fine_tuned_model_output_directory'

train_data = load_input_output_pairs(train_data_dir)
val_data = load_input_output_pairs(val_data_dir)

fine_tune_model(train_data, val_data, model_name, output_dir)