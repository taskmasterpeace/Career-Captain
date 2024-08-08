# ai/captain_ai.py
from core.ai_manager import AIManager
from core.context_manager import CAPTAINContextManager
from typing import Dict, List, Any
import json

class CaptainAI:
    def __init__(self, ai_manager: AIManager, context_manager: CAPTAINContextManager):
        self.ai_manager = ai_manager
        self.context_manager = context_manager

    def generate_job_search_overview(self) -> str:
        context = self.context_manager.get_context_for_captain()
        
        prompt = """Provide a comprehensive overview of the user's current job search status. Use the following information:

Active Job Applications:
{active_applications}

Recent Resume Changes:
{recent_resume_changes}

Job Market Trends:
{job_market_trends}

Overall Application Success Rate:
{success_rate}

Analyze this information and provide:
1. Summary of active applications and their statuses
2. Insights on application success rate and areas for improvement
3. Suggestions for new job opportunities based on the user's profile
4. Advice on resume improvements or skills to develop
5. Motivational message and next steps for the user's job search
6. Gamification update (e.g., "Job Search Level" or "Application Streaks")

Your response should be strategic, insightful, and actionable, with a focus on motivation and progress."""

        return self.ai_manager.generate_response("job_search_overview", {
            "active_applications": json.dumps(context['all_applications'], indent=2),
            "recent_resume_changes": context['master_resume'],
            "job_market_trends": json.dumps(context['global_insights'].get('job_market_trends', {}), indent=2),
            "success_rate": self.context_manager.get_application_success_rate()
        })

    def suggest_weekend_project(self) -> Dict[str, str]:
        context = self.context_manager.get_context_for_captain()
        
        prompt = """Based on the user's current job applications, resume, and market trends, suggest a weekend project that would enhance their skills and job prospects. Consider the following information:

Active Job Applications:
{active_applications}

Recent Resume Changes:
{recent_resume_changes}

Job Market Trends:
{job_market_trends}

Skill Gaps Identified:
{skill_gaps}

Provide a weekend project suggestion in the following format:
1. Project Title:
2. Skills Developed:
3. Relevance to Job Search:
4. Project Description:
5. Expected Outcomes:
6. How to Showcase in Applications/Interviews:
7. Resources Needed:
8. Estimated Time Commitment:"""

        response = self.ai_manager.generate_response("weekend_project", {
            "active_applications": json.dumps(context['all_applications'], indent=2),
            "recent_resume_changes": context['master_resume'],
            "job_market_trends": json.dumps(context['global_insights'].get('job_market_trends', {}), indent=2),
            "skill_gaps": json.dumps(context['global_insights'].get('skill_gaps', {}), indent=2)
        })

        # Parse the response into a structured format
        lines = response.split('\n')
        project = {}
        current_section = ""
        for line in lines:
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')):
                current_section = line[3:].strip(':')
                project[current_section] = ""
            elif current_section and line.strip():
                project[current_section] += line.strip() + " "
        
        return project

    def simulate_first_day(self, job_id: str) -> Dict[str, str]:
        job = self.context_manager.get_job_application(job_id)
        
        prompt = """Based on the job description and company information for the {job_title} position at {company}, create a simulation of what the user's first day might look like. Include:

1. Arrival and Onboarding Process:
2. Key People to Meet:
3. Main Tasks and Responsibilities:
4. Potential Challenges and How to Address Them:
5. Tips for Making a Great First Impression:
6. What to Prepare Before the First Day:
7. Expected Outcomes from the First Day:
8. How This Experience Aligns with Career Goals:

Use the following job details to inform your simulation:
{job_description_summary}
{company_culture_info}"""

        response = self.ai_manager.generate_response("first_day_simulation", {
            "job_title": job['position'],
            "company": job['company'],
            "job_description_summary": job.get('description_summary', 'No summary available'),
            "company_culture_info": job.get('company_culture', 'No company culture information available')
        })
        
        # Parse the response into a structured format
        lines = response.split('\n')
        simulation = {}
        current_section = ""
        for line in lines:
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')):
                current_section = line[3:].strip(':')
                simulation[current_section] = ""
            elif current_section and line.strip():
                simulation[current_section] += line.strip() + " "
        
        return simulation

    def generate_weekly_goals(self) -> List[str]:
        context = self.context_manager.get_context_for_captain()
        
        prompt = """Based on the current job search status, generate a list of weekly goals:

Job Applications:
{applications}

Resume:
{resume}

Please provide a list of 5 specific, actionable weekly goals to improve the job search process.

Weekly goals:"""

        response = self.ai_manager.generate_response("weekly_goals", {
            "applications": json.dumps(context['all_applications'], indent=2),
            "resume": context['master_resume']
        })
        return response.split('\n')

    def provide_motivation(self) -> str:
        applications = self.context_manager.get_all_job_applications()
        success_rate = self.context_manager.get_application_success_rate()
        
        prompt = """Provide a motivational message based on the following job search status:

Number of Applications: {num_applications}
Application Success Rate: {success_rate:.2%}

Please give an encouraging and motivational message to keep the job seeker inspired and focused on their goals.

Motivational message:"""

        return self.ai_manager.generate_response("motivation", {
            "num_applications": len(applications),
            "success_rate": success_rate
        })

    def suggest_skill_improvement(self) -> Dict[str, List[str]]:
        context = self.context_manager.get_context_for_captain()
        
        prompt = """Based on the current job applications and resume, suggest skills to improve:

Job Applications:
{applications}

Resume:
{resume}

Please provide suggestions for skill improvement in the following categories:
1. Technical Skills
2. Soft Skills
3. Industry Knowledge

For each category, list 3-5 specific skills or areas of knowledge to focus on.

Skill improvement suggestions:"""

        response = self.ai_manager.generate_response("skill_improvement", {
            "applications": json.dumps(context['all_applications'], indent=2),
            "resume": context['master_resume']
        })
        
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
        context = self.context_manager.get_context_for_captain()
        
        prompt = """Based on the current resume and job applications, generate a long-term career plan:

Resume:
{resume}

Job Applications:
{applications}

Please provide a 5-year career plan, including:
1. Career goals
2. Skill development roadmap
3. Potential job positions to target
4. Industry trends to watch
5. Networking and personal branding strategies

Long-term career plan:"""

        response = self.ai_manager.generate_response("long_term_career_plan", {
            "resume": context['master_resume'],
            "applications": json.dumps(context['all_applications'], indent=2)
        })
        
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
