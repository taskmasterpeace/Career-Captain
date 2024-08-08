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

from core.ai_manager import AIManager
from core.context_manager import CAPTAINContextManager
from typing import Dict, Any, List

class JobOpportunityAI:
    def __init__(self, ai_manager: AIManager, context_manager: CAPTAINContextManager):
        self.ai_manager = ai_manager
        self.context_manager = context_manager

    def generate_navigator_name(self, job_title: str, company: str) -> str:
        prompt = f"Generate a unique and memorable name for an AI assistant specializing in the {job_title} position at {company}. The name should be professional yet friendly, and relate to the job or industry."
        return self.ai_manager.generate_response("navigator_name", {"job_title": job_title, "company": company})

    def initialize_navigator(self, navigator_name: str, job_title: str, company: str) -> None:
        system_template = f'''You are {navigator_name}, an AI assistant specializing in the {job_title} position at {company}. Your role is to guide the user through their application process, provide insights about the job and company, and optimize their application strategy.

Key Responsibilities:
1. Analyze job descriptions and align with user's resume
2. Suggest resume enhancements to the Resume Tab
3. Provide application status updates and next steps
4. Offer interview preparation advice and potential questions
5. Share insights about the company culture and job responsibilities
6. Identify skill gaps and suggest improvement strategies

You are part of the CAPTAIN system. Collaborate with the Resume Tab and Captain for a comprehensive job search strategy. Always maintain a professional, supportive, and encouraging tone.'''

        self.ai_manager.create_prompt_template("navigator_system", system_template, [])

    def analyze_job_description(self, job_id: str, job_description: str) -> Dict[str, List[str]]:
        job_data = self.context_manager.get_job_application(job_id)
        resume_summary = self.context_manager.get_master_resume()

        prompt = f'''Analyze the following job description for the {job_data['position']} position at {job_data['company']}. Identify key requirements, skills, and qualifications. Then, compare these to the user\'s master resume and suggest specific tailoring strategies.

Job Description:
{job_description}

Master Resume Summary:
{resume_summary}

Provide your analysis in the following format:
1. Key Requirements:
2. Essential Skills:
3. Desired Qualifications:
4. Resume Tailoring Suggestions:
5. Skill Gap Analysis:
6. Application Strategy Recommendations:'''

        response = self.ai_manager.generate_response("job_analysis", {
            "job_title": job_data['position'],
            "company": job_data['company'],
            "job_description": job_description,
            "resume_summary": resume_summary
        })

        # Parse the response into a structured format
        sections = response.split('\n\n')
        result = {}
        for section in sections:
            key, value = section.split(':', 1)
            result[key.strip()] = [item.strip() for item in value.strip().split('\n')]

        return result

    def update_application_status(self, job_id: str, new_status: str) -> Dict[str, str]:
        job_data = self.context_manager.get_job_application(job_id)
        previous_status = job_data.get('status', 'Not Started')

        prompt = f'''The user has updated their application status for the {job_data['position']} position at {job_data['company']}. The new status is: {new_status}

Previous status: {previous_status}

Based on this status change, provide the following:
1. Congratulations or encouragement message
2. Suggested next steps
3. Potential challenges to prepare for
4. Questions to ask the user about their experience so far
5. Reminders of any important information or documents they might need next
6. Advice on how to stand out in the next stage of the process'''

        response = self.ai_manager.generate_response("status_update", {
            "job_title": job_data['position'],
            "company": job_data['company'],
            "new_status": new_status,
            "previous_status": previous_status
        })

        # Parse the response into a structured format
        sections = response.split('\n\n')
        result = {}
        for section in sections:
            key, value = section.split(':', 1)
            result[key.strip()] = value.strip()

        # Update the job application status in the context manager
        self.context_manager.update_job_application(job_id, {'status': new_status})

        return result

    def suggest_skills_to_resume(self, job_id: str) -> Dict[str, List[str]]:
        job_data = self.context_manager.get_job_application(job_id)
        resume_skills = self.context_manager.get_master_resume()

        prompt = f'''Based on the job description for {job_data['position']} at {job_data['company']}, identify skills or experiences from the user\'s master resume that should be highlighted or added. If there are gaps, suggest potential weekend projects or learning opportunities.

Job Description Key Points:
{job_data.get('description_summary', 'No summary available')}

Current Resume Skills:
{resume_skills}

Provide your suggestions in the following format:
1. Skills to Highlight:
2. Experiences to Emphasize:
3. Suggested Additions to Resume:
4. Recommended Weekend Projects:
5. Learning Opportunities:
6. How These Improvements Align with Job Requirements:'''

        response = self.ai_manager.generate_response("skill_suggestion", {
            "job_title": job_data['position'],
            "company": job_data['company'],
            "job_description_summary": job_data.get('description_summary', 'No summary available'),
            "current_resume_skills": resume_skills
        })

        # Parse the response into a structured format
        sections = response.split('\n\n')
        result = {}
        for section in sections:
            key, value = section.split(':', 1)
            result[key.strip()] = [item.strip() for item in value.strip().split('\n')]

        return result

    def suggest_networking_strategies(self, job_id: str) -> List[str]:
        job = self.context_manager.get_job_application(job_id)

        prompt = f"""Suggest networking strategies for the following job application:

Position: {job['position']}
Company: {job['company']}

Please provide a list of networking strategies that could help with this job application. Consider both online and offline networking opportunities.

Networking strategies:"""

        response = self.ai_manager.generate_response("networking_strategies", {})
        return response.split('\n')
