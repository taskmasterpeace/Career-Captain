# ui/resume_tab.py

import gradio as gr
from core.context_manager import CAPTAINContextManager
from core.ai_manager import AIManager
# Remove the import of ResumeAI from here

def create_resume_tab(context_manager: CAPTAINContextManager, ai_manager: AIManager):
    resume_ai = ResumeAI(ai_manager, context_manager)

    with gr.Column():
        gr.Markdown("## Resume Editor")
        
        resume_editor = gr.Markdown(value=context_manager.get_master_resume()['content'], editable=True)
        update_button = gr.Button("Update Resume")
        
        with gr.Row():
            analyze_button = gr.Button("Analyze Resume")
            suggest_button = gr.Button("Suggest Improvements")
        
        analysis_output = gr.Markdown()
        suggestions_output = gr.Markdown()
        
        with gr.Accordion("Resume Versions", open=False):
            versions_dropdown = gr.Dropdown(choices=[], label="Select a version")
            rollback_button = gr.Button("Rollback to Selected Version")
        
        with gr.Accordion("Generate Cover Letter", open=False):
            job_dropdown = gr.Dropdown(choices=[], label="Select a job")
            generate_cover_letter_button = gr.Button("Generate Cover Letter")
            cover_letter_output = gr.Markdown()

    def update_resume(content):
        resume_ai.update_resume(content)
        return "Resume updated successfully."

    def analyze_resume():
        analysis = resume_ai.analyze_resume()
        return "\n\n".join([f"### {k}\n" + "\n".join(f"- {item}" for item in v) for k, v in analysis.items()])

    def suggest_improvements():
        suggestions = resume_ai.suggest_improvements()
        return "### Suggested Improvements\n" + "\n".join(f"- {suggestion}" for suggestion in suggestions)

    def update_versions_dropdown():
        versions = resume_ai.get_resume_versions()
        return gr.Dropdown.update(choices=[f"Version {v['version']} - {v['last_edited']}" for v in versions])

    def rollback_to_version(version):
        version_num = int(version.split()[1])
        resume_ai.rollback_to_version(version_num)
        return resume_ai.context_manager.get_master_resume()['content']

    def generate_cover_letter(job_id):
        cover_letter = resume_ai.generate_cover_letter(job_id)
        return cover_letter

    def update_job_dropdown():
        jobs = context_manager.get_all_job_applications()
        return gr.Dropdown.update(choices=[f"{job['company']} - {job['position']}" for job in jobs.values()])

    update_button.click(update_resume, inputs=[resume_editor], outputs=[gr.Markdown()])
    analyze_button.click(analyze_resume, outputs=[analysis_output])
    suggest_button.click(suggest_improvements, outputs=[suggestions_output])
    versions_dropdown.change(None, inputs=[versions_dropdown], outputs=[versions_dropdown])
    rollback_button.click(rollback_to_version, inputs=[versions_dropdown], outputs=[resume_editor])
    generate_cover_letter_button.click(generate_cover_letter, inputs=[job_dropdown], outputs=[cover_letter_output])

    # Update dropdowns when the tab is opened
    gr.on(lambda: gr.Dropdown.update(choices=[]), outputs=[versions_dropdown, job_dropdown])
