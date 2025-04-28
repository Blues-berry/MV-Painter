import os
from PIL import Image, ImageDraw, ImageFont
from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
from glob import glob
from tqdm import tqdm
import torch
from prompts import Prompts
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--dir_a', type=str)
parser.add_argument('--dir_b', type=str)
parser.add_argument('--output_dir', type=str)

args = parser.parse_args()
dir_a = args.dir_a
dir_b = args.dir_b
image_names = ['000.png', '001.png', '002.png', '003.png']
image_rel_path = 'image'
output_dir = args.output_dir
os.makedirs(output_dir, exist_ok=True)



# prepare qwen
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2.5-VL-32B-Instruct",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
)
model.to(torch.device('cuda'))
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-32B-Instruct")






# settings
border_thickness = 6
margin = 10
text_padding = 8
label_font_size = 32
left_color = (40, 80, 180)   
right_color = (150, 40, 60)  
text_color = (255, 255, 255) 

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", label_font_size)

except:
    font = ImageFont.load_default()

subfolders = [f for f in os.listdir(dir_a) if os.path.isdir(os.path.join(dir_a, f))]

for folder in subfolders:
    images = []

    for img_name in image_names:
        img_path = os.path.join(dir_a, folder,'predict',folder, image_rel_path,img_name)
        images.append(Image.open(img_path).convert('RGB'))

    for img_name in image_names:
        img_path = os.path.join(dir_b, folder,'predict',folder, image_rel_path,img_name)
        images.append(Image.open(img_path).convert('RGB'))

    w, h = images[0].size

    group_w = 2 * w
    group_h = 2 * h
    total_w = group_w * 2 + 3 * margin
    total_h = group_h + 2 * margin

    canvas = Image.new('RGB', (total_w, total_h), (255, 255, 255))  # 白色背景
    draw = ImageDraw.Draw(canvas)

    for idx in range(4):
        row = idx // 2
        col = idx % 2
        x = margin + col * w
        y = margin + row * h
        canvas.paste(images[idx], (x, y))

    for idx in range(4, 8):
        row = (idx - 4) // 2
        col = (idx - 4) % 2
        x = margin * 2 + group_w + col * w
        y = margin + row * h
        canvas.paste(images[idx], (x, y))

    left_rect = [margin - border_thickness, margin - border_thickness,
                 margin + group_w + border_thickness - 1, margin + group_h + border_thickness - 1]
    draw.rectangle(left_rect, outline=left_color, width=border_thickness)

    right_rect = [margin * 2 + group_w - border_thickness, margin - border_thickness,
                  total_w - margin + border_thickness - 1, margin + group_h + border_thickness - 1]
    draw.rectangle(right_rect, outline=right_color, width=border_thickness)

    draw.rectangle([margin, 0, margin + 80, margin - text_padding + label_font_size], fill=left_color)
    draw.text((margin + 6, 2), "Left", font=font, fill=text_color)

    draw.rectangle([margin * 2 + group_w, 0, margin * 2 + group_w + 100, margin - text_padding + label_font_size], fill=right_color)
    draw.text((margin * 2 + group_w + 6, 2), "Right", font=font, fill=text_color)

    output_path = os.path.join(output_dir, f'{folder}.png')
    canvas.save(output_path)
    print(f'Saved comparison image for {folder} at {output_path}')


    



    ################## qwen 2.5 vl chat ##################
    system_prompt = Prompts().four_views_prompt
    img_path = output_path
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": f"file://{img_path}",
                },
                {"type": "text", "text": system_prompt},
            ],
        }
    ]
    # Preparation for inference
    text = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to("cuda")


    # Inference: Generation of the output
    generated_ids = model.generate(**inputs, max_new_tokens=1024)
    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    output_text = output_text[0]
    
    print(output_text)

    file_name = f"{img_path.replace('.png','.txt')}"  # 生成文件名
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(output_text)  # 将 response 写入文件
        print(f"Saved response  to '{file_name}'")

