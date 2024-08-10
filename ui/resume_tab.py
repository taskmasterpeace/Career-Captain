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
            with gr.Column(scale=1):
                gr.Markdown("## Resume Chat")
                chatbot = gr.Chatbot(height=400)
                msg = gr.Textbox(label="Ask about your resume or request edits", placeholder="Type your question or edit request here...")
                clear = gr.Button("Clear Chat")

            with gr.Column(scale=1):
                gr.Markdown("## Current Resume")
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

        # Resume Input (in an accordion)
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
            updated_resume, explanation = handle_resume_edit(message, current_content)
            response = f"I've made the following changes:\n\n{explanation}"
            if updated_resume != current_content:
                current_content = updated_resume
                status = f"Resume Status: Updated (Length: {len(current_content)})"
            else:
                status = gr.update()  # No change in status
        else:
            response = resume_ai.chat_about_resume(message)
            status = gr.update()  # No change in status
        history.append((message, response))
        return "", history, current_content, current_content, status

    def toggle_freeze(is_frozen):
        return (
            gr.update(visible=is_frozen),  # resume_display
            gr.update(visible=not is_frozen),  # resume_editor
        )

    def update_resume(content):
        # Extract only the markdown content
        markdown_content = extract_markdown(content)
    
        # Update the resume with only the markdown content
        context_manager.update_master_resume(markdown_content)
        resume_manager.update_resume(markdown_content)
    
        return (
            markdown_content,  # update resume_display
            markdown_content,  # update resume_editor
            f"Resume Status: Updated (Length: {len(markdown_content)})"
        )

    def extract_markdown(content):
        # Split the content by lines
        lines = content.split('\n')
    
        # Filter out lines that start with numbers and periods (e.g., "1. ", "2. ")
        markdown_lines = [line for line in lines if not line.strip().startswith(tuple(f"{i}. " for i in range(1, 10)))]
    
        # Join the filtered lines back into a single string
        return '\n'.join(markdown_lines)

    def handle_resume_edit(edit_request, current_content):
        result = resume_ai.edit_resume(edit_request)
        if isinstance(result, dict):
            updated_resume = result.get('Updated Resume', current_content)
            explanation = result.get('Edit Explanation', 'No changes made.')
            
            # Update the resume content
            context_manager.update_master_resume(updated_resume)
            resume_manager.update_resume(updated_resume)
            
            return updated_resume, explanation
        else:
            return current_content, "Error: Unexpected response format from AI."

    # Event handlers

    add_resume_button.click(add_resume, inputs=[resume_file, resume_text_input], outputs=[resume_status, resume_display, resume_editor])
    resume_text_input.submit(add_resume, inputs=[resume_file, resume_text_input], outputs=[resume_status, resume_display, resume_editor])
    
    msg.submit(chat, inputs=[msg, chatbot, resume_editor], outputs=[msg, chatbot, resume_editor, resume_display, resume_status])
    clear.click(lambda: None, None, chatbot, queue=False)

    is_frozen.change(toggle_freeze, inputs=[is_frozen], outputs=[resume_display, resume_editor])
    update_resume_btn.click(update_resume, inputs=[resume_editor], outputs=[resume_display, resume_editor, resume_status])

    return resume_tab
