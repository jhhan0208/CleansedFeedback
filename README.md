
# CleansedFeedback
![1_Logo](https://github.com/user-attachments/assets/12c328cf-6669-4b9a-8a67-51cfed81faef)
2025-1학기 소프트웨어융합 캡스톤 디자인으로 진행했던 순화된 피드백 제공 서비스, "CleansedFeedback"입니다.

# 🔥 프로젝트 소개

<img src="https://github.com/user-attachments/assets/cb4ad97b-022a-432c-8aa4-c4edb4f3fc2b" alt="2_기사" width="600"/>
  
영화, 드라마, 만화 등 예술 작품은 감동과 즐거움을 전달하며 관객과 소통하는 매개체로 관람 후 관객들은 댓글을 통해 감상평과 감정을 자유롭게 표현합니다.

하지만 이런 공간에는 작품과 작가를 향한 욕설과 악성 댓글도 존재하며, 이러한 부정적인 표현은 창작자와 다른 관람객 모두에게 마음의 상처를 남기고 건강한 소통 문화를 해칩니다.

![3_차별점](https://github.com/user-attachments/assets/1fb7d960-51ee-4ea1-af78-24e744a3af28)

이 문제를 해결하기 위해 비난표현을 분류/제거하는 연구나 순화하는 연구들이 존재합니다. 하지만 비난 분류/제거 연구의 경우 비난 섞인 피드백 댓글의 피드백도 제거될 위험이 있으며, 비난 순화 연구의 경우 비난만 있는 댓글에 대해서는 순화 의미가 없다는 단점이 있습니다.

그래서 본 프로젝트에서는 KcELECTRA 기반 Fine-tuned 모델들을 통해 댓글들을
- 중립 댓글
- 순수 피드백 댓글
- 순수 비난 댓글
- 비난 섞인 피드백 댓글<br>

의 네가지 유형으로 분류하고, 정말 비난만 있는 경우에는 기존의 비난 분류/제거 연구처럼 제거합니다.
단 비난이 존재하는 경우에도 피드백이 포함되어 있다면 비난은 순화, 피드백은 살려서 제공합니다.

<b>
이를 통해 "비난으로 인한 마음의 상처는 최소화하면서 피드백은 받아들여 더 좋은 작품을 만드는 데에 기여하는 것"이 목표입니다.
</b>

# ⚙️ 서비스 아키텍처
![그림5](https://github.com/user-attachments/assets/ea470749-5c5a-4d17-97b6-219452f384cc)

# 🔎 모델 성능 평가

비난 분류에는 기존 KcELECTRA 기반 Fine-tuned model 'beomi/korean-hatespeech-classifier'을 사용하였으며,<br>
https://huggingface.co/beomi/korean-hatespeech-classifier

피드백 분류에는 네이버 웹툰에 대해 피드백 여부를 LLM으로 라벨링한 dataset로 KcELECTRA 모델을 직접 Fine-tuning한 모델 'jhhan0208/feedback-classification-kcelectra-v1'을 사용하였습니다.<br>
https://huggingface.co/jhhan0208/feedback-classification-kcelectra-v1

### 1️⃣ LLM 라벨링 성능 평가<br>
1. 라벨링된 댓글들 중 200개 랜덤 샘플링<br>
2. 라벨을 가리고 사람(본인, 동료)이 직접 댓글의 피드백 여부를 판단<br>
3. 본인, 동료 불일치 라벨은 상의해서 결정, Gold Label 생성<br>
4. Gold Label과 LLM Label 얼마나 일치하는지 확인<br>

<img src="https://github.com/user-attachments/assets/35d801d6-649d-45be-9baa-07d9c947402b" width="300"/>

### 2️⃣ 피드백 분류 모델 성능 평가<br>
1. 전체 댓글을 80%의 Train set(2742개)와 20%의 Test set(685개)로 분할<br>
2. 5-Fold Cross Validation 진행<br>
3. 5개 Fold의 평균 지표(Accuracy, F1 Score)로 피드백 분류 모델 성능 확인<br>

<img src="https://github.com/user-attachments/assets/8e5e71ee-5a77-4032-a992-11c94f8a6401" width="300"/>

# 🎥 데모 영상

https://github.com/user-attachments/assets/c94f1f05-46bf-4819-966e-d2c0ccca5161

# ✔️ 결론
![6_결론](https://github.com/user-attachments/assets/a447a849-086b-4e82-bda2-7bda13cf63da)<br>

<b>
<p>• 평점이 낮은 웹툰일수록 순수 피드백의 비중은 줄고, 비난 섞인 피드백의 비중이 늘어나 서비스 필요성이 증가</p>
<p>• 서비스를 통해 순수 비난은 제거, 비난 섞인 피드백은 순수 피드백으로 변환하여 더 나은 댓글환경 조성 가능 </p>
<p>• 향후 네이버 웹툰 댓글 이외에도 피드백과 비난이 혼재하는 더 많은 환경에 프로젝트를 적용할 계획</p>
</b>
