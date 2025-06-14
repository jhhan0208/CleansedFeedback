import pandas as pd
import openai
from tqdm import tqdm
import time

# OpenAI 클라이언트 설정
OPENAI_API_KEY = 'My_Key'
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def cleanse_reviews(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()  # SettingWithCopyWarning 방지
    cleansed_texts = []

    for idx, row in tqdm(data.iterrows(), total=len(data)):
        if (row['final_hate'] != 'clean') and (row['final_feedback'] == 'feedback'):
            prompt = (
                f"다음 문장을 더 상냥하고 부드러운 말투로 고쳐줘.\n"
                f"원문: {row['content']}\n"
                f"상냥한 말투:"
            )

            for attempt in range(3):  # 최대 3번 재시도
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "너는 공격적인 문장을 예의 바르고 친절하게 바꾸는 전문가야."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    new_text = response.choices[0].message.content.strip()
                    cleansed_texts.append(new_text)
                    break  # 성공하면 반복 종료

                except Exception as e:
                    print(f"[{idx}] 오류 발생 (시도 {attempt+1}/3): {e}")
                    time.sleep(5)  # 오류 후 잠시 대기
                    if attempt == 2:
                        cleansed_texts.append(row['content'])

            time.sleep(0.5)  # 매 요청 간 대기 (RateLimit 방지)

        else:
            cleansed_texts.append(row['content'])

    data.loc[:, 'Cleansed'] = cleansed_texts
    return data

