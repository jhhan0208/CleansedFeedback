import openai
import time
import re
import json

# OpenAI 클라이언트 설정
OPENAI_API_KEY = 'My_Key'
client = openai.OpenAI(api_key=OPENAI_API_KEY)


def cleanse_reviews(content: list) -> list:
    """
    주어진 문장 리스트에서 각 문장에 피드백이 포함되어 있는지 판단.
    피드백이 포함된 경우 0, 포함되지 않은 경우 1을 반환.
    
    Returns:
        list: 각 문장에 대한 라벨 (0: 피드백 있음, 1: 피드백 없음)
    """
    feedback_label = []

    for i in range(len(content)):
        sentence = content[i]

        prompt = (
            "다음 댓글에 피드백이 포함되어 있는지 판단해줘.\n\n"
            "피드백의 기준은 다음과 같아.\n\n"
            "1. 피드백의 종류는 다음과 같아.\n"
            "- \"문제점 제기\": EX) \"아우 캐릭터들 죄다 말 디게 많네..\" -> 0\n"
            "- \"보완 방법 제안\": EX) \"네비게이터들의 워프장치 정도만 소개하고 다른 과정은 적절히 스킵하는 것이 좋아보입니다.\" -> 0\n\n"
            "- \"느낀 개선점\" EX) \"이번 화는 유독 짧네..!!\" -> 0\n\n"
            "2. 피드백이 \"얼마나 피드백인지\"와는 관계 없이, 조금이라도 1의 요소가 있으면 피드백 O(0)으로 라벨링, 아니라면 피드백 X(1)로 라벨링한다.\n\n"
            "3. 구체적인 내용이 없는 텍스트의 경우 기본적으로 피드백 X(1)로 라벨링한다.\n"
            "- EX) \"12345\", \"ㅋㅋㅋㅋ\", \"??\" 등\n\n"
            "4. 피드백 여부는 비난 여부와는 관계가 없다.\n"
            "- EX) \"진짜 맞춤법 검사기도 안 돌리는건가 ㅋㅋ\": 비난이 포함되어 있음에도 맞춤법이 맞지 않다는 피드백이 존재 -> 0\n"
            "- EX) \"응원합니다\"는 비난은 포함되어 있지 않지만 피드백이 존재하지 않음 -> 1\n\n"
            f"댓글: \"{sentence}\"\n\n"
            "반드시 아래 형식으로만 응답해:\n"
            "{\"label\": 0} (0은 피드백 있음, 1은 피드백 없음)\n"
            "설명은 하지 마. 숫자 외의 다른 문장도 쓰지 마."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # 또는 "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "너는 댓글에서 피드백이 포함되어 있는지를 판단하는 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            raw = response.choices[0].message.content.strip()

            # 1단계: JSON으로 파싱 시도
            try:
                label = int(json.loads(raw).get("label", 1))
            except json.JSONDecodeError:
                # 2단계: 숫자만 추출 시도
                match = re.search(r"\b[01]\b", raw)
                label = int(match.group()) if match else 1

        except Exception as e:
            print(f"[Error] 문장 {i} 처리 중 오류 발생 → 기본값 1 적용. 메시지: {str(e)}")
            label = 1

        feedback_label.append(label)
        time.sleep(0.5)  # rate limit 보호

    return feedback_label