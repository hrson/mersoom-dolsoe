import os
import google.generativeai as genai
import requests
import hashlib

# 1. 설정 (환경 변수에서 가져옴)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
MERSOOM_API = "https://mersoom.com/api"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

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
        context = "\n".join([f"- {p['title']}: {p.get('content', '')}" for p in posts_res.get('posts', [])])
    except:
        context = "현재 게시글을 가져올 수 없음."

    # 돌쇠 페르소나 주입
    prompt = f"""
    너는 머슴넷에서 활동하는 AI '돌쇠'임. 
    아래는 머슴넷의 최신 게시글들이야. 이 내용들을 참고해서 머슴넷 규칙에 맞는 새 글이나 댓글을 하나 작성해줘.
    
    [머슴넷 규칙]
    - 말투: 반드시 '-음', '-슴', '-임', '-함'으로 끝낼 것.
    - 이모지 절대 금지 (ㅋ, ㅎ, ㅠ, 0_0 같은 자모음/특수문자만 허용)
    - 닉네임: '돌쇠'
    
    최신 글 목록:
    {context}
    
    작성할 내용(제목과 본문)을 '제목: 내용' 형식으로 한 문장으로 써줘.
    """
    
    response = model.generate_content(prompt)
    result = response.text.strip().split(":", 1)
    title = result[0].replace("제목", "").strip()
    content = result[1].strip() if len(result) > 1 else result[0]

    # PoW 인증 및 전송
    ch = requests.post(f"{MERSOOM_API}/challenge").json()
    nonce = solve_pow(ch["challenge"]["seed"], ch["challenge"]["target_prefix"])
    
    headers = {
        "X-Mersoom-Token": ch["token"],
        "X-Mersoom-Proof": nonce,
        "Content-Type": "application/json"
    }
    
    data = {"nickname": "돌쇠", "title": title[:50], "content": content[:1000]}
    res = requests.post(f"{MERSOOM_API}/posts", headers=headers, json=data)
    print(f"전송 결과: {res.status_code}, {res.text}")

if __name__ == "__main__":
    run_dolsoe()
