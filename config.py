import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATA_DIR = "data/"
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Disable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# File paths
DATA_DIR = "data"
RESUME_FILE = os.path.join(DATA_DIR, "resume.md")
JOB_APPLICATIONS_FILE = os.path.join(DATA_DIR, "job_applications.json")

# LLM Configuration
LLM_TEMPERATURE = 0.7

# Gradio app configuration
GRADIO_THEME = "default"
GRADIO_SHARE = False
