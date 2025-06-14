from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

model_name = "jhhan0208/feedback-classification-kcelectra-v1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def classify2(sent):
    # 평가모드로 변경
    model.eval()

    # 입력된 문장 토크나이징
    tokenized_sent = tokenizer(
        sent,
        return_tensors="pt",
        truncation=True,
        add_special_tokens=True,
        max_length=128
    )

    # 예측
    with torch.no_grad():
        outputs = model(
            input_ids=tokenized_sent["input_ids"],
            attention_mask=tokenized_sent["attention_mask"],
            token_type_ids=tokenized_sent["token_type_ids"]
            )

    # 결과 return
    logits = outputs.logits # logits = outputs[0]

    probs = torch.softmax(logits, dim=1)
    pred = torch.argmax(probs, dim=1).item()
    labels = ["feedback", "none"]

    return labels[pred], probs[0][pred].item()

def filter_reviews2(df):
    labels = []
    scores = []

    for elem in df['content']:
      label, confidence = classify2(elem)

      labels.append(label)

      scores.append(round(confidence, 2))

    df['F_Label'] = labels # LABEL_0: 중립 / LABEL_1: 부정 / LABEL_2: 긍정
    df['F_Score'] = scores

    return df