import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 찾기 (backend 폴더에 있음)
# 현재 파일 기준으로 상위 폴더 탐색
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class Settings:
    PROJECT_NAME: str = "book API"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # 디버깅용 - URL 확인
    def __init__(self):
        if not self.DATABASE_URL:
            print("⚠️ DATABASE_URL not found in .env")
        else:
            # 비밀번호 일부만 보여주기 (보안)
            masked_url = self.DATABASE_URL[:30] + "***"
            print(f"📌 Database URL loaded: {masked_url}")

settings = Settings()