import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

class TraceLogger:
    def __init__(self, run_id: str, user_prompt: str = "", input_dataset: str = "", config: Optional[Dict[str, Any]] = None):
        self.run_id = run_id
        self.started_at = datetime.utcnow().isoformat() + "Z"
        self.user_prompt = user_prompt
        self.input_dataset = input_dataset
        self.config = config or {}
        
        self.events: List[Dict[str, Any]] = []
        self.data_quality: Dict[str, Any] = {}
        self.anomalies: List[Dict[str, Any]] = []
        self.driver_results: List[Dict[str, Any]] = []
        self.security_flags: List[Dict[str, Any]] = []
        self.human_review: Dict[str, Any] = {
            "required": False,
            "reasons": []
        }
        self.final_report_path: str = ""
        self.final_status: str = "success"
        self.event_counter = 0

    def add_event(self, event_type: str, name: str, input_summary: Dict[str, Any], output_summary: Dict[str, Any], status: str = "completed", duration_ms: int = 0):
        self.event_counter += 1
        self.events.append({
            "event_id": self.event_counter,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "name": name,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "status": status,
            "duration_ms": duration_ms
        })

    def add_security_flag(self, flag_type: str, severity: str, source: str, description: str, action_taken: str):
        self.security_flags.append({
            "flag_type": flag_type,
            "severity": severity,
            "source": source,
            "description": description,
            "action_taken": action_taken
        })

    def write_trace(self, workspace_root: str) -> str:
        completed_at = datetime.utcnow().isoformat() + "Z"
        
        trace_data = {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "completed_at": completed_at,
            "user_prompt": self.user_prompt,
            "input_dataset": self.input_dataset,
            "config": self.config,
            "events": self.events,
            "data_quality": self.data_quality,
            "anomalies": self.anomalies,
            "driver_results": self.driver_results,
            "security_flags": self.security_flags,
            "human_review": self.human_review,
            "final_report_path": self.final_report_path,
            "final_status": self.final_status
        }
        
        traces_dir = os.path.join(workspace_root, "outputs", "traces")
        os.makedirs(traces_dir, exist_ok=True)
        
        trace_filename = f"run_{self.run_id}.json"
        trace_path = os.path.join(traces_dir, trace_filename)
        
        with open(trace_path, "w") as f:
            json.dump(trace_data, f, indent=2)
            
        return os.path.relpath(trace_path, workspace_root)
