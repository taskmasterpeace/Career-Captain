from core.ai_manager import AIManager
from core.context_manager import CAPTAINContextManager
from core.resume_manager import ResumeManager
from typing import Dict, List
import re

class ResumeAI:
    def __init__(self, ai_manager: AIManager, context_manager: CAPTAINContextManager, resume_manager: ResumeManager):
        self.ai_manager = ai_manager
        self.context_manager = context_manager
        self.resume_manager = resume_manager

    def analyze_resume(self) -> Dict[str, List[str]]:
        resume_content = self.resume_manager.get_resume()
        analysis = self.ai_manager.analyze_resume(resume_content)
        return analysis

    def suggest_improvements(self) -> List[str]:
        resume_content = self.resume_manager.get_resume()
        prompt = f"""Analyze the following resume and provide improvement suggestions:

{resume_content}

Provide your suggestions in the following format:
1. Overall strengths of the resume
2. Areas for improvement
3. Suggestions for additional information to include
4. Formatting and structure recommendations
5. Industry-specific advice
6. Quantifiable achievements to highlight

Your suggestions:"""
        suggestions = self.ai_manager.generate_response("resume_improvements", {"resume": resume_content})
        return suggestions.split('\n')

    def update_resume(self, new_content: str):
        self.resume_manager.update_resume(new_content)
        self.context_manager.update_master_resume(new_content)

    def edit_resume(self, edit_request: str) -> Dict[str, str]:
        current_resume = self.resume_manager.get_resume()
        prompt = f"""You are editing the user's master resume. The current version is:

{current_resume}

The user has requested the following change:

{edit_request}

Implement this change by providing a complete, updated version of the resume. Make sure to include all sections, even those not affected by the edit. Your response should be the entire updated resume in Markdown format.

After the updated resume, provide a brief explanation of the changes made."""

        result = self.ai_manager.generate_response("resume_edit", {"prompt": prompt})
        
        # Split the response into updated resume and explanation
        parts = result.split("\n\nExplanation of changes:")
        updated_resume = parts[0].strip()
        explanation = parts[1].strip() if len(parts) > 1 else "Changes applied as requested."
        
        # Update the entire resume with the new content
        self.update_resume(updated_resume)

        return {
            "Updated Resume": updated_resume,
            "Explanation of Changes": explanation,
        }
        
        return result

    def edit_resume(self, edit_request: str) -> Dict[str, str]:
        current_resume = self.resume_manager.get_resume()
        prompt = f"""You are editing the user's master resume. The current version is:

{current_resume}

The user has requested the following change:

{edit_request}

Implement this change by providing a complete, updated version of the resume. Make sure to include all sections, even those not affected by the edit. Your response should be the entire updated resume in Markdown format."""

        try:
            response = self.ai_manager.generate_response("resume_edit", {"current_resume": current_resume, "edit_request": edit_request})
            
            # Update the entire resume with the new content
            self.update_resume(response)

            return {"Updated Resume": response, "Message": "Resume has been updated successfully."}
        except Exception as e:
            return {"error": f"An error occurred while editing the resume: {str(e)}"}

    def chat_about_resume(self, user_input: str) -> str:
        current_resume = self.resume_manager.get_resume()
        response = self.ai_manager.generate_response("resume_chat", {"resume_content": current_resume, "user_input": user_input})
        return response
