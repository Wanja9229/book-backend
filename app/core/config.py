import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary

load_dotenv()

# .env 파일 찾기 (backend 폴더에 있음)
# 현재 파일 기준으로 상위 폴더 탐색
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class Settings:
    PROJECT_NAME: str = "book API"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # Cloudinary 설정
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")
    
    def __init__(self):
            self._validate_config()
            self._init_cloudinary()
        
    def _validate_config(self):
        """설정 검증"""
        if not self.DATABASE_URL:
            print("⚠️ DATABASE_URL not found")
        else:
            masked = self.DATABASE_URL[:30] + "***"
            print(f"✅ Database: {masked}")
        
    def _init_cloudinary(self):
        """Cloudinary 초기화"""
        if all([self.CLOUDINARY_CLOUD_NAME, 
                self.CLOUDINARY_API_KEY, 
                self.CLOUDINARY_API_SECRET]):
            cloudinary.config(
                cloud_name=self.CLOUDINARY_CLOUD_NAME,
                api_key=self.CLOUDINARY_API_KEY,
                api_secret=self.CLOUDINARY_API_SECRET
            )
            print(f"✅ Cloudinary: {self.CLOUDINARY_CLOUD_NAME}")
        else:
            print("⚠️ Cloudinary not configured")

settings = Settings()