import os

# Database - uses DATABASE_URL env var on Render, falls back to local MySQL for dev
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Legacy MySQL config (only used if DATABASE_URL is not set)
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = int(os.environ.get('DB_PORT', 3307))
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'business_directory')
DB_SOCKET = os.environ.get('DB_SOCKET', '/tmp/mysqld/mysql.sock')

# API Keys
OPENROUTER_KEY = os.environ.get('OPENROUTER_KEY', '')
AI_MODEL = os.environ.get('AI_MODEL', 'deepseek/deepseek-chat')

GEMINI_KEYS = os.environ.get('GEMINI_KEYS', '').split(',')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')

SECRET_KEY = os.environ.get('SECRET_KEY', 'business-directory-secret-key-2026')
