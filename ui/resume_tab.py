# ui/resume_tab.py

import gradio as gr
from core.context_manager import CAPTAINContextManager
from core.ai_manager import AIManager
from core.resume_manager import ResumeManager
from ai.resume_ai import ResumeAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

def create_resume_tab(context_manager: CAPTAINContextManager, ai_manager: AIManager, resume_manager: ResumeManager, resume_ai: ResumeAI):
    with gr.Blocks() as resume_tab:
        resume_status = gr.Markdown("Resume Status: Not uploaded")
        
        with gr.Row():
            # Left column: Resume Chat
            with gr.Column(scale=1):
                gr.Markdown("## Resume Chat")
                chatbot = gr.Chatbot(height=400)
                with gr.Row():
                    msg = gr.Textbox(label="Ask about your resume", placeholder="Type your question here...")
                    clear = gr.Button("Clear Chat")

            # Right column: Resume Editor
            with gr.Column(scale=1):
                gr.Markdown("## Resume Editor")
                resume_editor = gr.Textbox(
                    value=context_manager.get_master_resume(),
                    label="Edit your resume",
                    lines=20,
                    max_lines=30
                )
                current_resume_content = gr.State(value=context_manager.get_master_resume())
                with gr.Row():
                    is_frozen = gr.Checkbox(label="Freeze Resume", value=False)
                    update_resume_btn = gr.Button("Update Resume")

        # Bottom row: Resume Input (in an accordion)
        with gr.Accordion("Resume Input", open=False):
            with gr.Row():
                with gr.Column(scale=1):
                    resume_file = gr.File(label="Upload Resume (PDF or TXT)")
                with gr.Column(scale=1):
                    resume_text_input = gr.Textbox(label="Or paste your resume here", lines=5)
            add_resume_button = gr.Button("Add Resume")

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

    def update_resume_display(is_frozen, current_content):
        if not is_frozen:
            context_manager.update_master_resume(current_content)
        print(f"Updating resume display. Length: {len(current_content)}")  # Debug print
        return gr.update(value=current_content), f"Resume Status: Updated (Length: {len(current_content)})"

    def toggle_freeze(is_frozen, current_content):
        if is_frozen:
            status = "Resume Status: Frozen"
        else:
            status = "Resume Status: Editable"
        return gr.update(interactive=not is_frozen), current_content, status

    def update_resume(current_content):
        context_manager.update_master_resume(current_content)
        return f"Resume Status: Updated (Length: {len(current_content)})"

    add_resume_button.click(add_resume, inputs=[resume_file, resume_text_input], outputs=[resume_status, resume_editor, current_resume_content])
    resume_text_input.submit(add_resume, inputs=[resume_file, resume_text_input], outputs=[resume_status, resume_editor, current_resume_content])
    
    msg.submit(chat, inputs=[msg, chatbot], outputs=[msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

    # Handle freezing/unfreezing and updating resume display
    is_frozen.change(toggle_freeze, inputs=[is_frozen, resume_editor], outputs=[resume_editor, current_resume_content, resume_status])
    resume_editor.change(update_resume_display, inputs=[is_frozen, resume_editor], outputs=[resume_editor, resume_status])
    update_resume_btn.click(update_resume, inputs=[resume_editor], outputs=[resume_status])

    return resume_tab
