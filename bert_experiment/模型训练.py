import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
import torch
from datasets import Dataset # 需要安装 datasets: pip install datasets

# --- 假设你已经运行了 5.1 的代码并得到了 df ---
# 或者从已处理的文件加载
try:
    df = pd.read_csv('processed_reviews.csv')
    if 'label' not in df.columns:
        raise ValueError("处理后的数据文件需要包含 'label' 列。")
except FileNotFoundError:
     print("错误：'processed_reviews.csv' 未找到。请先运行5.1的预处理代码。")
     # 创建示例数据
     data = {'cleaned_content': ['这部 电影 太棒了', '剧情 有点 拖沓', '演员 演技 在线', '不 好看'],
             'label': [2, 0, 2, 0]}
     df = pd.DataFrame(data)
     print("已创建示例数据进行演示。")
except ValueError as e:
    print(f"错误: {e}")
    exit()


# 划分训练集和验证集
train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)

# 将 Pandas DataFrame 转换为 Hugging Face Dataset 对象
train_dataset = Dataset.from_pandas(train_df)
val_dataset = Dataset.from_pandas(val_df)

# 加载 Tokenizer
model_name = 'bert-base-chinese'
try:
    tokenizer = BertTokenizer.from_pretrained(model_name)
except OSError:
     print(f"错误：无法下载或找到 '{model_name}' 的 tokenizer。请检查网络连接或模型名称。")
     exit()


# 定义预处理函数
def preprocess_function(examples):
    # 使用 cleaned_content 列进行 tokenize
    return tokenizer(examples['cleaned_content'], padding='max_length', truncation=True, max_length=128)

# 应用预处理
train_dataset = train_dataset.map(preprocess_function, batched=True)
val_dataset = val_dataset.map(preprocess_function, batched=True)

# 设置 Dataset 格式，移除不需要的列，重命名 label 列
train_dataset = train_dataset.remove_columns(['__index_level_0__', 'cleaned_content', 'tokenized_content'] if '__index_level_0__' in train_dataset.column_names else ['cleaned_content', 'tokenized_content'])
val_dataset = val_dataset.remove_columns(['__index_level_0__', 'cleaned_content', 'tokenized_content'] if '__index_level_0__' in val_dataset.column_names else ['cleaned_content', 'tokenized_content'])
# train_dataset = train_dataset.rename_column("label", "labels") # Trainer 默认需要 'labels' 列
# val_dataset = val_dataset.rename_column("label", "labels")
train_dataset.set_format('torch')
val_dataset.set_format('torch')


# 加载预训练模型，指定类别数量 (positive, neutral, negative -> 3)
try:
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=3)
except OSError:
     print(f"错误：无法下载或找到 '{model_name}' 的模型。请检查网络连接或模型名称。")
     exit()

# 定义训练参数
training_args = TrainingArguments(
    output_dir='./results_bert_finetune', # 输出目录
    num_train_epochs=1,                  # 训练轮数 (示例减少轮数)
    per_device_train_batch_size=4,       # 减小 batch size 以适应内存 (示例)
    per_device_eval_batch_size=8,
    warmup_steps=10,                     # 减小 warmup steps (示例)
    weight_decay=0.01,
    logging_dir='./logs_bert',           # 日志目录
    logging_steps=10,
    evaluation_strategy="epoch",         # 每个 epoch 结束时评估
    save_strategy="epoch",               # 每个 epoch 结束时保存模型
    load_best_model_at_end=True,         # 训练结束时加载最佳模型
    metric_for_best_model="accuracy",    # 使用准确率作为最佳模型指标
)

# 定义评估指标 (可选，更精细化评估)
import numpy as np
from datasets import load_metric

metric = load_metric("accuracy") # 可以添加 F1, Precision, Recall 等

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

# 初始化 Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics, # 添加评估指标计算函数
)

# 开始训练 (需要 GPU 加速效果更佳)
print("开始模型微调...")
try:
    trainer.train()
    print("模型训练完成。")
    # 保存最终模型和 tokenizer
    trainer.save_model("./results_bert_finetune/final_model")
    tokenizer.save_pretrained("./results_bert_finetune/final_model")
    print("最终模型已保存。")
except Exception as e:
    print(f"模型训练过程中发生错误: {e}")
