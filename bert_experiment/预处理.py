import pandas as pd
import re
import jieba # 需要提前安装: pip install jieba

# 假设您有一个包含评论数据的CSV文件 'reviews.csv'
# 列名可能包含 'review_id', 'content', 'raw_sentiment' (如果做了初步标注)
try:
    df = pd.read_csv('reviews.csv')
except FileNotFoundError:
    print("错误：'reviews.csv' 未找到。请确保数据文件存在。")
    # 在此可以创建一个示例 DataFrame 用于演示
    data = {'review_id': [1, 2, 3, 4, 5, 5],
            'content': ['这部电影太棒了！', '剧情有点拖沓。', None, '演员演技在线！', '不好看。', '不好看。'],
            'raw_sentiment': ['positive', 'negative', 'neutral', 'positive', 'negative', 'negative']}
    df = pd.DataFrame(data)
    print("已创建示例数据进行演示。")


print(f"原始数据量: {len(df)}")

# 1. 数据清洗
# 1.1 去除重复评论 (基于内容)
df.drop_duplicates(subset=['content'], keep='first', inplace=True)
print(f"去除内容重复后数据量: {len(df)}")

# 1.2 处理缺失值 (例如，删除内容为空的评论)
df.dropna(subset=['content'], inplace=True)
print(f"去除内容为空后数据量: {len(df)}")

# 1.3 文本清洗 (示例: 去除特殊字符、多余空格)
def clean_text(text):
    if isinstance(text, str):
        text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9\s]", "", text) # 保留中英文、数字、空格
        text = re.sub(r"\s+", " ", text).strip() # 去除多余空格
        return text
    return ""

df['cleaned_content'] = df['content'].apply(clean_text)
# 删除清洗后为空的内容
df = df[df['cleaned_content'] != ""]
print(f"文本清洗后数据量: {len(df)}")


# 2. 中文分词 (使用 jieba)
# 可以加载自定义词典和停用词表
# jieba.load_userdict('user_dict.txt')
# stopwords = set(line.strip() for line in open('stopwords.txt', encoding='utf-8'))

def tokenize_chinese(text):
    words = jieba.cut(text)
    # filtered_words = [word for word in words if word not in stopwords and len(word.strip()) > 0]
    # 简化示例：仅分词
    filtered_words = [word for word in words if len(word.strip()) > 0]
    return " ".join(filtered_words) # 返回以空格分隔的词

df['tokenized_content'] = df['cleaned_content'].apply(tokenize_chinese)

# 3. 标签映射 (假设已有初步标注 'raw_sentiment')
# 将 'positive', 'neutral', 'negative' 映射为 0, 1, 2
sentiment_map = {'positive': 2, 'neutral': 1, 'negative': 0}
# 假设存在名为 'raw_sentiment' 的列
if 'raw_sentiment' in df.columns:
    df['label'] = df['raw_sentiment'].map(sentiment_map)
    # 处理无法映射的情况 (可选)
    df.dropna(subset=['label'], inplace=True)
    df['label'] = df['label'].astype(int)
    print("标签已映射为数字。")
else:
    print("警告：数据中缺少'raw_sentiment'列，无法进行标签映射。")


# 查看处理后的数据
print("\n处理后的数据示例:")
print(df[['cleaned_content', 'tokenized_content', 'label' if 'label' in df.columns else 'cleaned_content']].head())

# 保存处理后的数据 (可选)
# df.to_csv('processed_reviews.csv', index=False)