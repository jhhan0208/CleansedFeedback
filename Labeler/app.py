import pandas as pd
import os
import time
from GPT_Labeler import cleanse_reviews  # 라벨링 함수 (안정성 강화 버전)

# === 설정 ===
csv_input_path = 'data/merged_result.csv'
csv_output_path = 'data/labeling_result.csv'

CHUNK_SIZE = 40  # A: 한 번에 처리할 문장 수
BATCH_SIZE = 20    # B: GPT 호출 단위

# === 입력 데이터 로드 ===
df = pd.read_csv(csv_input_path)
content = list(df['content'])
total = len(content)

# === 이미 처리된 개수 확인 ===
if os.path.exists(csv_output_path):
    processed_df = pd.read_csv(csv_output_path)
    start_idx = len(processed_df)
    print(f"✅ 이전에 {start_idx}개 처리됨. 이어서 실행합니다.")
else:
    start_idx = 0
    print("🚀 처음부터 시작합니다.")

# === 청크별 처리 ===
for chunk_start in range(start_idx, total, CHUNK_SIZE):
    chunk_end = min(chunk_start + CHUNK_SIZE, total)
    chunk = content[chunk_start:chunk_end]
    labels = []

    print(f"\n🔄 {chunk_start} ~ {chunk_end} 문장 처리 중...")

    for i in range(0, len(chunk), BATCH_SIZE):
        sub_chunk = chunk[i:i + BATCH_SIZE]
        try:
            batch_labels = cleanse_reviews(sub_chunk)
        except Exception as e:
            print(f"[Error] 청크 {i} ~ {i+BATCH_SIZE} 처리 실패: {e}")
            batch_labels = [1] * len(sub_chunk)  # fallback

        labels.extend(batch_labels)

    # === 결과 저장 ===
    chunk_df = pd.DataFrame({
        'content': chunk,
        'label': labels # feedback_label': labels
    })

    # append 모드로 저장
    if not os.path.exists(csv_output_path):
        chunk_df.to_csv(csv_output_path, index=False, encoding='utf-8-sig')
    else:
        chunk_df.to_csv(csv_output_path, mode='a', header=False, index=False, encoding='utf-8-sig')

    print(f"✅ 저장 완료: {chunk_start} ~ {chunk_end} 문장")

    # 지연 주기 (원하면 비활성화 가능)
    time.sleep(3)

