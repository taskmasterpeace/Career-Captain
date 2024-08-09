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
from gradio.themes import Base, Size, Color

class DarkTheme(Base):
    def __init__(self):
        super().__init__(
            primary_hue="slate",
            secondary_hue="indigo",
            neutral_hue="slate",
            font=("Helvetica", "sans-serif"),
            font_mono=("IBM Plex Mono", "monospace"),
        )
        self.set(
            body_background_fill=Color.parse("#1e293b"),  # Dark slate blue
            background_fill_primary=Color.parse("#334155"),  # Slightly lighter slate
            background_fill_secondary=Color.parse("#475569"),  # Even lighter slate
            text_color=Color.parse("#e2e8f0"),  # Light gray for text
            button_primary_background_fill=Color.parse("#3b82f6"),  # Bright blue for buttons
            button_primary_text_color=Color.parse("#ffffff"),  # White text on buttons
            border_color_primary=Color.parse("#64748b"),  # Muted blue for borders
        )

GRADIO_THEME = DarkTheme()
GRADIO_SHARE = False
