# ui/resume_tab.py

import gradio as gr
from core.context_manager import CAPTAINContextManager
from core.ai_manager import AIManager
from core.resume_manager import ResumeManager
from ai.resume_ai import ResumeAI
from prompts import RESUME_ANALYSIS_PROMPT, RESUME_IMPROVEMENT_PROMPT, COVER_LETTER_PROMPT, RESUME_CHAT_PROMPT

def create_resume_tab(context_manager: CAPTAINContextManager, ai_manager: AIManager, resume_manager: ResumeManager, resume_ai: ResumeAI):

    with gr.Column():
        gr.Markdown("## Resume Input")
        
        resume_file = gr.File(label="Upload Resume (PDF or TXT)")
        resume_text_input = gr.Textbox(label="Or paste your resume here", lines=10, interactive=True)
        add_resume_button = gr.Button("Add Resume from File")
        update_from_paste_button = gr.Button("Update Resume from Pasted Text")
        
        gr.Markdown("## Resume Editor")
        
        resume_editor = gr.Markdown(value=context_manager.get_master_resume(), label="Resume Editor")
        current_resume_content = gr.State(value=context_manager.get_master_resume())
        is_frozen = gr.Checkbox(label="Freeze Resume", value=False)
        update_button = gr.Button("Update Resume")
        
        # Add a new button for manual update after pasting
        update_from_paste_button = gr.Button("Update Resume from Pasted Text")
        
        with gr.Row():
            analyze_button = gr.Button("Analyze Resume")
            suggest_button = gr.Button("Suggest Improvements")
        
        analysis_output = gr.Markdown(label="Analysis Output")
        suggestions_output = gr.Markdown(label="Improvement Suggestions")
        
        with gr.Accordion("Resume Versions", open=False):
            versions_dropdown = gr.Dropdown(choices=[], label="Select a version")
            rollback_button = gr.Button("Rollback to Selected Version")
        
        with gr.Accordion("Generate Cover Letter", open=False):
            job_dropdown = gr.Dropdown(choices=[], label="Select a job")
            generate_cover_letter_button = gr.Button("Generate Cover Letter")
            cover_letter_output = gr.Markdown()

        gr.Markdown("## Resume Chat")
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        clear = gr.Button("Clear")

    def add_resume(file):
        if file:
            content = resume_manager.read_resume_file(file.name)
            markdown_content = resume_ai.convert_to_markdown(content)
            resume_ai.update_resume(markdown_content)
            return "Resume added successfully from file.", markdown_content
        else:
            return "Please upload a file to add a resume.", ""

    def update_from_paste(text):
        if text:
            markdown_content = resume_ai.convert_to_markdown(text)
            resume_ai.update_resume(markdown_content)
            context_manager.update_master_resume(markdown_content)
            return "Resume updated successfully from pasted text.", markdown_content, markdown_content
        else:
            return "Please paste your resume text before updating.", "", current_resume_content.value

    def update_resume(content, frozen):
        if not frozen:
            resume_ai.update_resume(content)
            return "Resume updated successfully.", content
        else:
            return "Resume is frozen. Cannot update.", content

    def analyze_resume():
        resume_content = resume_editor.value
        analysis = ai_manager.generate_response(RESUME_ANALYSIS_PROMPT, {"resume_content": resume_content})
        return analysis

    def suggest_improvements():
        resume_content = resume_editor.value
        suggestions = ai_manager.generate_response(RESUME_IMPROVEMENT_PROMPT, {"resume_content": resume_content})
        return suggestions

    def update_versions_dropdown():
        versions = resume_manager.get_resume_versions()
        return gr.Dropdown.update(choices=[f"Version {v['version']} - {v['last_edited']}" for v in versions])

    def rollback_to_version(version):
        version_num = int(version.split()[1])
        resume_content = resume_manager.rollback_to_version(version_num)
        return resume_content

    def generate_cover_letter(job_id):
        resume_content = resume_editor.value
        job_details = context_manager.get_job_application(job_id)
        cover_letter = ai_manager.generate_response(COVER_LETTER_PROMPT, {
            "job_details": job_details,
            "resume_content": resume_content
        })
        return cover_letter

    def update_job_dropdown():
        jobs = context_manager.get_all_job_applications()
        return gr.Dropdown.update(choices=[f"{job['company']} - {job['position']}" for job in jobs.values()])

    def chat(message, history, current_content):
        response = resume_ai.chat_about_resume(message, current_content)
        history.append((message, response))
        return "", history

    def toggle_freeze(is_frozen):
        if is_frozen:
            gr.Warning("Resume is now frozen. You cannot make changes.")
        else:
            gr.Warning("Resume is now unfrozen. You can make changes.")
        return is_frozen

    def get_resume_content():
        return resume_editor.value

    def format_resume(content):
        sections = content.split('\n\n')
        formatted_sections = []
        for section in sections:
            lines = section.split('\n')
            if lines[0].startswith('#'):
                formatted_sections.append(f"\n\n{section}")
            else:
                formatted_sections.append(section)
        return '\n\n'.join(formatted_sections)

    def update_resume_with_formatting(content, frozen):
        if not frozen:
            formatted_content = format_resume(content)
            resume_ai.update_resume(formatted_content)
            return "Resume updated successfully.", formatted_content
        else:
            return "Resume is frozen. Cannot update.", content

    add_resume_button.click(add_resume, inputs=[resume_file], outputs=[gr.Markdown(), resume_editor])
    update_from_paste_button.click(update_from_paste, inputs=[resume_text_input], outputs=[gr.Markdown(), resume_editor, current_resume_content])
    update_button.click(update_resume_with_formatting, inputs=[resume_editor, is_frozen], outputs=[gr.Markdown(), resume_editor, current_resume_content])
    analyze_button.click(analyze_resume, inputs=[], outputs=[analysis_output])
    suggest_button.click(suggest_improvements, inputs=[], outputs=[suggestions_output])
    versions_dropdown.change(None, inputs=[versions_dropdown], outputs=[versions_dropdown])
    rollback_button.click(rollback_to_version, inputs=[versions_dropdown], outputs=[resume_editor, current_resume_content])
    generate_cover_letter_button.click(generate_cover_letter, inputs=[job_dropdown], outputs=[cover_letter_output])
    is_frozen.change(toggle_freeze, inputs=[is_frozen], outputs=[is_frozen])

    msg.submit(chat, inputs=[msg, chatbot, current_resume_content], outputs=[msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

    # Update the resume content for the chatbot
    resume_editor.change(get_resume_content, outputs=[resume_editor])

    # Handle freezing/unfreezing
    is_frozen.change(toggle_freeze, inputs=[is_frozen], outputs=[is_frozen])

    # Update dropdowns when the tab is opened
    # You may need to implement a custom event handler for this functionality
