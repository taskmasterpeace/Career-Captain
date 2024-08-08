from core.ai_manager import AIManager
from core.context_manager import CAPTAINContextManager
from core.resume_manager import ResumeManager

class ResumeAI:
    def __init__(self, ai_manager: AIManager, context_manager: CAPTAINContextManager, resume_manager: ResumeManager):
        self.ai_manager = ai_manager
        self.context_manager = context_manager
        self.resume_manager = resume_manager

    def analyze_resume(self):
        resume_content = self.resume_manager.get_resume()
        analysis = self.ai_manager.analyze_resume(resume_content)
        return analysis

    def suggest_improvements(self):
        resume_content = self.resume_manager.get_resume()
        suggestions = self.ai_manager.generate_resume_improvements(resume_content)
        return suggestions

    def update_resume(self, new_content):
        self.resume_manager.update_resume(new_content)
        self.context_manager.update_master_resume(new_content)
