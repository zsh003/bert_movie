import torch
from transformers import BertTokenizer, BertForSequenceClassification

# 定义标签映射
label_map = {0: 'negative', 1: 'positive'}

# 加载保存的模型和分词器
model_path = "saved_model"  # 替换为你实际保存模型的路径

# 加载分词器
tokenizer = BertTokenizer.from_pretrained(model_path)

# 加载模型
model = BertForSequenceClassification.from_pretrained(model_path)
model.eval()  # 设置模型为评估模式

# 检查是否有可用的GPU，如果没有则使用CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)  # 将模型移动到选定设备

# 准备输入文本
example_text = "我不喜欢这部电影"

# 对输入文本进行编码
inputs = tokenizer(example_text, return_tensors="pt")

# 如果有GPU，则将输入张量也移动到GPU上
inputs = {k: v.to(device) for k, v in inputs.items()}

# 使用模型进行预测
with torch.no_grad():
    outputs = model(**inputs)

# 获取预测结果
predictions = torch.argmax(outputs.logits, dim=-1).item()

# 映射预测结果到人类可读的标签
predicted_label = label_map[predictions]

print(f"Input text: {example_text}")
print(f"Predicted class: {predicted_label}")