
RESUME_ANALYSIS_PROMPT = """
Analyze the following resume and provide insights in these categories:
1. Overall Impression
2. Strengths
3. Areas for Improvement
4. Key Skills Highlighted
5. Formatting and Structure

Resume:
{resume_content}

Provide your analysis in a clear, concise manner for each category.
"""

RESUME_IMPROVEMENT_PROMPT = """
Based on the following resume, suggest improvements in these areas:
1. Content Enhancements
2. Skills to Emphasize
3. Achievements to Highlight
4. Formatting Suggestions
5. Industry-Specific Recommendations

Resume:
{resume_content}

Provide specific, actionable suggestions for each area.
"""

COVER_LETTER_PROMPT = """
Generate a cover letter for the following job opportunity using the provided resume:

Job Details:
{job_details}

Resume:
{resume_content}

Create a professional cover letter that highlights the candidate's relevant skills and experiences for this specific job opportunity.
"""

RESUME_CHAT_PROMPT = """
You are an AI assistant specializing in resume and job application advice. You have access to the user's current resume:

{resume_content}

Provide helpful, professional advice based on the user's questions or requests. If you need more information, ask clarifying questions.

User: {user_input}
AI Assistant:
"""
