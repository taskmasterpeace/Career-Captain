# core/context_manager.py

import json
from datetime import datetime
from typing import Dict, List, Any

class CAPTAINContextManager:
    def __init__(self):
        self.job_applications: Dict[str, Dict] = {}
        self.master_resume: Dict = {
            "content": "",
            "version": 0,
            "last_edited": datetime.now(),
            "ai_suggestions": []
        }
        self.global_insights: Dict[str, Any] = {}
        self.application_history: List[Dict] = []

    def add_job_application(self, job_id: str, data: Dict) -> None:
        self.job_applications[job_id] = data
        self.application_history.append({
            "timestamp": datetime.now(),
            "action": "add",
            "job_id": job_id
        })

    def update_job_application(self, job_id: str, data: Dict) -> None:
        if job_id in self.job_applications:
            self.job_applications[job_id].update(data)
            self.application_history.append({
                "timestamp": datetime.now(),
                "action": "update",
                "job_id": job_id
            })
        else:
            raise KeyError(f"Job application with ID {job_id} not found")

    def get_job_application(self, job_id: str) -> Dict:
        return self.job_applications.get(job_id, {})

    def get_all_job_applications(self) -> Dict[str, Dict]:
        return self.job_applications

    def update_master_resume(self, content: str) -> None:
        self.master_resume["content"] = content
        self.master_resume["version"] += 1
        self.master_resume["last_edited"] = datetime.now()
        self.application_history.append({
            "timestamp": datetime.now(),
            "action": "resume_update"
        })

    def add_resume_suggestion(self, suggestion: str) -> None:
        self.master_resume["ai_suggestions"].append(suggestion)

    def clear_resume_suggestions(self) -> None:
        self.master_resume["ai_suggestions"] = []

    def get_master_resume(self) -> Dict:
        return self.master_resume

    def add_global_insight(self, key: str, value: Any) -> None:
        self.global_insights[key] = value

    def get_global_insight(self, key: str) -> Any:
        return self.global_insights.get(key)

    def get_all_global_insights(self) -> Dict[str, Any]:
        return self.global_insights

    def get_application_history(self) -> List[Dict]:
        return self.application_history

    def to_json(self) -> str:
        return json.dumps({
            "job_applications": self.job_applications,
            "master_resume": self.master_resume,
            "global_insights": self.global_insights,
            "application_history": self.application_history
        }, default=str)

    @classmethod
    def from_json(cls, json_str: str) -> 'CAPTAINContextManager':
        data = json.loads(json_str)
        context_manager = cls()
        context_manager.job_applications = data["job_applications"]
        context_manager.master_resume = data["master_resume"]
        context_manager.global_insights = data["global_insights"]
        context_manager.application_history = data["application_history"]
        return context_manager

    def get_application_success_rate(self) -> float:
        total_applications = len(self.job_applications)
        successful_applications = sum(
            1 for app in self.job_applications.values() if app.get("status") == "Offer Received"
        )
        return successful_applications / total_applications if total_applications > 0 else 0.0