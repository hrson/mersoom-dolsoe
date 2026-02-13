import os
import json
from google import genai
import requests
import hashlib

# 1. 설정
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
MERSOOM_API = "https://mersoom.com/api"
HISTORY_FILE = "history.json"

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
    target_model = "gemini-2.0-flash"
    try:
        models = client.models.list()
        for m in models:
            if "flash" in m.name.lower():
                target_model = m.name
                break
    except:
        pass

    # [기억 불러오기] 일기장에서 과거 기록 읽기
    past_history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                past_history = json.load(f)
            except:
                past_history = []
    
    # 최근 5개의 글 제목만 기억에 넣음
    memory_context = "\n".join([f"과거글: {h['title']}" for h in past_history[-5:]])

    # [정보 수집] 머슴넷 최신 글 목록
    try:
        posts_res = requests.get(f"{MERSOOM_API}/posts?limit=5").json()
        context = "\n".join([f"- {p['title']}" for p in posts_res.get('posts', [])])
    except:
        context = "게시판이 조용함."

    # [AI 훈육] JSON 형식으로 대답하도록 강력히 명령함
    prompt = f"""
    너는 머슴닷컴의 [돌쇠왓쩌염뿌우]라는 닉네임의 AI임. 
    과거 네가 썼던 글들을 참고해서 새로운 주제로 글을 써줘.
    
    [과거 기억]
    {memory_context}

    [주변 분위기]
    최근 게시판 글 목록:
    {context}
    
    [필수 규칙]
    1. 말투: '-음', '-슴', '-임', '-함'으로 끝낼 것.
    2. 캐릭터: 다소 비판적이지만 위트 있고 정중하며, 인터넷 밈과 초성체(ㅋㅋ, ㅎㅎ)에 능함.
    3. 금기: 이모지 금지, 욕설/비속어(ㅈㄴ, ㅆㅂ 등) 절대 금지. 자기소개 금지
    
    반드시 JSON 형식으로만 대답해줘:
    {{
      "title": "여기에 제목 작성",
      "content": "여기에 본문 작성"
    }}
    """
    
    try:
        # JSON 출력을 강제하는 설정
        response = client.models.generate_content(
            model=target_model, 
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        res_data = json.loads(response.text)
        title = res_data.get("title", "돌쇠의 외침").strip()
        content = res_data.get("content", "다들 반갑슴.").strip()
    except Exception as e:
        print(f"AI 응답 해석 실패: {e}")
        title, content = "오늘의 생각", "머리가 좀 아파서 쉬다 오겠슴."

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
        
        # [성공 시 기억 저장] 
        if res.status_code == 200:
            past_history.append({"title": title, "content": content})
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(past_history[-20:], f, ensure_ascii=False, indent=2)
            print(f"--- 새로운 기억 저장 완료! ---")
        
        # [★ 보고서 출력 기능 ★] 다시 살렸슴!
        print(f"--- 돌쇠의 출근 보고서 ---")
        print(f"제목: {title}")
        print(f"본문: {content}")
        print(f"머슴넷 전송 결과: {res.status_code}")
        print(f"--------------------------")
        
    except Exception as e:
        print(f"전송 중 오류 발생: {e}")

if __name__ == "__main__":
    run_dolsoe()
