# ai/job_opportunity_ai.py

from core.ai_manager import AIManager
from core.context_manager import CAPTAINContextManager
from typing import Dict, List
import json

class JobOpportunityAI:
    def __init__(self, ai_manager: AIManager, context_manager: CAPTAINContextManager):
        self.ai_manager = ai_manager
        self.context_manager = context_manager

    def analyze_job_description(self, job_id: str) -> Dict[str, List[str]]:
        job = self.context_manager.get_job_application(job_id)
        resume = self.context_manager.get_master_resume()
        analysis = self.ai_manager.analyze_job_description(job['description'], resume['content'])
        return analysis

    def suggest_application_improvements(self, job_id: str) -> List[str]:
        analysis = self.analyze_job_description(job_id)
        suggestions = []
        for category, items in analysis.items():
            if category == "Suggestions for tailoring the resume to this job":
                suggestions.extend(items)
        return suggestions

    def update_application_status(self, job_id: str, new_status: str) -> str:
        job = self.context_manager.get_job_application(job_id)
        old_status = job.get('status', 'Not Started')
        job['status'] = new_status
        self.context_manager.update_job_application(job_id, job)

        prompt = f"""The application status for the {job['position']} position at {job['company']} has been updated from {old_status} to {new_status}.

Please provide:
1. A brief message about this status change
2. Suggested next steps
3. Any potential challenges to prepare for
4. Questions to consider asking in the next stage

Your response:"""

        return self.ai_manager.generate_response(prompt, {})

    def generate_application_strategy(self, job_id: str) -> str:
        job = self.context_manager.get_job_application(job_id)
        resume = self.context_manager.get_master_resume()

        prompt = f"""Generate an application strategy for the following job:

Position: {job['position']}
Company: {job['company']}
Job Description: {job['description']}

Candidate's Resume:
{resume['content']}

Please provide a comprehensive application strategy, including:
1. Key points to emphasize in the application
2. Suggested changes or additions to the resume
3. Cover letter writing tips
4. Preparation for potential interview questions
5. Research to conduct about the company
6. Any additional steps to stand out as a candidate

Your strategy:"""

        return self.ai_manager.generate_response(prompt, {})

    def simulate_interview_questions(self, job_id: str) -> List[Dict[str, str]]:
        job = self.context_manager.get_job_application(job_id)
        resume = self.context_manager.get_master_resume()

        prompt = f"""Generate a set of potential interview questions and suggested answers for the following job:

Position: {job['position']}
Company: {job['company']}
Job Description: {job['description']}

Candidate's Resume:
{resume['content']}

Please provide 5 likely interview questions and suggested answers. Format your response as a JSON list of objects, each with 'question' and 'suggested_answer' keys.

Interview questions and answers:"""

        response = self.ai_manager.generate_response(prompt, {})
        return json.loads(response)

    def analyze_company_culture(self, job_id: str) -> Dict[str, str]:
        job = self.context_manager.get_job_application(job_id)

        prompt = f"""Analyze the company culture for {job['company']} based on the following job description:

{job['description']}

Please provide insights on:
1. Work environment
2. Company values
3. Team dynamics
4. Growth opportunities
5. Work-life balance

Format your response as a JSON object with these categories as keys.

Company culture analysis:"""

        response = self.ai_manager.generate_response(prompt, {})
        return json.loads(response)

    def suggest_networking_strategies(self, job_id: str) -> List[str]:
        job = self.context_manager.get_job_application(job_id)

        prompt = f"""Suggest networking strategies for the following job application:

Position: {job['position']}
Company: {job['company']}

Please provide a list of networking strategies that could help with this job application. Consider both online and offline networking opportunities.

Networking strategies:"""

        response = self.ai_manager.generate_response(prompt, {})
        return response.split('\n')