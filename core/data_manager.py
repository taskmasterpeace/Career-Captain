import json

def save_progress(context_manager, file_path):
    # Save application state to file
    pass

def load_progress(file_path):
    # Load application state from file
    pass
import json
import os
from config import DATA_DIR, RESUME_FILE, JOB_APPLICATIONS_FILE
from core.context_manager import CAPTAINContextManager

class DataManager:
    def __init__(self, context_manager: CAPTAINContextManager):
        self.context_manager = context_manager
        self.ensure_data_directory()

    def ensure_data_directory(self):
        os.makedirs(DATA_DIR, exist_ok=True)

    def save_state(self):
        self.save_resume()
        self.save_job_applications()

    def load_state(self):
        self.load_resume()
        self.load_job_applications()

    def save_resume(self):
        with open(RESUME_FILE, "w") as f:
            f.write(self.context_manager.master_resume)

    def load_resume(self):
        if os.path.exists(RESUME_FILE):
            with open(RESUME_FILE, "r") as f:
                self.context_manager.master_resume = f.read()

    def save_job_applications(self):
        with open(JOB_APPLICATIONS_FILE, "w") as f:
            json.dump(self.context_manager.job_applications, f)

    def load_job_applications(self):
        if os.path.exists(JOB_APPLICATIONS_FILE):
            with open(JOB_APPLICATIONS_FILE, "r") as f:
                self.context_manager.job_applications = json.load(f)

    def periodic_save(self):
        # This method can be called periodically to save the application state
        self.save_state()
