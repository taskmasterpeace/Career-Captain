# core/ai_manager.py

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from typing import List, Dict, Any
import os
from config import LLM_MODEL, LLM_TEMPERATURE, OPENAI_API_KEY

class AIManager:
    def __init__(self):
        # self.llm = ChatOpenAI(temperature=0.1, model_name="gpt4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
        self.system_message = SystemMessage(content="You are an AI assistant for the CAPTAIN job application system.")
        self.llm = ChatOpenAI(model_name=LLM_MODEL, temperature=LLM_TEMPERATURE, api_key=OPENAI_API_KEY)
        self.memory = ConversationBufferMemory(return_messages=True)

    def create_chain(self, prompt_template: str):
        prompt = ChatPromptTemplate.from_messages([
            self.system_message,
            ("human", prompt_template)
        ])
        return prompt | self.llm | StrOutputParser()

    def generate_response(self, prompt: str, context: Dict[str, Any]) -> str:
        # If the resume content is too long, summarize it
        if 'resume_content' in context and len(context['resume_content']) > 2000:
            context['resume_content'] = self.summarize_text(context['resume_content'])

        chain = self.create_chain(prompt)
        response = chain.invoke(context)
        self.memory.save_context({"input": prompt.format(**context)}, {"output": response})
        return response

    def summarize_text(self, text: str, max_length: int = 2000) -> str:
        if len(text) <= max_length:
            return text

        summarize_prompt = f"Summarize the following text in no more than {max_length} characters:\n\n{text}"
        summary = self.llm([HumanMessage(content=summarize_prompt)]).content
        return summary[:max_length]

    def analyze_resume(self, resume_content: str) -> Dict[str, Any]:
        prompt = """Analyze the following resume in Markdown format and provide insights:

Resume:
{resume_content}

Please provide:
1. Overall strengths
2. Areas for improvement
3. Suggested additions or modifications
4. Industry-specific advice

Your analysis:"""

        response = self.generate_response(prompt, {"resume_content": resume_content})
        
        # Parse the response into a structured format
        lines = response.split('\n')
        analysis = {}
        current_section = ""
        for line in lines:
            if line.startswith(('1.', '2.', '3.', '4.')):
                current_section = line[3:].strip()
                analysis[current_section] = []
            elif current_section and line.strip():
                analysis[current_section].append(line.strip())

        return analysis

    def analyze_job_description(self, job_description: str, resume: str) -> Dict[str, Any]:
        prompt = """Analyze the following job description and compare it to the given resume:

Job Description:
{job_description}

Resume:
{resume}

Please provide:
1. Key requirements of the job
2. Skills that match between the job and resume
3. Skills or experiences missing from the resume
4. Suggestions for tailoring the resume to this job

Your analysis:"""

        response = self.generate_response(prompt, {
            "job_description": job_description,
            "resume": resume
        })
        
        # Parse the response into a structured format
        lines = response.split('\n')
        analysis = {}
        current_section = ""
        for line in lines:
            if line.startswith(('1.', '2.', '3.', '4.')):
                current_section = line[3:].strip()
                analysis[current_section] = []
            elif current_section and line.strip():
                analysis[current_section].append(line.strip())

        return analysis

    def generate_job_search_overview(self, applications: List[Dict], resume: str) -> str:
        prompt = """Generate a job search overview based on the following information:

Job Applications:
{applications}

Resume:
{resume}

Please provide:
1. Summary of active applications
2. Overall application success rate
3. Suggestions for improvement
4. Next steps in the job search

Your overview:"""

        return self.generate_response(prompt, {
            "applications": json.dumps(applications, indent=2),
            "resume": resume
        })

    def suggest_weekend_project(self, applications: List[Dict], resume: str) -> str:
        prompt = """Suggest a weekend project based on the user's job applications and resume:

Job Applications:
{applications}

Resume:
{resume}

Please provide a weekend project suggestion that will enhance the user's skills and job prospects. Include:
1. Project title
2. Skills developed
3. Relevance to job search
4. Brief project description
5. Expected outcome
6. How to showcase in applications/interviews

Your suggestion:"""

        return self.generate_response(prompt, {
            "applications": json.dumps(applications, indent=2),
            "resume": resume
        })

    def simulate_first_day(self, job_description: str, company_info: str) -> str:
        prompt = """Simulate the first day at a new job based on the following information:

Job Description:
{job_description}

Company Information:
{company_info}

Please provide a simulation of the first day, including:
1. Arrival and onboarding process
2. Key people to meet
3. Main tasks and responsibilities
4. Potential challenges and how to address them
5. Tips for making a great first impression

Your simulation:"""

        return self.generate_response(prompt, {
            "job_description": job_description,
            "company_info": company_info
        })

import json
from typing import Dict, Any, List
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from config import OPENAI_API_KEY, LLM_TEMPERATURE

class AIManager:
    def __init__(self):
        self.llm = ChatOpenAI(model_name=LLM_MODEL, temperature=LLM_TEMPERATURE, api_key=OPENAI_API_KEY)
        self.memory = ConversationBufferMemory(return_messages=True)
        self.prompt_templates = {}
        
        # Add the resume_chat prompt template
        self.create_prompt_template(
            "resume_chat",
            "You are an AI assistant specializing in resume advice. The user's current resume is:\n\n{resume_content}\n\nUser: {user_input}\nAI Assistant:",
            ["resume_content", "user_input"]
        )
        
        # Add the resume_edit prompt template
        self.create_prompt_template(
            "resume_edit",
            """You are editing the user's master resume. The current version is:

{current_resume}

The user has requested the following change:

{edit_request}

Implement this change while maintaining the overall structure and formatting of the resume. Provide your response in the following format:

1. Updated Resume Section:
[Provide the updated section here]

2. Explanation of Changes:
[Explain what was changed and why]

3. Potential Impact:
[Discuss how this change might affect the overall resume and job applications]

4. Additional Suggestions:
[Offer any related improvements or cautions]""",
            ["current_resume", "edit_request"]
        )
        
        # Add the format_resume prompt template
        self.create_prompt_template(
            "format_resume",
            """Format and improve the following resume content:

{resume_content}

Please format the resume using the following guidelines:
1. Use Markdown formatting throughout.
2. Start with the candidate's name as a top-level header (# Name).
# [Candidate Name]
3. Structure the resume with the following sections, using second-level headers:
## Contact Information
## Professional Summary
## Work Experience
## Education
## Skills
4. Under each section header, use the following formatting:
Contact Information:

Use a single line for each piece of contact information.
Include only available information; do not leave blank lines.
Format:
- Email: [email address]
- Phone: [phone number]
- Location: [city, state/province, country]
- LinkedIn: [profile URL] (if available)
Professional Summary:

Write a brief paragraph (3-5 sentences) summarizing key qualifications and career objectives.
Use italics for emphasis on key points:
*[Key skill or qualification]*
Work Experience:

List each job in reverse chronological order.
Use third-level headers (###) for job titles and companies:
Copy### [Job Title] at [Company Name]

Include employment dates on the same line as the job title:
Copy### [Job Title] at [Company Name] (Month Year - Month Year or Present)

Use bullet points (-) for responsibilities and achievements.
Start each bullet point with a strong action verb.
Highlight key achievements or metrics in bold:
Copy- Increased sales by **25%** through implementation of new marketing strategies


Education:

List degrees in reverse chronological order.
Use the following format:
Copy- [Degree Name], [Major] - [University Name], [Graduation Year]

Include any relevant coursework, honors, or GPA if noteworthy:
Copy- Relevant coursework: [Course names]
- Honors: [Honor or award names]
- GPA: [X.XX] (if 3.5 or above)


Skills:

Group skills into categories (e.g., Technical Skills, Soft Skills, Languages).
Use a bullet point list for each category:
Copy- Technical Skills: [Skill 1], [Skill 2], [Skill 3]
- Soft Skills: [Skill 1], [Skill 2], [Skill 3]
- Languages: [Language 1] (Fluent), [Language 2] (Intermediate)
5. Ensure consistent spacing:
Add a blank line before and after each section header.
Add a blank line between each job entry in the Work Experience section.
6. If a section has no content, omit it entirely rather than leaving it empty.
7. Use consistent capitalization for job titles, degree names, and skill categories.
8. Limit the use of special characters and formatting to maintain a clean, professional appearance.

Provide the formatted and improved resume:""",
            ["resume_content"]
        )

    def create_prompt_template(self, name: str, template: str, input_variables: List[str]):
        self.prompt_templates[name] = PromptTemplate(template=template, input_variables=input_variables)

    def create_chain(self, prompt_name: str) -> LLMChain:
        if prompt_name not in self.prompt_templates:
            raise ValueError(f"Prompt template '{prompt_name}' not found")
        return LLMChain(llm=self.llm, prompt=self.prompt_templates[prompt_name])

    def create_chat_chain(self, system_template: str, human_template: str) -> LLMChain:
        chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
        return LLMChain(llm=self.llm, prompt=chat_prompt)

    def generate_response(self, prompt_name: str, context: Dict[str, Any]) -> str:
        print(f"Generating response for prompt: {prompt_name}")
        print(f"Context keys: {context.keys()}")
        if 'resume_content' in context:
            print(f"Resume content length: {len(context['resume_content'])}")
        
        if prompt_name not in self.prompt_templates:
            raise ValueError(f"Prompt template '{prompt_name}' not found")
        
        chain = self.create_chain(prompt_name)
        return chain.run(**context)

    def chat(self, user_input: str) -> str:
        messages = self.memory.chat_memory.messages + [HumanMessage(content=user_input)]
        response = self.llm(messages)
        self.memory.chat_memory.add_user_message(user_input)
        self.memory.chat_memory.add_ai_message(response.content)
        return response.content

    def analyze_resume(self, resume_content: str) -> Dict[str, List[str]]:
        prompt_name = "resume_analysis"
        if prompt_name not in self.prompt_templates:
            self.create_prompt_template(
                prompt_name,
                "Analyze the following resume:\n\n{resume_content}\n\nProvide analysis in the following categories:\n1. Strengths\n2. Areas for Improvement\n3. Suggested Additions\n4. Formatting Recommendations\n5. Industry-Specific Advice",
                ["resume_content"]
            )
        response = self.generate_response(prompt_name, {"resume_content": resume_content})
        return self._parse_list_response(response)

    def analyze_job_description(self, job_description: str, resume: str) -> Dict[str, List[str]]:
        prompt_name = "job_description_analysis"
        if prompt_name not in self.prompt_templates:
            self.create_prompt_template(
                prompt_name,
                "Analyze the following job description and compare it to the resume:\n\nJob Description:\n{job_description}\n\nResume:\n{resume}\n\nProvide analysis in the following categories:\n1. Key Requirements\n2. Matching Skills\n3. Missing Skills\n4. Tailoring Suggestions",
                ["job_description", "resume"]
            )
        response = self.generate_response(prompt_name, {"job_description": job_description, "resume": resume})
        return self._parse_list_response(response)

    def generate_job_search_overview(self, applications: List[Dict], resume: str) -> str:
        prompt_name = "job_search_overview"
        if prompt_name not in self.prompt_templates:
            self.create_prompt_template(
                prompt_name,
                "Generate a job search overview based on the following information:\n\nJob Applications:\n{applications}\n\nResume:\n{resume}\n\nProvide an overview including:\n1. Summary of active applications\n2. Overall application success rate\n3. Suggestions for improvement\n4. Next steps in the job search",
                ["applications", "resume"]
            )
        return self.generate_response(prompt_name, {"applications": json.dumps(applications), "resume": resume})

    def _parse_list_response(self, response: str) -> Dict[str, List[str]]:
        lines = response.strip().split('\n')
        result = {}
        current_category = None
        for line in lines:
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                current_category = line[3:].strip()
                result[current_category] = []
            elif current_category and line.strip():
                result[current_category].append(line.strip())
        return result
