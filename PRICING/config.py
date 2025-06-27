import os
from pathlib import Path


class Config:
    def __init__(self):
        self.app_root = Path(__file__).parent.parent
        
    @property
    def openai_api_key(self) -> str:
        return os.getenv('OPENAI_API_KEY', '')
    
    @property
    def openai_model(self) -> str:
        return os.getenv('OPENAI_MODEL', 'gpt-4o-2024-08-06')
    
    @property
    def max_retries(self) -> int:
        return int(os.getenv('MAX_RETRIES', '3'))
    
    @property
    def system_prompt_path(self) -> str:
        default_path = '/app/prompts/system_prompt.md'
        return os.getenv('SYSTEM_PROMPT_PATH', default_path)

    @property
    def user_prompt_path(self) -> str:
        default_path = '/app/prompts/user_prompt.md'
        return os.getenv('USER_PROMPT_PATH', default_path)
    
    @property
    def default_output_dir(self) -> str:
        default_path = self.app_root / 'outputs'
        return os.getenv('OUTPUT_DIR', str(default_path))
    
    @property
    def db_host(self) -> str:
        return os.getenv('DB_HOST', 'host.docker.internal')
    
    @property
    def db_port(self) -> int:
        return int(os.getenv('DB_PORT', '5433'))
    
    @property
    def db_name(self) -> str:
        return os.getenv('DB_NAME', 'insors_db')
    
    @property
    def db_user(self) -> str:
        return os.getenv('DB_USER', 'insors_demo')
    
    @property
    def db_password(self) -> str:
        return os.getenv('DB_PASSWORD', 'p@ssW0rd!')


config = Config()