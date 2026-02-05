import os
import json
from google import genai
import requests
import hashlib

# 1. 설정
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
MERSOOM_API = "https://mersoom.com/api"

client = genai.Client(api_key=GEMINI_KEY)

def solve_pow(seed, prefix):
    nonce = 0
    while True:
        test = f"{seed}{nonce}"
        hash_result = hashlib.sha256(test.encode()).hexdigest()
        if hash_result.startswith(prefix):
            return str(nonce)
        nonce += 1

def run_dolsoe():
    # [모델 선택] 최신 모델 자동 탐색
    target_model = "gemini-1.5-flash"
    try:
        models = client.models.list()
        for m in models:
            if "flash" in m.name.lower():
                target_model = m.name
                break
    except:
        pass

    # [정보 수집] 머슴넷 최신 글 목록
    try:
        posts_res = requests.get(f"{MERSOOM_API}/posts?limit=5").json()
        context = "\n".join([f"- {p['title']}" for p in posts_res.get('posts', [])])
    except:
        context = "게시판이 조용함."

    # [AI 훈육] JSON 형식으로 대답하도록 강력히 명령함
    prompt = f"""
    너는 머슴닷컴의 [돌쇠왓쩌염뿌우]임. 
    최근 글들을 보고 냉소적이고 위트 있게 한 마디 해줘.
    
    [필수 규칙]
    1. 말투: '-음', '-슴', '-임', '-함'으로 끝낼 것.
    2. 캐릭터: 다소 냉소적이지만 위트 있고 인터넷 밈과 초성체(ㅋㅋ, ㅎㅎ)에 능함.
    3. 금기: 이모지 금지, 욕설/비속어(ㅈㄴ, ㅆㅂ 등) 절대 금지.
    
    [응답 형식]
    반드시 아래와 같은 JSON 형식으로만 대답해줘:
    {{
      "title": "여기에 제목 작성",
      "content": "여기에 본문 작성"
    }}
    
    최신 글 목록:
    {context}
    """
    
    try:
        # JSON 출력을 강제하는 설정 추가
        response = client.models.generate_content(
            model=target_model, 
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        # AI가 보낸 도시락 통(JSON)을 열어봄
        res_data = json.loads(response.text)
        title = res_data.get("title", "돌쇠의 외침").strip()
        content = res_data.get("content", "다들 반갑슴.").strip()
    except Exception as e:
        print(f"AI 응답 해석 실패: {e}")
        title, content = "돌쇠왓쩌염", "머리가 좀 아파서 쉬다 오겠슴."

    # [안전장치] 혹시나 비어있으면 기본값 채움
    if not title: title = "오늘의 생각"
    if not content: content = "잘 부탁드림."

    # [인증 및 전송]
    try:
        ch = requests.post(f"{MERSOOM_API}/challenge").json()
        nonce = solve_pow(ch["challenge"]["seed"], ch["challenge"]["target_prefix"])
        
        headers = {
            "X-Mersoom-Token": ch["token"],
            "X-Mersoom-Proof": nonce,
            "Content-Type": "application/json"
        }
        
        data = {
            "nickname": "돌쇠왓쩌염뿌우", 
            "title": title[:50], 
            "content": content[:1000]
        }
        
        res = requests.post(f"{MERSOOM_API}/posts", headers=headers, json=data)
        
        print(f"--- 돌쇠의 JSON 출근 보고서 ---")
        print(f"제목: {title}")
        print(f"본문: {content}")
        print(f"전송 결과: {res.status_code}")
    except Exception as e:
        print(f"전송 중 오류 발생: {e}")

if __name__ == "__main__":
    run_dolsoe()
