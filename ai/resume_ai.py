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
        result = self.ai_manager.generate_response("resume_edit", {"current_resume": current_resume, "edit_request": edit_request})
        
        # Parse the result and update the resume
        updated_section = result.get("1. Updated Resume Section", "")
        if updated_section:
            self.update_resume(updated_section)
        
        return result

    def chat_about_resume(self, user_message: str, resume_content: str = None) -> str:
        if resume_content is None:
            resume_content = self.context_manager.get_master_resume()
        
        print(f"Chat about resume. Resume length: {len(resume_content)}")  # Debug print
        
        if not resume_content.strip():
            return "I'm sorry, but I don't have access to your resume. Could you please make sure you've added your resume to the system?"

        # Check if the message is an edit request
        if user_message.lower().startswith(("edit", "change", "update", "modify")):
            result = self.edit_resume(user_message)
            return f"I've made the following changes:\n\n{result.get('2. Explanation of Changes', 'No changes made.')}"

        # If not an edit request, proceed with normal chat
        response = self.ai_manager.generate_response("resume_chat", {
            "resume_content": resume_content,
            "user_input": user_message
        })
        return response

    def _split_resume(self, resume_content: str, max_chunk_size: int = 1000) -> List[str]:
        # Split the resume into chunks of maximum 1000 characters
        chunks = []
        current_chunk = ""
        for line in resume_content.split('\n'):
            if len(current_chunk) + len(line) > max_chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = line
            else:
                current_chunk += "\n" + line
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def convert_to_markdown(self, content: str) -> str:
        # Split the content into lines
        lines = content.split('\n')
        markdown_lines = []
        
        for line in lines:
            # Remove leading/trailing whitespace
            line = line.strip()
            
            # Convert headers (assume lines in all caps are headers)
            if line.isupper():
                markdown_lines.append(f"## {line}")
            # Convert bullet points
            elif line.startswith('•') or line.startswith('-'):
                markdown_lines.append(line)
            # Convert everything else to regular text
            elif line:
                markdown_lines.append(line)
            # Preserve empty lines
            else:
                markdown_lines.append('')
        
        # Join the lines back together
        return '\n'.join(markdown_lines)

    def edit_resume(self, edit_request: str) -> Dict[str, str]:
        current_resume = self.resume_manager.get_resume()
        prompt = f"""You are editing the user's master resume. The current version is:

{current_resume}

The user or Job Opportunity Navigator has requested the following change:

{edit_request}

Implement this change while maintaining the overall structure and formatting of the resume. Provide your response in the following format:

1. Updated Resume Section:
[Provide the updated section here]

2. Explanation of Changes:
[Explain what was changed and why]

3. Potential Impact:
[Discuss how this change might affect the overall resume and job applications]

4. Additional Suggestions:
[Offer any related improvements or cautions]

5. Next Steps for Further Improvement:"""

        response = self.ai_manager.generate_response("resume_edit", {"current_resume": current_resume, "edit_request": edit_request})
        
        # Parse the response into a structured format
        sections = response.split('\n\n')
        result = {}
        for section in sections:
            key, value = section.split(':', 1)
            result[key.strip()] = value.strip()

        # Update the resume with the new content
        updated_section = result.get("1. Updated Resume Section", "")
        if updated_section:
            self.update_resume(updated_section)

        return result
