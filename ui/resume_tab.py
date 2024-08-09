# ui/resume_tab.py

import gradio as gr
from core.context_manager import CAPTAINContextManager
from core.ai_manager import AIManager
from core.resume_manager import ResumeManager
from ai.resume_ai import ResumeAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

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
        if file_or_text is None:
            return "No resume content provided.", ""

        if isinstance(file_or_text, str):
            # Text input
            content = file_or_text
        elif hasattr(file_or_text, 'name'):  # Check if it's a file object
            # File input
            try:
                content = file_or_text.read().decode('utf-8')
            except AttributeError:
                return "Invalid file format.", ""
        else:
            return "Invalid input type.", ""

        # Use AI to convert and format the resume
        try:
            formatted_resume = ai_manager.generate_response("format_resume", {"resume_content": content})
            resume_ai.update_resume(formatted_resume)
            context_manager.update_master_resume(formatted_resume)
            return "Resume processed successfully.", formatted_resume
        except Exception as e:
            print(f"Error processing resume: {str(e)}")  # For debugging
            return f"Error processing resume: {str(e)}", ""

    def add_resume(file, text):
        if file is not None and file.name != '':
            status, formatted_resume = process_resume(file)
        elif text:
            status, formatted_resume = process_resume(text)
        else:
            status, formatted_resume = "No resume content provided.", ""
        
        if formatted_resume:
            context_manager.update_master_resume(formatted_resume)
            resume_manager.update_resume(formatted_resume)
            resume_ai.update_resume(formatted_resume)
        
        print(f"Resume added. Length: {len(formatted_resume)}")  # Debug print
        return status, formatted_resume, formatted_resume

    def chat(message, history):
        current_content = context_manager.get_master_resume()
        print(f"Chat function. Current resume length: {len(current_content)}")  # Debug print
        response = resume_ai.chat_about_resume(message, current_content)
        history.append((message, response))
        return "", history

    def update_resume_display():
        current_resume = context_manager.get_master_resume()
        print(f"Updating resume display. Length: {len(current_resume)}")  # Debug print
        return current_resume

    # Add this line after creating the resume_editor component
    resume_editor.change(update_resume_display, outputs=[resume_editor])

    def update_chat_context(current_content):
        return current_content

    resume_editor.change(update_chat_context, inputs=[resume_editor], outputs=[current_resume_content])

    def toggle_freeze(is_frozen):
        if is_frozen:
            gr.Warning("Resume is now frozen. You cannot make changes.")
        else:
            gr.Warning("Resume is now unfrozen. You can make changes.")
        return is_frozen

    add_resume_button.click(add_resume, inputs=[resume_file, resume_text_input], outputs=[gr.Markdown(), resume_editor, current_resume_content])
    resume_text_input.submit(add_resume, inputs=[resume_file, resume_text_input], outputs=[gr.Markdown(), resume_editor, current_resume_content])
    
    msg.submit(chat, inputs=[msg, chatbot], outputs=[msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

    # Handle freezing/unfreezing
    is_frozen.change(toggle_freeze, inputs=[is_frozen], outputs=[is_frozen])

    # Update the resume content when the editor changes
    resume_editor.change(lambda x: x, inputs=[resume_editor], outputs=[current_resume_content])
