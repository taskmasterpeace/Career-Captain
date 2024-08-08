# ai/captain_ai.py

from core.ai_manager import AIManager
from core.context_manager import CAPTAINContextManager
from typing import Dict, List
import json

class CaptainAI:
    def __init__(self, ai_manager: AIManager, context_manager: CAPTAINContextManager):
        self.ai_manager = ai_manager
        self.context_manager = context_manager

    def generate_job_search_overview(self) -> str:
        applications = self.context_manager.get_all_job_applications()
        resume = self.context_manager.get_master_resume()
        
        prompt = """Generate a job search overview based on the following information:

Job Applications:
{applications}

Resume:
{resume}

Previous conversation context:
{chat_history}

Please provide:
1. Summary of active applications
2. Overall application success rate
3. Suggestions for improvement
4. Next steps in the job search

Your overview:"""

        context = {
            "applications": applications,
            "resume": resume['content'],
            "chat_history": self.ai_manager.memory.load_memory_variables({})["history"]
        }
        
        return self.ai_manager.generate_response(prompt, context)

    def suggest_weekend_project(self) -> Dict[str, str]:
        applications = self.context_manager.get_all_job_applications()
        resume = self.context_manager.get_master_resume()
        
        response = self.ai_manager.suggest_weekend_project(applications, resume['content'])
        
        # Parse the response into a structured format
        lines = response.split('\n')
        project = {}
        current_section = ""
        for line in lines:
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                current_section = line[3:].strip(':')
                project[current_section] = ""
            elif current_section and line.strip():
                project[current_section] += line.strip() + " "
        
        return project

    def simulate_first_day(self, job_id: str) -> Dict[str, str]:
        job = self.context_manager.get_job_application(job_id)
        
        response = self.ai_manager.simulate_first_day(job['description'], job.get('company_info', ''))
        
        # Parse the response into a structured format
        lines = response.split('\n')
        simulation = {}
        current_section = ""
        for line in lines:
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                current_section = line[3:].strip(':')
                simulation[current_section] = ""
            elif current_section and line.strip():
                simulation[current_section] += line.strip() + " "
        
        return simulation

    def generate_weekly_goals(self) -> List[str]:
        applications = self.context_manager.get_all_job_applications()
        resume = self.context_manager.get_master_resume()
        
        prompt = f"""Based on the current job search status, generate a list of weekly goals:

Job Applications:
{json.dumps(applications, indent=2)}

Resume:
{resume['content']}

Please provide a list of 5 specific, actionable weekly goals to improve the job search process.

Weekly goals:"""

        response = self.ai_manager.generate_response(prompt, {})
        return response.split('\n')

    def provide_motivation(self) -> str:
        applications = self.context_manager.get_all_job_applications()
        success_rate = self.context_manager.get_application_success_rate()
        
        prompt = f"""Provide a motivational message based on the following job search status:

Number of Applications: {len(applications)}
Application Success Rate: {success_rate:.2%}

Please give an encouraging and motivational message to keep the job seeker inspired and focused on their goals.

Motivational message:"""

        return self.ai_manager.generate_response(prompt, {})

    def suggest_skill_improvement(self) -> Dict[str, List[str]]:
        applications = self.context_manager.get_all_job_applications()
        resume = self.context_manager.get_master_resume()
        
        prompt = f"""Based on the current job applications and resume, suggest skills to improve:

Job Applications:
{json.dumps(applications, indent=2)}

Resume:
{resume['content']}

Please provide suggestions for skill improvement in the following categories:
1. Technical Skills
2. Soft Skills
3. Industry Knowledge

For each category, list 3-5 specific skills or areas of knowledge to focus on.

Skill improvement suggestions:"""

        response = self.ai_manager.generate_response(prompt, {})
        
        # Parse the response into a structured format
        lines = response.split('\n')
        suggestions = {}
        current_category = ""
        for line in lines:
            if line.startswith(('1.', '2.', '3.')):
                current_category = line[3:].strip(':')
                suggestions[current_category] = []
            elif current_category and line.strip():
                suggestions[current_category].append(line.strip())
        
        return suggestions

    def generate_long_term_career_plan(self) -> Dict[str, str]:
        resume = self.context_manager.get_master_resume()
        applications = self.context_manager.get_all_job_applications()
        
        prompt = f"""Based on the current resume and job applications, generate a long-term career plan:

Resume:
{resume['content']}

Job Applications:
{json.dumps(applications, indent=2)}

Please provide a 5-year career plan, including:
1. Career goals
2. Skill development roadmap
3. Potential job positions to target
4. Industry trends to watch
5. Networking and personal branding strategies

Long-term career plan:"""

        response = self.ai_manager.generate_response(prompt, {})
        
        # Parse the response into a structured format
        lines = response.split('\n')
        plan = {}
        current_section = ""
        for line in lines:
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                current_section = line[3:].strip(':')
                plan[current_section] = ""
            elif current_section and line.strip():
                plan[current_section] += line.strip() + " "
        
        return plan
        
        prompt = f"""Based on the current job search status, generate a list of weekly goals:

Job Applications:
{json.dumps(applications, indent=2)}

Resume:
{resume['content']}

Please provide a list of 5 specific, actionable weekly goals to improve the job search process.

Weekly goals:"""

        response = self.ai_manager.generate_response(prompt, {})
        return response.split('\n')

    def provide_motivation(self) -> str:
        applications = self.context_manager.get_all_job_applications()
        success_rate = self.context_manager.get_application_success_rate()
        
        prompt = f"""Provide a motivational message based on the following job search status:

Number of Applications: {len(applications)}
Application Success Rate: {success_rate:.2%}

Please give an encouraging and motivational message to keep the job seeker inspired and focused on their goals.

Motivational message:"""

        return self.ai_manager.generate_response(prompt, {})

    def suggest_skill_improvement(self) -> Dict[str, List[str]]:
        applications = self.context_manager.get_all_job_applications()
        resume = self.context_manager.get_master_resume()
        
        prompt = f"""Based on the current job applications and resume, suggest skills to improve:

Job Applications:
{json.dumps(applications, indent=2)}

Resume:
{resume['content']}

Please provide suggestions for skill improvement in the following categories:
1. Technical Skills
2. Soft Skills
3. Industry Knowledge

For each category, list 3-5 specific skills or areas of knowledge to focus on.

Skill improvement suggestions:"""

        response = self.ai_manager.generate_response(prompt, {})
        
        # Parse the response into a structured format
        lines = response.split('\n')
        suggestions = {}
        current_category = ""
        for line in lines:
            if line.startswith(('1.', '2.', '3.')):
                current_category = line[3:].strip(':')
                suggestions[current_category] = []
            elif current_category and line.strip():
                suggestions[current_category].append(line.strip())
        
        return suggestions

    def generate_long_term_career_plan(self) -> Dict[str, str]:
        resume = self.context_manager.get_master_resume()
        applications = self.context_manager.get_all_job_applications()
        
        prompt = f"""Based on the current resume and job applications, generate a long-term career plan:

Resume:
{resume['content']}

Job Applications:
{json.dumps(applications, indent=2)}

Please provide a 5-year career plan, including:
1. Career goals
2. Skill development roadmap
3. Potential job positions to target
4. Industry trends to watch
5. Networking and personal branding strategies

Long-term career plan:"""

        response = self.ai_manager.generate_response(prompt, {})
        
        # Parse the response into a structured format
        lines = response.split('\n')
        plan = {}
        current_section = ""
        for line in lines:
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                current_section = line[3:].strip(':')
                plan[current_section] = ""
            elif current_section and line.strip():
                plan[current_section] += line.strip() + " "
        
        return plan
