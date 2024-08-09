from ui.app import create_app

if __name__ == "__main__":
    app = create_app()
    app.launch()
from ui.app import create_app
import gradio as gr
from config import GRADIO_THEME, GRADIO_SHARE

if __name__ == "__main__":
    app = create_app()
    app.launch(theme=GRADIO_THEME, share=GRADIO_SHARE)
