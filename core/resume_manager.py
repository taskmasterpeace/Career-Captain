class ResumeManager:
    def __init__(self):
        self.resume_content = ""

    def update_resume(self, new_content):
        self.resume_content = new_content

    def get_resume(self):
        return self.resume_content

    # Add other shared methods here
