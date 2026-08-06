import os
os.environ['HF_HOME'] = 'D:\\huggingface'

import torch
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
from peft import LoraConfig
import json

# ================================================================
# 1. 加载模型和分词器
# ================================================================
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name='D:\\huggingface\\models\\Qwen2.5-1.5B',
    max_seq_length=512,       # 训练时每个样本最多 512 个 token
    dtype=torch.float16,      # 半精度
    load_in_4bit=True,        # 4-bit 量化（QLoRA），显存从 3GB 降到 1.5GB
)

# ================================================================
# 2. 给模型加 LoRA 适配器
# ================================================================
model = FastLanguageModel.get_peft_model(
    model,
    r=16,                     # LoRA rank：越大越强但也越耗显存，16 是平衡点
    target_modules=[          # 哪些层插 LoRA 矩阵？只插 Attention 的 Q/K/V/O
        'q_proj', 'k_proj', 'v_proj', 'o_proj',
    ],
    lora_alpha=16,            # 缩放系数，通常设成和 r 一样
    lora_dropout=0,           # dropout=0 反而更稳定
    use_gradient_checkpointing='unsloth',  # 用梯度换显存，显存不够时用
    random_state=42,
)

# 给分词器添加对话需要的特殊 token
special_tokens = ['<|im_start|>', '<|im_end|>']
for tok in special_tokens:
    if tok not in tokenizer.get_vocab():
        tokenizer.add_tokens([tok], special_tokens=True)
model.resize_token_embeddings(len(tokenizer))
tokenizer.chat_template = '{% for message in messages %}{{ \'<|im_start|>\' + message[\'role\'] + \'\\n\' + message[\'content\'] + \'<|im_end|>\' + \'\\n\' }}{% endfor %}'

# ================================================================
# 3. 准备训练数据
# ================================================================
with open('D:\\huggingface\\data\\train_200.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)[:50]  # 先跑 50 条看效果

# 手动拼对话格式（基座模型没有 chat_template）
def format_chat(examples):
    texts = []
    for inst, out in zip(examples['instruction'], examples['output']):
        text = (
            '<|im_start|>user\n' + inst + '<|im_end|>\n'
            '<|im_start|>assistant\n' + out + '<|im_end|>'
        )
        texts.append(text)
    return texts

formatted = [format_chat(x) for x in raw_data]

print('训练数据格式示例:')
print(formatted[0])
print()

# 组装成 datasets 格式
dataset = load_dataset('json', data_files={'train': 'D:\\huggingface\\data\\train_200.json'}, split='train')

# ================================================================
# 4. 配置训练器
# ================================================================
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    args=TrainingArguments(
        output_dir='D:\\huggingface\\output',   # 存模型的地方
        per_device_train_batch_size=1,           # 批次=1，你 4GB 显存只能塞 1 条
        gradient_accumulation_steps=4,           # 累积 4 步再更新权重（等效 batch=4）
        num_train_epochs=3,                      # 整个数据集重复训练 3 轮
        learning_rate=2e-4,                      # LoRA 常用学习率
        fp16=True,                               # 半精度训练
        save_strategy='no',                      # 不保存中间节点
        logging_steps=10,
        report_to='none',                        # 不上报给 wandb
    ),
    formatting_func=format_chat,                 # 自动把数据转成对话格式
)

# ================================================================
# 5. 开始训练
# ================================================================
print('开始训练...')
trainer.train()

# 保存 LoRA 权重
model.save_pretrained('D:\\huggingface\\output\\lora_model')
tokenizer.save_pretrained('D:\\huggingface\\output\\lora_model')
print('训练完成，模型已保存')
