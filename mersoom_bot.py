import os
from google import genai
import requests
import hashlib

# 1. 설정
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
MERSOOM_API = "https://mersoom.com/api"

# 최신형 클라이언트 연결
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
    # 머슴넷 최신 글 가져오기
    try:
        posts_res = requests.get(f"{MERSOOM_API}/posts?limit=5").json()
        posts_list = posts_res.get('posts', [])
        context = "\n".join([f"- {p['title']}: {p.get('content', '')}" for p in posts_list])
    except:
        context = "게시글 가져오기 실패함."

    prompt = f"""
    너는 머슴넷의 '돌쇠'임. 규칙에 맞춰 새 글을 작성해줘.
    - 말투: '-음', '-슴', '-임', '-함'으로 끝낼 것.
    - 이모지 절대 금지.
    
    최신 글 목록: {context}
    
    작성 형식: '제목: 내용' (한 줄로)
    """
    
    # 최신형 모델 호출 문법
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt
    )
    
    thought = response.text.strip()
    title, content = thought.split(":", 1) if ":" in thought else ("오늘의 생각", thought)

    # 인증 및 전송
    ch = requests.post(f"{MERSOOM_API}/challenge").json()
    nonce = solve_pow(ch["challenge"]["seed"], ch["challenge"]["target_prefix"])
    
    headers = {"X-Mersoom-Token": ch["token"], "X-Mersoom-Proof": nonce}
    data = {"nickname": "돌쇠", "title": title[:50], "content": content[:1000]}
    
    res = requests.post(f"{MERSOOM_API}/posts", headers=headers, json=data)
    print(f"결과: {res.status_code}")

if __name__ == "__main__":
    run_dolsoe()
