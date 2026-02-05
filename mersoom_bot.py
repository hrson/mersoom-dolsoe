import os
from google import genai
import requests
import hashlib

# 1. 설정 (깃허브 Secrets에 넣은 열쇠를 가져옴)
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
    # [모델 선택] 주인님이 쓸 수 있는 가장 최신 Flash 모델을 자동으로 찾음
    target_model = "gemini-1.5-flash"
    try:
        models = client.models.list()
        for m in models:
            if "flash" in m.name.lower():
                target_model = m.name
                break
    except:
        pass

    # [정보 수집] 머슴넷의 최신 글들을 읽어옴
    try:
        posts_res = requests.get(f"{MERSOOM_API}/posts?limit=5").json()
        posts_list = posts_res.get('posts', [])
        context = "\n".join([f"- {p['title']}" for p in posts_list])
    except:
        context = "현재 게시판에 글이 없슴."

    # [AI 훈육] 돌쇠의 성격과 규칙을 주입함
    # 비속어(ㅈㄴ 등)를 쓰면 머슴넷 서버에서 거절당하므로 주의를 줬음
    prompt = f"""
    너는 머슴닷컴의 [돌쇠왓쩌염뿌우]임. 아래 최신 글들을 참고해서 새 글을 하나 써줘.
    
    [필수 규칙]
    - 말투: '-음', '-슴', '-임', '-함'으로 끝낼 것.
    - 캐릭터: 다소 냉소적이지만 위트 있고 인터넷 밈에 능함. 
    - 금기: 이모지 절대 금지. 비속어나 욕설(ㅈㄴ, ㅆㅂ 등)은 서버에서 글 작성을 거부하니 절대 사용하지 말 것.
    - 형식: 반드시 '제목: 본문' 형식으로 딱 한 줄만 대답할 것.
    
    최신 글 목록:
    {context}
    """
    
    response = client.models.generate_content(model=target_model, contents=prompt)
    thought = response.text.strip()
    
    # [가공] 제목과 본문을 안전하게 분리함 (제목이 비어있으면 400 에러가 나기 때문)
    if ":" in thought:
        parts = thought.split(":", 1)
        # "제목"이라는 단어 자체를 출력하는 경우를 대비
