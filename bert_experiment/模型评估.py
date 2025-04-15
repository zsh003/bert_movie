import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
from sklearn.preprocessing import label_binarize
from itertools import cycle
from datasets import load_from_disk
from transformers import BertForSequenceClassification, Trainer
import torch
# 假设 trainer.predict(val_dataset) 返回了 PredictionOutput 对象
# 或者您有 `y_true` (真实标签列表) 和 `y_pred` (预测标签列表), `y_prob` (预测概率列表 n_samples x n_classes)
import matplotlib
#matplotlib.use('Agg')  # 使用非交互式后端

try:
    val_dataset = load_from_disk("./processed_val_dataset")  # 假设已保存预处理数据集
    model = BertForSequenceClassification.from_pretrained("./results_bert_finetune/final_model")
    trainer = Trainer(model=model)
    print("成功加载预训练模型和验证集")
except Exception as e:
    print(f"加载失败: {e}")
    val_dataset = None

try:
    trainer = None
    if trainer and val_dataset:
        predictions = trainer.predict(val_dataset)    
    else:
        raise NameError
    y_true = predictions.label_ids
    y_pred = np.argmax(predictions.predictions, axis=-1)
    y_prob = torch.softmax(torch.from_numpy(predictions.predictions), dim=-1).numpy() # 获取概率
    labels = ["negative", "neutral", "positive"] # 类别标签
    n_classes = len(labels)
    print("已获取模型预测结果。")
except NameError:
    print("警告：未找到 `trainer` 或预测结果。将使用示例数据。")
    # 生成的示例数据 (n_samples=200, 模拟 accuracy~80%)
    # 注意：以下数据为示例结构，请运行生成代码获取真实随机数据
    y_true = np.array([2, 1, 2, 0, 2, 1, 0, 0, 2, 1, 2, 0, 2, 1, 0, 2, 0, 1, 2, 2, 1, 0, 1, 2, 0, 1, 1, 1, 0, 2, 2, 0, 1, 2, 0, 2, 0, 0, 1, 2, 0, 2, 1, 2, 0, 1, 0, 2, 1, 1, 2, 0, 1, 1, 1, 0, 2, 1, 0, 2, 1, 0, 2, 2, 1, 0, 1, 1, 0, 2, 0, 1, 2, 1, 0, 1, 1, 0, 2, 0, 1, 2, 0, 1, 2, 0, 2, 1, 0, 2, 0, 0, 2, 1, 0, 2, 1, 0, 2, 0, 1, 2, 0, 2, 1, 0, 1, 2, 0, 2, 1, 2, 0, 1, 0, 1, 1, 0, 2, 0, 1, 2, 1, 0, 2, 1, 0, 2, 1, 1, 2, 2, 1, 0, 2, 1, 0, 2, 0, 1, 1, 1, 0, 2, 1, 0, 2, 0, 1, 2, 0, 1, 2, 0, 1, 1, 0, 2, 1, 0, 2, 1, 0, 2, 1, 0, 1, 0, 1, 2, 0, 2, 1, 0, 1, 2, 0, 2, 1, 2, 0, 1, 0, 2, 1, 0, 2, 0, 1, 1, 1, 0, 2, 1, 0, 2, 1, 0, 1, 1]) # (200,)
    print(len(y_true))
    y_pred = np.array([2, 1, 1, 0, 2, 2, 0, 0, 2, 1, 2, 0, 2, 1, 0, 2, 0, 1, 2, 2, 1, 0, 1, 2, 0, 1, 1, 1, 0, 2, 2, 0, 1, 2, 0, 2, 0, 0, 1, 2, 0, 2, 1, 2, 0, 1, 0, 2, 1, 1, 2, 0, 1, 1, 1, 0, 2, 1, 0, 2, 1, 0, 2, 2, 1, 0, 1, 1, 0, 2, 0, 1, 2, 1, 0, 1, 1, 0, 2, 0, 1, 2, 0, 1, 2, 0, 2, 1, 0, 2, 0, 0, 2, 1, 0, 2, 1, 0, 2, 0, 1, 2, 0, 2, 1, 0, 1, 2, 0, 2, 1, 2, 0, 1, 0, 1, 1, 0, 2, 0, 1, 2, 1, 0, 2, 1, 0, 2, 1, 1, 2, 2, 1, 0, 2, 1, 0, 2, 0, 1, 1, 1, 0, 2, 1, 0, 2, 0, 1, 2, 0, 1, 2, 0, 1, 1, 0, 2, 1, 0, 2, 1, 0, 2, 1, 0, 1, 0, 1, 2, 0, 2, 1, 0, 1, 2, 0, 2, 1, 2, 0, 1, 0, 2, 1, 0, 2, 0, 1, 1, 1, 0, 2, 1, 0, 2, 1, 0, 1, 1]) # (200,)
    print(len(y_pred))
    y_prob = np.array([
        [0.08, 0.12, 0.8 ], [0.15, 0.75, 0.1 ], [0.2,  0.6,  0.2 ], [0.85, 0.1,  0.05], [0.05, 0.1,  0.85],
        [0.1,  0.3,  0.6 ], [0.9,  0.05, 0.05], [0.7,  0.2,  0.1 ], [0.03, 0.07, 0.9 ], [0.1,  0.8,  0.1 ],
        [0.1,  0.15, 0.75], [0.75, 0.15, 0.1 ], [0.1,  0.05, 0.85], [0.2,  0.7,  0.1 ], [0.8,  0.15, 0.05],
        [0.07, 0.13, 0.8 ], [0.95, 0.03, 0.02], [0.15, 0.7,  0.15], [0.04, 0.06, 0.9 ], [0.06, 0.14, 0.8 ],
        [0.12, 0.78, 0.1 ], [0.88, 0.08, 0.04], [0.1,  0.8,  0.1 ], [0.02, 0.08, 0.9 ], [0.9,  0.07, 0.03],
        [0.15, 0.25, 0.6 ], [0.09, 0.82, 0.09], [0.11, 0.79, 0.1 ], [0.92, 0.05, 0.03], [0.06, 0.11, 0.83],
        [0.04, 0.09, 0.87], [0.85, 0.1,  0.05], [0.13, 0.74, 0.13], [0.03, 0.05, 0.92], [0.94, 0.04, 0.02],
        [0.08, 0.12, 0.8 ], [0.25, 0.65, 0.1 ], [0.82, 0.12, 0.06], [0.14, 0.76, 0.1 ], [0.05, 0.08, 0.87],
        [0.89, 0.06, 0.05], [0.07, 0.13, 0.8 ], [0.18, 0.72, 0.1 ], [0.09, 0.81, 0.1 ], [0.91, 0.05, 0.04],
        [0.06, 0.1,  0.84], [0.1,  0.7,  0.2 ], [0.04, 0.07, 0.89], [0.86, 0.09, 0.05], [0.16, 0.74, 0.1 ],
        [0.08, 0.1,  0.82], [0.1,  0.3,  0.6 ], [0.78, 0.15, 0.07], [0.05, 0.09, 0.86], [0.12, 0.75, 0.13],
        [0.83, 0.1,  0.07], [0.06, 0.08, 0.86], [0.9,  0.06, 0.04], [0.15, 0.75, 0.1 ], [0.04, 0.06, 0.9 ],
        [0.11, 0.78, 0.11], [0.87, 0.08, 0.05], [0.03, 0.07, 0.9 ], [0.13, 0.77, 0.1 ], [0.84, 0.11, 0.05],
        [0.07, 0.11, 0.82], [0.8,  0.13, 0.07], [0.17, 0.73, 0.1 ], [0.06, 0.09, 0.85], [0.1,  0.8,  0.1 ],
        [0.88, 0.07, 0.05], [0.05, 0.15, 0.8 ], [0.1,  0.75, 0.15], [0.81, 0.12, 0.07], [0.08, 0.1,  0.82],
        [0.85, 0.1,  0.05], [0.19, 0.71, 0.1 ], [0.07, 0.13, 0.8 ], [0.12, 0.76, 0.12], [0.89, 0.06, 0.05],
        [0.04, 0.08, 0.88], [0.1,  0.8,  0.1 ], [0.82, 0.11, 0.07], [0.09, 0.11, 0.8 ], [0.87, 0.09, 0.04],
        [0.14, 0.75, 0.11], [0.06, 0.1,  0.84], [0.11, 0.79, 0.1 ], [0.8,  0.14, 0.06], [0.05, 0.08, 0.87],
        [0.15, 0.7,  0.15], [0.9,  0.05, 0.05], [0.1,  0.2,  0.7 ], [0.13, 0.77, 0.1 ], [0.86, 0.08, 0.06],
        [0.07, 0.12, 0.81], [0.1,  0.7,  0.2 ], [0.84, 0.1,  0.06], [0.06, 0.09, 0.85], [0.17, 0.73, 0.1 ],# 100
        [0.83, 0.11, 0.06], [0.05, 0.1,  0.85], [0.1,  0.8,  0.1 ], [0.88, 0.07, 0.05], [0.18, 0.71, 0.11],
        [0.04, 0.06, 0.9 ], [0.12, 0.78, 0.1 ], [0.87, 0.08, 0.05], [0.08, 0.1,  0.82], [0.81, 0.13, 0.06],
        [0.16, 0.74, 0.1 ], [0.06, 0.11, 0.83], [0.1,  0.79, 0.11], [0.89, 0.06, 0.05], [0.07, 0.12, 0.81],
        [0.1,  0.7,  0.2 ], [0.03, 0.05, 0.92], [0.14, 0.76, 0.1 ], [0.85, 0.09, 0.06], [0.05, 0.1,  0.85],
        [0.15, 0.75, 0.1 ], [0.82, 0.12, 0.06], [0.09, 0.11, 0.8 ], [0.86, 0.08, 0.06], [0.1,  0.8,  0.1 ],
        [0.07, 0.13, 0.8 ], [0.8,  0.15, 0.05], [0.17, 0.72, 0.11], [0.06, 0.09, 0.85], [0.11, 0.78, 0.11],
        [0.9,  0.05, 0.05], [0.05, 0.15, 0.8 ], [0.1,  0.75, 0.15], [0.88, 0.07, 0.05], [0.08, 0.11, 0.81],
        [0.13, 0.76, 0.11], [0.84, 0.1,  0.06], [0.07, 0.1,  0.83], [0.1,  0.8,  0.1 ], [0.87, 0.08, 0.05],
        [0.83, 0.11, 0.06], [0.05, 0.1,  0.85], [0.1,  0.8,  0.1 ], [0.88, 0.07, 0.05], [0.18, 0.71, 0.11],
        [0.04, 0.06, 0.9 ], [0.12, 0.78, 0.1 ], [0.87, 0.08, 0.05], [0.08, 0.1,  0.82], [0.81, 0.13, 0.06],
        [0.83, 0.11, 0.06], [0.05, 0.1,  0.85], [0.1,  0.8,  0.1 ], [0.88, 0.07, 0.05], [0.18, 0.71, 0.11],
        [0.04, 0.06, 0.9 ], [0.12, 0.78, 0.1 ], [0.87, 0.08, 0.05], [0.08, 0.1,  0.82], [0.81, 0.13, 0.06],
        [0.16, 0.74, 0.1 ], [0.06, 0.11, 0.83], [0.1,  0.79, 0.11], [0.89, 0.06, 0.05], [0.07, 0.12, 0.81],
        [0.1,  0.7,  0.2 ], [0.03, 0.05, 0.92], [0.14, 0.76, 0.1 ], [0.85, 0.09, 0.06], [0.05, 0.1,  0.85],
        [0.15, 0.75, 0.1 ], [0.82, 0.12, 0.06], [0.09, 0.11, 0.8 ], [0.86, 0.08, 0.06], [0.1,  0.8,  0.1 ],
        [0.07, 0.13, 0.8 ], [0.8,  0.15, 0.05], [0.17, 0.72, 0.11], [0.06, 0.09, 0.85], [0.11, 0.78, 0.11],
        [0.9,  0.05, 0.05], [0.05, 0.15, 0.8 ], [0.1,  0.75, 0.15], [0.88, 0.07, 0.05], [0.08, 0.11, 0.81],
        [0.13, 0.76, 0.11], [0.84, 0.1,  0.06], [0.07, 0.1,  0.83], [0.1,  0.8,  0.1 ], [0.87, 0.08, 0.05],
        [0.83, 0.11, 0.06], [0.05, 0.1,  0.85], [0.1,  0.8,  0.1 ], [0.88, 0.07, 0.05], [0.18, 0.71, 0.11],
        [0.04, 0.06, 0.9 ], [0.12, 0.78, 0.1 ], [0.87, 0.08, 0.05], [0.08, 0.1,  0.82], [0.81, 0.13, 0.06]
    ])
    print(len(y_prob)) # 200 x 3 矩阵
    labels = ["negative", "neutral", "positive"]
    n_classes = len(labels)

# 数据加载部分
try:
    # 加载预处理后的数据
    df = pd.read_csv('processed_reviews.csv')
    print("成功加载预处理数据")
except FileNotFoundError:
    print("警告：未找到 processed_reviews.csv，将使用示例数据生成词云")
    # 创建示例数据
    data = {'tokenized_content': ['电影 太棒', '剧情 拖沓', '演员 演技', '不好看']}
    df = pd.DataFrame(data)



# --- 1. 混淆矩阵 ---
cm = confusion_matrix(y_true, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix')
# plt.savefig('confusion_matrix.png') # 保存图片
plt.show()

print("\n混淆矩阵:")
print(cm)

# --- 混淆矩阵可视化说明 ---
# 上述代码会生成一个热力图 (Heatmap)。
# 图表的 X 轴代表模型预测的类别，Y 轴代表真实的类别。
# 每个单元格中的数字表示该组合下的样本数量。例如，对角线上的数字表示预测正确的样本数 (TP)。
# 非对角线上的数字表示预测错误的样本数 (FP, FN)。
# 颜色深浅通常表示数量多少，可以直观看出模型在哪些类别之间容易混淆。


# --- 2. 分类报告 (精确率, 召回率, F1分数) ---
report = classification_report(y_true, y_pred, target_names=labels, digits=4)
print("\n分类报告:")
print(report)

# --- 分类报告可视化说明 ---
# 分类报告通常以文本形式展示，不直接生成图表，但其数据是评估模型性能的关键。
# Precision: 预测为该类别的样本中，实际是该类别的比例 (TP / (TP + FP))。
# Recall: 实际为该类别的样本中，被预测为该类别的比例 (TP / (TP + FN))。
# F1-score: Precision 和 Recall 的调和平均数 (2 * Precision * Recall / (Precision + Recall))。
# Support: 该类别的真实样本数量。
# Accuracy: 整体预测正确的比例。
# Macro avg: 各类别指标的算术平均值。
# Weighted avg: 各类别指标根据其 support 加权平均。


# --- 3. ROC 曲线 (适用于多分类) ---
# 需要将标签二值化
y_true_bin = label_binarize(y_true, classes=range(n_classes))

assert y_true_bin.shape[0] == y_prob.shape[0], f"数据维度不匹配: y_true样本数={y_true_bin.shape[0]}, y_prob样本数={y_prob.shape[0]}"
assert y_prob.shape[1] == n_classes, f"概率矩阵列数({y_prob.shape[1]})应与类别数({n_classes})一致"

fpr = dict()
tpr = dict()
roc_auc = dict()

for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_prob[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# 计算 Micro-average ROC curve and ROC area
fpr["micro"], tpr["micro"], _ = roc_curve(y_true_bin.ravel(), y_prob.ravel())
roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

n_samples = len(y_true)
plt.figure(figsize=(10, 8 + n_samples//1000))  # 根据样本量自动调整图像高度
lw = 2 # line width

# 绘制 Micro-average ROC curve
plt.plot(fpr["micro"], tpr["micro"],
         label='micro-average ROC curve (area = {0:0.3f})'
               ''.format(roc_auc["micro"]),
         color='deeppink', linestyle=':', linewidth=4)

for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_prob[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# 优化图例显示
plt.legend(
    loc='lower right' if n_samples < 500 else 'upper center',
    bbox_to_anchor=(1, 0.5) if n_samples >= 500 else None,
    fontsize='small' if n_samples > 1000 else 'medium'
)
# 优化坐标轴标签
plt.xticks(fontsize=8)
plt.yticks(fontsize=8)
plt.gca().xaxis.set_major_locator(plt.MaxNLocator(5))
plt.gca().yaxis.set_major_locator(plt.MaxNLocator(5))


plt.plot([0, 1], [0, 1], 'k--', lw=lw) # 绘制对角线
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Multi-class Receiver Operating Characteristic (ROC)')
plt.legend(loc="lower right")
# plt.savefig('roc_curve.png') # 保存图片
plt.show()

# --- ROC 曲线可视化说明 ---
# ROC 曲线展示了在不同的分类阈值下，模型的真阳性率（True Positive Rate, TPR，即Recall）相对于假阳性率（False Positive Rate, FPR）的变化情况。
# X 轴是 FPR (FP / (FP + TN))，Y 轴是 TPR (TP / (TP + FN))。
# 曲线越靠近左上角，表示模型性能越好（在较低的FPR下获得较高的TPR）。
# 对角虚线代表随机猜测的性能。
# AUC (Area Under the Curve) 是 ROC 曲线下的面积，是衡量模型整体区分能力的指标，值越接近 1 越好。
# 对于多分类问题，通常会绘制每个类别的 ROC 曲线（One-vs-Rest），以及宏平均（Macro-average）或微平均（Micro-average）的 ROC 曲线。微平均考虑了所有样本的预测结果。


# --- 4. 词云图 (基于评论文本) ---
from wordcloud import WordCloud
import matplotlib.pyplot as plt

try:
    # 确保列存在
    if 'tokenized_content' in df.columns:
        all_words = ' '.join(df['tokenized_content'])
    else:
        raise ValueError("数据中缺少 tokenized_content 列")
        
    # ... 原有词云生成代码 ...
except Exception as e:
    print(f"生成词云时出错: {e}")

# 需要指定中文字体路径，否则中文会显示为方框
font_path = 'C:/Windows/Fonts/simhei.ttf' # Windows SimHei 示例路径，请替换为你的字体路径
#font_path = None # 如果没有合适字体，可以先不指定，但中文无法显示

try:
    wordcloud = WordCloud(
        font_path=font_path, # 指定字体！
        width=800,
        height=400,
        background_color='white',
        # collocations=False, # 避免生成重复词组
        # max_words=100 # 限制最大词数
    ).generate(all_words)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Reviews')
    # plt.savefig('word_cloud.png')
    plt.show()

except RuntimeError as e:
     print(f"\n生成词云图时出错: {e}")
     print("请确保已安装 WordCloud 库 (pip install wordcloud) 并正确指定了中文字体路径 (font_path)。")
except ValueError as e:
    print(f"\n生成词云图时出错: {e}")
    print("可能是文本内容为空或格式错误。")


# --- 词云图可视化说明 ---
# 词云图直观地展示了文本中词语的频率。
# 出现频率越高的词语，在图中的字体越大。
# 可以帮助快速了解评论中讨论的热点话题和关键词。
# 生成中文词云需要指定包含中文字符的字体文件路径。


# --- 5. 情感趋势图 (需要时间戳数据) ---
# 假设原始数据 df 中有 'created_at' 列 和 'label' 列
# df['created_at'] = pd.to_datetime(df['created_at']) # 转换为 datetime 对象
# df.set_index('created_at', inplace=True)
# sentiment_counts = df.groupby([pd.Grouper(freq='D'), 'label']).size().unstack(fill_value=0)
# sentiment_counts.columns = [id2label[col] for col in sentiment_counts.columns] # 映射回标签名

# plt.figure(figsize=(12, 6))
# sentiment_counts.plot(kind='line', marker='o')
# plt.title('Sentiment Trend Over Time')
# plt.xlabel('Date')
# plt.ylabel('Number of Reviews')
# plt.legend(title='Sentiment')
# plt.grid(True)
# plt.tight_layout()
# # plt.savefig('sentiment_trend.png')
# plt.show()

# --- 情感趋势图可视化说明 ---
# 这通常是一个折线图。
# X 轴代表时间（例如按天、周、月聚合）。
# Y 轴代表评论的数量。
# 图中包含多条线，每条线代表一种情感倾向（积极、中性、消极）的评论数量随时间的变化。
# 可以帮助分析特定事件（如电影上映、口碑发酵）对用户情感的影响，或者观察整体情感的演变趋势。
# 需要数据中包含评论的时间戳信息。


# --- 6. 评分分布图 (需要评分数据) ---
# 假设原始数据 df 中有 'rating' 列
# plt.figure(figsize=(8, 5))
# sns.histplot(df['rating'], bins=10, kde=False) # 或者 sns.countplot(x='rating', data=df)
# plt.title('Distribution of Movie Ratings')
# plt.xlabel('Rating Score')
# plt.ylabel('Number of Reviews/Movies')
# # plt.savefig('rating_distribution.png')
# plt.show()

# --- 评分分布图可视化说明 ---
# 这通常是一个直方图或条形图。
# X 轴代表评分值（例如 1 到 5 星，或具体分数）。
# Y 轴代表给出该评分的评论数量（或拥有该评分的电影数量）。
# 可以帮助了解用户评分的整体分布情况，是倾向于高分还是低分，或者是否存在两极分化等现象。
# 需要数据中包含用户评分信息。
