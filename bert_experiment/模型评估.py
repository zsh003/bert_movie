import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
from sklearn.preprocessing import label_binarize
from itertools import cycle
# 假设 trainer.predict(val_dataset) 返回了 PredictionOutput 对象
# 或者您有 `y_true` (真实标签列表) 和 `y_pred` (预测标签列表), `y_prob` (预测概率列表 n_samples x n_classes)

# --- 以下代码需要在模型训练和预测之后运行 ---
# 假设已经通过 Trainer 的 predict 方法或手动推理获取了验证集/测试集的预测结果
# 示例数据 (需要替换为真实预测结果)
try:
    predictions = trainer.predict(val_dataset)
    y_true = predictions.label_ids
    y_pred = np.argmax(predictions.predictions, axis=-1)
    y_prob = torch.softmax(torch.from_numpy(predictions.predictions), dim=-1).numpy() # 获取概率
    labels = ["negative", "neutral", "positive"] # 类别标签
    n_classes = len(labels)
    print("已获取模型预测结果。")
except NameError:
    print("警告：未找到 `trainer` 或预测结果。将使用示例数据。")
    # 示例数据
    y_true = np.array([2, 0, 1, 2, 0, 1, 0, 2, 1])
    y_pred = np.array([2, 0, 1, 1, 0, 2, 0, 2, 1])
    # 示例概率 (n_samples, n_classes)
    y_prob = np.array([
        [0.1, 0.1, 0.8], [0.7, 0.2, 0.1], [0.2, 0.6, 0.2],
        [0.3, 0.5, 0.2], [0.9, 0.05, 0.05], [0.1, 0.3, 0.6],
        [0.8, 0.1, 0.1], [0.05, 0.15, 0.8], [0.1, 0.7, 0.2]
    ])
    labels = ["negative", "neutral", "positive"]
    n_classes = len(labels)


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

fpr = dict()
tpr = dict()
roc_auc = dict()

for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_prob[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# 计算 Micro-average ROC curve and ROC area
fpr["micro"], tpr["micro"], _ = roc_curve(y_true_bin.ravel(), y_prob.ravel())
roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

plt.figure(figsize=(10, 8))
lw = 2 # line width

# 绘制 Micro-average ROC curve
plt.plot(fpr["micro"], tpr["micro"],
         label='micro-average ROC curve (area = {0:0.3f})'
               ''.format(roc_auc["micro"]),
         color='deeppink', linestyle=':', linewidth=4)

# 绘制每个类别的 ROC curve
colors = cycle(['aqua', 'darkorange', 'cornflowerblue'])
for i, color in zip(range(n_classes), colors):
    plt.plot(fpr[i], tpr[i], color=color, lw=lw,
             label='ROC curve of class {0} ({1}) (area = {2:0.3f})'
             ''.format(i, labels[i], roc_auc[i]))

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

# 假设 df['tokenized_content'] 包含分词后的文本
all_words = ' '.join(df['tokenized_content'])

# 需要指定中文字体路径，否则中文会显示为方框
# font_path = 'C:/Windows/Fonts/simhei.ttf' # Windows SimHei 示例路径，请替换为你的字体路径
font_path = None # 如果没有合适字体，可以先不指定，但中文无法显示

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
