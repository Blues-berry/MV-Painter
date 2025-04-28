import os
from PIL import Image, ImageDraw, ImageFont
from glob import glob
from tqdm import tqdm
import torch
from prompts import Prompts
from transformers import AutoModelForCausalLM, AutoTokenizer

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', type=str)
args = parser.parse_args()



model_name = "Qwen/Qwen2.5-32B-Instruct"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    # device_map="auto"
)
model.to(torch.device('cuda'))

tokenizer = AutoTokenizer.from_pretrained(model_name)

system_prompt = Prompts().correct_prompt

root_dir = args.input_dir

for filename in os.listdir(root_dir):
    if filename.endswith(".png"):
        txt_filename = os.path.splitext(filename)[0] + ".txt"
        txt_path = os.path.join(root_dir, txt_filename)
        with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()

                final_answer_index = content.find("### Final Answer")

                if final_answer_index != -1:
                    content_before_final = content[:final_answer_index].strip()
                else:
                    content_before_final = content.strip()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content_before_final}
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        print(response)



        file_name = f"{txt_path.replace('.txt','_final.txt')}"  # 生成文件名
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(response)  # 将 response 写入文件
            print(f"Saved response  to '{file_name}'")
