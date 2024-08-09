# ui/resume_tab.py

import gradio as gr
from core.context_manager import CAPTAINContextManager
from core.ai_manager import AIManager
from core.resume_manager import ResumeManager
from ai.resume_ai import ResumeAI
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

def create_resume_tab(context_manager: CAPTAINContextManager, ai_manager: AIManager, resume_manager: ResumeManager, resume_ai: ResumeAI):

    with gr.Column():
        gr.Markdown("## Resume Input")
        
        resume_file = gr.File(label="Upload Resume (PDF or TXT)")
        resume_text_input = gr.Textbox(label="Or paste your resume here", lines=10, interactive=True)
        add_resume_button = gr.Button("Add Resume")
        
        gr.Markdown("## Resume Editor")
        
        resume_editor = gr.Markdown(value=context_manager.get_master_resume(), label="Resume Editor")
        current_resume_content = gr.State(value=context_manager.get_master_resume())
        is_frozen = gr.Checkbox(label="Freeze Resume", value=False)
        
        gr.Markdown("## Resume Chat")
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        clear = gr.Button("Clear")

    def process_resume(file_or_text):
        if isinstance(file_or_text, str):
            # Text input
            loader = TextLoader(file_or_text)
        else:
            # File input
            loader = TextLoader(file_or_text.name)
        
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        splits = text_splitter.split_documents(documents)
        
        # Use AI to convert and format the resume
        formatted_resume = ai_manager.generate_response("format_resume", {"resume_content": splits})
        
        resume_ai.update_resume(formatted_resume)
        context_manager.update_master_resume(formatted_resume)
        return "Resume processed successfully.", formatted_resume

    def add_resume(file_or_text):
        return process_resume(file_or_text if file_or_text else resume_text_input.value)

    def chat(message, history):
        current_content = resume_editor.value
        response = resume_ai.chat_about_resume(message, current_content)
        history.append((message, response))
        return "", history

    def toggle_freeze(is_frozen):
        if is_frozen:
            gr.Warning("Resume is now frozen. You cannot make changes.")
        else:
            gr.Warning("Resume is now unfrozen. You can make changes.")
        return is_frozen

    add_resume_button.click(add_resume, inputs=[resume_file], outputs=[gr.Markdown(), resume_editor, current_resume_content])
    resume_text_input.submit(add_resume, inputs=[resume_text_input], outputs=[gr.Markdown(), resume_editor, current_resume_content])
    
    msg.submit(chat, inputs=[msg, chatbot], outputs=[msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

    # Handle freezing/unfreezing
    is_frozen.change(toggle_freeze, inputs=[is_frozen], outputs=[is_frozen])

    # Update the resume content when the editor changes
    resume_editor.change(lambda x: x, inputs=[resume_editor], outputs=[current_resume_content])
