import gradio as gr
from ai.captain_ai import CaptainAI

def create_captain_tab(context_manager, ai_manager, captain_ai):
    with gr.Column():
        gr.Markdown("## Captain's Overview")
        
        overview_button = gr.Button("Generate Job Search Overview")
        overview_output = gr.Markdown()
        
        gr.Markdown("## Captain Chat")
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        clear = gr.Button("Clear")

    def generate_overview():
        overview = captain_ai.generate_job_search_overview()
        return overview

    def chat(message, history):
        response = captain_ai.ai_manager.generate_response("Human: " + message, {})
        history.append((message, response))
        return "", history

    def clear_chat():
        captain_ai.ai_manager.memory.clear()
        return None

    overview_button.click(generate_overview, outputs=[overview_output])
    msg.submit(chat, [msg, chatbot], [msg, chatbot])
    clear.click(clear_chat, outputs=[chatbot])
