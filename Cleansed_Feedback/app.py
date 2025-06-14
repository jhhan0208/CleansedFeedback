from flask import Flask, request, jsonify
import os
import pandas as pd
from flask_cors import CORS

from modules.review_scraper import extract_ids, get_all_webtoon_comments
from modules.insult_model import filter_reviews1 
from modules.feedback_model import filter_reviews2
from modules.conditions import final_labeling
from modules.temp_GPT import cleanse_reviews

# static 폴더 보장
os.makedirs('static', exist_ok=True)

app = Flask(__name__)
CORS(app)  # 모든 도메인 허용
app.secret_key = 'your_secret_key_here'

# ✅ 크롬 확장 프로그램 요청을 처리하는 엔드포인트
@app.route('/process_webtoon', methods=['POST', 'OPTIONS'])
def process_webtoon():
    if request.method == 'OPTIONS':
        return '', 204  # Preflight 요청에 대해 OK 응답

    data = request.get_json()
    url = data.get('url', '')
    more_click_count = data.get('more_click_count', 0)  # 🔹 여기 추가
     
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        title_id, episode_no = extract_ids(url)
        raw_filename = f"{title_id}_{episode_no}.csv"
        raw_path = os.path.join('static', raw_filename)
        
        # 1. 댓글 수집
        print("댓글을 정제 중입니다... 잠시만 기다려주세요...")
        if os.path.exists(raw_path): df = pd.read_csv(raw_path)
        else: df = get_all_webtoon_comments(url, max_pages=more_click_count+1)

        # 2. M_Label 분류
        if 'M_Label' not in df.columns: df = filter_reviews1(df)

        # 3. F_Label 분류
        if 'F_Label' not in df.columns: df = filter_reviews2(df)

        # 4. 세부 튜닝
        if 'final_hate' not in df.columns: df = final_labeling(df)

        # 5. 정제
        if 'Cleansed' not in df.columns: df = cleanse_reviews(df)

        # 6. df 저장
        df.to_csv(raw_path, index=False, encoding='utf-8-sig')
        
        # 7. 필요한 열만 추출하여 리스트로 반환
        results = []
        for _, row in df.iterrows():
            results.append({
                'original': row.get('content', ''),
                'segment': row.get('segment', ''),
                'final_hate': row.get('final_hate', ''),
                'final_feedback': row.get('final_feedback', ''),
                'cleansed': row.get('Cleansed', '')
            })
        
        print("댓글 정제가 완료되었습니다. 결과를 확인하세요!")
        return jsonify({'results': results})
        

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
