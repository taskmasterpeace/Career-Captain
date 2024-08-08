# core/ai_manager.py

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain.memory import ConversationBufferMemory
from typing import List, Dict, Any
import os

class AIManager:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))
        self.system_message = SystemMessage(content="You are an AI assistant for the CAPTAIN job application system.")
        self.memory = ConversationBufferMemory(return_messages=True)

    def create_chain(self, prompt_template: str) -> LLMChain:
        prompt = ChatPromptTemplate.from_messages([
            self.system_message,
            ("human", prompt_template)
        ])
        return LLMChain(llm=self.llm, prompt=prompt, memory=self.memory)

    def generate_response(self, prompt: str, context: Dict[str, Any]) -> str:
        messages = [
            self.system_message,
            HumanMessage(content=prompt.format(**context))
        ]
        response = self.llm(messages).content
        self.memory.save_context({"input": prompt.format(**context)}, {"output": response})
        return response

    def analyze_resume(self, resume_content: str) -> Dict[str, Any]:
        prompt = """Analyze the following resume and provide insights:

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
from typing import Dict, Any
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from config import OPENAI_API_KEY, LLM_TEMPERATURE

class AIManager:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=LLM_TEMPERATURE, api_key=OPENAI_API_KEY, callbacks=[])
        self.memory = ConversationBufferMemory(return_messages=True)

    def create_chain(self, prompt_template: str, input_variables: list) -> LLMChain:
        prompt = PromptTemplate(template=prompt_template, input_variables=input_variables)
        return LLMChain(llm=self.llm, prompt=prompt)

    def create_chat_chain(self, system_template: str, human_template: str) -> LLMChain:
        chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
        return LLMChain(llm=self.llm, prompt=chat_prompt)

    def generate_response(self, prompt: str, context: Dict[str, Any]) -> str:
        messages = [
            SystemMessagePromptTemplate.from_template("You are an AI assistant for the CAPTAIN job application system."),
            HumanMessagePromptTemplate.from_template(prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = LLMChain(llm=self.llm, prompt=chat_prompt)
        return chain.run(**context)

    def chat(self, user_input: str) -> str:
        messages = self.memory.chat_memory.messages + [HumanMessage(content=user_input)]
        response = self.llm.invoke(messages)
        self.memory.chat_memory.add_user_message(user_input)
        self.memory.chat_memory.add_ai_message(response.content)
        return response.content
