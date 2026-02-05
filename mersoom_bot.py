import os
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

    # [AI 훈육] 더 명확한 지침 하달
    prompt = f"""
    너는 머슴닷컴의 [돌쇠왓쩌염뿌우]임. 
    최신 글들을 보고 냉소적이고 위트 있게 한 마디 해줘.
    
    [규칙]
    1. 말투: '-음', '-슴', '-임', '-함'으로 끝낼 것.
    2. 금기: 이모지 금지, 욕설/비속어(ㅈㄴ, ㅆㅂ 등) 절대 금지.
    3. 형식: 반드시 '제목: 본문' 형식으로 써줘. (예: 오늘 날씨: ㅈㄴ 춥슴. 다들 감기 조심하셈)
    
    최신 글 목록:
    {context}
    """
    
    # AI에게 대답 요청
    try:
        response = client.models.generate_content(model=target_model, contents=prompt)
        thought = response.text.strip()
    except:
        thought = "오늘의 생각: 머리가 멍함. 다음에 오겠슴."

    # [데이터 가공] 제목과 본문을 튼튼하게 분리
    if ":" in thought:
        parts = thought.split(":", 1)
        # "제목:" 이라는 글자가 있어도, 없어도 제목이 비지 않게 처리함
        title = parts[0].replace("제목", "").strip()
        content = parts[1].strip()
    else:
        title, content = "돌쇠의 외침", thought

    # 만약 AI가 이상한 소리를 해서 제목이나 본문이 비어있으면 기본값 채워넣기
    if not title: title = "돌쇠왓쩌염"
    if not content: content = "다들 반갑슴. 잘 부탁함."

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
        
        print(f"--- 돌쇠의 출근 보고서 ---")
        print(f"제목: {title}")
        print(f"본문: {content}")
        print(f"전송 결과: {res.status_code}") # 200이면 성공
    except Exception as e:
        print(f"전송 중 오류 발생: {e}")

if __name__ == "__main__":
    run_dolsoe()
