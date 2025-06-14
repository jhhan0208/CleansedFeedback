from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# 모델과 토크나이저 로드
model_name = "beomi/korean-hatespeech-classifier"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def classify(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    probs = torch.softmax(logits, dim=1)
    pred = torch.argmax(probs, dim=1).item()
    labels = ["clean", "hate", "offensive"]
    return labels[pred], probs[0][pred].item()

def filter_reviews1(df):

    labels = []
    scores = []

    for elem in df['content']:
      label, confidence = classify(elem)

      labels.append(label)
      scores.append(round(confidence, 2))

    df['M_Label'] = labels # LABEL_0: 중립 / LABEL_1: 부정 / LABEL_2: 긍정
    df['M_Score'] = scores

    return df

