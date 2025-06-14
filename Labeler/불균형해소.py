import pandas as pd

# 1. 데이터 로드
df = pd.read_csv("data/labeling_result.csv")
df = df.dropna(subset=['content', 'feedback_label'])
df = df.drop_duplicates(subset='content')
df['feedback_label'] = df['feedback_label'].astype(int)

# 2. 클래스별 분리
df_feedback = df[df['feedback_label'] == 0]               # 피드백 있음 (소수 클래스)
df_non_feedback = df[df['feedback_label'] == 1]           # 피드백 없음 (다수 클래스)

# 3. 피드백 없는 댓글을 2,000개만 샘플링
df_non_feedback_sampled = df_non_feedback.sample(n=2000, random_state=42)

# 4. 결합하여 균형 데이터셋 생성
df_balanced = pd.concat([df_feedback, df_non_feedback_sampled]).sample(frac=1, random_state=42)

# 분포 확인
print(df_balanced['feedback_label'].value_counts())

df_balanced.to_csv('data/balanced_labeling_result.csv', header=['content', 'lable'], index=False, encoding='utf-8-sig')
