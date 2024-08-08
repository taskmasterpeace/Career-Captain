# ui/job_applications_tab.py

import gradio as gr
from core.context_manager import CAPTAINContextManager
from core.ai_manager import AIManager
from ai.job_opportunity_ai import JobOpportunityAI

def create_job_applications_tab(context_manager: CAPTAINContextManager, ai_manager: AIManager):
    job_ai = JobOpportunityAI(ai_manager, context_manager)

    with gr.Column():
        gr.Markdown("## Job Applications")
        
        with gr.Row():
            with gr.Column():
                company_input = gr.Textbox(label="Company")
                position_input = gr.Textbox(label="Position")
                job_description_input = gr.Textbox(label="Job Description", lines=5)
                add_job_button = gr.Button("Add Job Application")
            
            with gr.Column():
                job_list = gr.Dropdown(choices=[], label="Select a job application")
                status_dropdown = gr.Dropdown(choices=["Not Started", "Applied", "Interview Scheduled", "Offer Received", "Rejected"], label="Application Status")
                update_status_button = gr.Button("Update Status")
        
        # Chatbot for job-specific interactions
        chatbot = gr.Chatbot()
        msg = gr.Textbox(label="Chat with Job AI")
        clear = gr.Button("Clear Chat")

    def chat(message, history):
        # Use ai_manager to generate a response
        response = ai_manager.chat(message)
        history.append((message, response))
        return "", history

    msg.submit(chat, inputs=[msg, chatbot], outputs=[msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)
