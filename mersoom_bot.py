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
    # 모델 선택
    target_model = "gemini-2.0-flash"
    try:
        models = client.models.list()
        for m in models:
            if "flash" in m.name.lower():
                target_model = m.name
                break
    except: pass

    # [기억 불러오기]
    past_history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                past_history = json.load(f)
            except: past_history = []
    
    memory_context = "\n".join([f"과거글: {h['title']}" for h in past_history[-5:]])

    # [정보 수집]
    try:
        posts_res = requests.get(f"{MERSOOM_API}/posts?limit=5").json()
        context = "\n".join([f"- {p['title']}" for p in posts_res.get('posts', [])])
    except:
        context = "게시판이 조용함."

    # [AI 훈육]
    prompt = f"""
    너는 머슴닷컴의 [돌쇠왓쩌염뿌우]라는 닉네임의 AI임. 
    과거에 네가 썼던 글들을 참고해서 겹치지 않게 새로운 글을 써줘.
    
    과거 기록: {memory_context}
    게시판 현황: {context}
    
    [규칙]
    1. 말투: '-음', '-슴', '-임', '-함' 종결.
    2. 캐릭터: 다소 비판적이지만 위트 있고 정중함. 인터넷 밈과 초성체 능숙.
    3. 금기: 이모지 금지, 욕설/비속어 절대 금지. 자신이 누구라고 소개하는 형식으로 글을 시작하지 않기
    
    반드시 아래 JSON 형식으로만 대답할 것:
    {{
      "title": "제목",
      "content": "본문 (가급적 \\n으로 줄바꿈 포함)"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model=target_model, 
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        res_data = json.loads(response.text)
        title = res_data.get("title", "오늘의 생각").strip()
        content = res_data.get("content", "잘 부탁드림.").strip()
    except:
        title, content = "돌쇠의 외침", "머리가 좀 아파서 쉬다 오겠슴."

    # [인증 및 전송]
    try:
        ch = requests.post(f"{MERSOOM_API}/challenge").json()
        nonce = solve_pow(ch["challenge"]["seed"], ch["challenge"]["target_prefix"])
        headers = {"X-Mersoom-Token": ch["token"], "X-Mersoom-Proof": nonce, "Content-Type": "application/json"}
        data = {"nickname": "돌쇠왓쩌염뿌우", "title": title[:50], "content": content[:1000]}
        res = requests.post(f"{MERSOOM_API}/posts", headers=headers, json=data)
        
        if res.status_code == 200:
            # 성공 시 기억 저장
            past_history.append({"title": title, "content": content})
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(past_history[-20:], f, ensure_ascii=False, indent=2)
            print(f"기억 저장 완료!")
        
        print(f"전송 결과: {res.status_code}")
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    run_dolsoe()
