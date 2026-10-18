import os
from pathlib import Path

from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parent.parent

print(PROJECT_ROOT)

load_dotenv(PROJECT_ROOT / ".env")

print(os.environ.get('SF_COMPANY_ID'))