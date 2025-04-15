import torch
from datasets import load_dataset
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments

# 检查是否有可用的GPU，如果没有则使用CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 加载IMDB数据集
dataset = load_dataset('imdb', data_files={
    'train': 'imdb_cache/aclImdb/train/**/*.txt',
    'test': 'imdb_cache/aclImdb/test/**/*.txt'
})

# 加载BERT分词器
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# 数据预处理函数
def preprocess_function(examples):
    return tokenizer(examples['text'], padding='max_length', truncation=True, max_length=512)

# 对整个数据集进行预处理
encoded_dataset = dataset.map(preprocess_function, batched=True)

# 设置训练参数
training_args = TrainingArguments(
    output_dir='results',          # 输出目录
    evaluation_strategy="epoch",     # 每个epoch后评估
    learning_rate=2e-5,              # 学习率
    per_device_train_batch_size=8,   # 训练时每个设备上的batch size
    per_device_eval_batch_size=8,    # 评估时每个设备上的batch size
    num_train_epochs=3,              # 训练周期数
    weight_decay=0.01,               # 权重衰减
    push_to_hub=False,               # 不推送至模型中心
)

# 加载BERT模型，num_labels设置为2因为是二分类问题（正面/负面）
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
model.to(device)  # 将模型移动到选定设备

# 使用Trainer API进行训练
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=encoded_dataset['train'].shuffle().select(range(1000)),  # 示例中只用了部分数据以节省时间
    eval_dataset=encoded_dataset['test'].shuffle().select(range(1000)),    # 同上
)

# 开始训练
trainer.train()

# 保存训练好的模型
trainer.save_model('./saved_model')

# 保存tokenizer
tokenizer.save_pretrained('./saved_model')

# 评估模型
results = trainer.evaluate()
print(results)

# 使用模型进行预测
example_text = "I really enjoyed this movie!"
inputs = tokenizer(example_text, return_tensors="pt")
# 将输入张量移动到与模型相同的设备
inputs = {k: v.to(device) for k, v in inputs.items()}
outputs = model(**inputs)
predictions = torch.argmax(outputs.logits, dim=-1).item()

# 映射预测结果到人类可读的标签
label_map = {0: 'negative', 1: 'positive'}
predicted_label = label_map[predictions]

print(f"Predicted class: {predicted_label}")