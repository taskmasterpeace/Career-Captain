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

            # Right column: Resume Display and Editor
            with gr.Column(scale=1):
                gr.Markdown("## Resume")
                resume_display = gr.Markdown(value=context_manager.get_master_resume())
                resume_editor = gr.TextArea(
                    value=context_manager.get_master_resume(),
                    label="Edit Your Resume (Markdown)",
                    lines=20,
                    max_lines=30,
                    visible=False
                )
                with gr.Row():
                    is_frozen = gr.Checkbox(label="Freeze Resume", value=True)
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
        try:
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
        except Exception as e:
            error_message = f"Error processing resume: {str(e)}"
            return error_message, "", ""

    def chat(message, history, current_content):
        if message.lower().startswith(("edit", "change", "update", "modify")):
            result = resume_ai.edit_resume(message)
            if isinstance(result, dict) and "error" in result:
                response = result["error"]
            else:
                response = f"I've made the following changes:\n\n{result.get('Explanation of Changes', 'No changes made.')}"
            updated_resume = resume_ai.resume_manager.get_resume()
            if updated_resume != current_content:
                current_content = updated_resume
                status = f"Resume Status: Updated (Length: {len(current_content)})"
            else:
                status = gr.update()  # No change in status
        else:
            response = "I'm sorry, I can only process edit requests. Please start your message with 'edit', 'change', 'update', or 'modify'."
            status = gr.update()  # No change in status
        history.append((message, response))
        return "", history, current_content, status

    def toggle_freeze(is_frozen):
        return (
            gr.update(visible=is_frozen),  # resume_display
            gr.update(visible=not is_frozen),  # resume_editor
        )

    def update_resume(content):
        context_manager.update_master_resume(content)
        resume_manager.update_resume(content)
        return (
            content,  # update resume_display
            content,  # update resume_editor
            f"Resume Status: Updated (Length: {len(content)})"
        )

    def chat(message, history, current_content):
        try:
            if message.lower().startswith(("edit", "change", "update", "modify")):
                result = resume_ai.edit_resume(message)
                if isinstance(result, dict) and "error" in result:
                    response = result["error"]
                else:
                    response = f"I've made the following changes:\n\n{result.get('Message', 'No changes made.')}"
                    updated_resume = result.get('Updated Resume', current_content)
                    if updated_resume != current_content:
                        current_content = updated_resume
                        context_manager.update_master_resume(current_content)
            else:
                response = resume_ai.chat_about_resume(message)
        
            history.append((message, response))
            return "", history, current_content, current_content, f"Resume Status: Updated (Length: {len(current_content)})"
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            history.append((message, error_message))
            return "", history, current_content, current_content, f"Resume Status: Error occurred"

    add_resume_button.click(add_resume, inputs=[resume_file, resume_text_input], outputs=[resume_status, resume_display, resume_editor])
    resume_text_input.submit(add_resume, inputs=[resume_file, resume_text_input], outputs=[resume_status, resume_display, resume_editor])
    
    msg.submit(chat, inputs=[msg, chatbot, resume_editor], outputs=[msg, chatbot, resume_editor, resume_status])
    clear.click(lambda: None, None, chatbot, queue=False)

    is_frozen.change(toggle_freeze, inputs=[is_frozen], outputs=[resume_display, resume_editor])
    update_resume_btn.click(update_resume, inputs=[resume_editor], outputs=[resume_display, resume_editor, resume_status])

    return resume_tab
