from transformers import BertTokenizer, BertForSequenceClassification
import torch
import torch.nn.functional as F

# 加载微调后的模型和 Tokenizer
model_path = "./results_bert_finetune/final_model"
try:
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertForSequenceClassification.from_pretrained(model_path)
    model.eval() # 设置为评估模式
    print(f"从 '{model_path}' 加载模型成功。")
except OSError:
    print(f"错误：无法从 '{model_path}' 加载模型或 Tokenizer。请确保路径正确且模型已训练保存。")
    exit()


# 待分析的文本
texts = [
    "这部电影的视觉效果令人惊叹，故事也很感人！",
    "感觉剧情平平无奇，没什么亮点。",
    "导演的叙事手法很大胆，毁誉参半吧。",
    "非常失望，浪费了我的时间和金钱。"
]

# 情感标签映射
id2label = {0: "negative", 1: "neutral", 2: "positive"}

# 进行推理
print("\n情感分析推理结果:")
with torch.no_grad():
    for text in texts:
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = F.softmax(logits, dim=-1)
        predicted_class_id = torch.argmax(probabilities, dim=-1).item()
        predicted_label = id2label[predicted_class_id]
        confidence = probabilities[0][predicted_class_id].item()

        print(f"文本: {text}")
        print(f"  预测情感: {predicted_label}")
        print(f"  置信度: {confidence:.4f}")
        print(f"  概率分布 (neg, neu, pos): {probabilities.numpy()[0]}")
        print("-" * 20)