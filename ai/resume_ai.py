# ui/app.py

import gradio as gr
from core.context_manager import CAPTAINContextManager
from core.ai_manager import AIManager
# Remove the import of create_resume_tab from here
from ui.job_applications_tab import create_job_applications_tab
from ui.captain_tab import create_captain_tab

def create_app():
    context_manager = CAPTAINContextManager()
    ai_manager = AIManager()

    with gr.Blocks(title="CAPTAIN - AI-Powered Job Application Tracker") as app:
        gr.Markdown("# CAPTAIN: Comprehensive AI-Powered Tracking And INtegration")
        
        with gr.Tabs():
            with gr.TabItem("Resume"):
                create_resume_tab(context_manager, ai_manager)
            
            with gr.TabItem("Job Applications"):
                create_job_applications_tab(context_manager, ai_manager)
            
            with gr.TabItem("Captain's Overview"):
                create_captain_tab(context_manager, ai_manager)

        @app.load(outputs=None)
        def on_load():
            # TODO: Implement loading saved state
            pass

        @app.unload(outputs=None)
        def on_unload():
            # TODO: Implement saving state
            pass

    return app

if __name__ == "__main__":
    app = create_app()
    app.launch()
