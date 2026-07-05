import json
import datetime
from pathlib import Path
from typing import List, Dict, Any

from portfolio_agent.support.config import APPLICATION_NAME

class TraceLogger:
    """
    Collects run information, steps, tool calls, and saves a JSON trace.
    """
    def __init__(self, run_id: str, dataset_path: str):
        self.run_id = run_id
        self.dataset_path = dataset_path
        self.timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        self.events: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        self._next_event_id = 1

    def log_event(
        self,
        name: str,
        details: Dict[str, Any] = None,
        event_type: str = "agent_decision",
        status: str = "completed",
        duration_ms: int = 0,
        correlation_id: str = None,
    ):
        """
        Record a pipeline milestone or tool execution.
        """
        event_id = self._next_event_id
        self._next_event_id += 1
        details = details or {}
        self.events.append({
            "event_id": event_id,
            "event_name": name,
            "event_type": event_type,
            "name": name,
            "invocation_id": self.metadata.get("invocation_id", self.run_id),
            "correlation_id": correlation_id,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "details": details,
            "input_summary": details.get("input_summary", {}),
            "output_summary": details.get("output_summary", details),
            "status": status,
            "duration_ms": duration_ms,
        })

    def log_policy_decision(
        self,
        *,
        hook: str,
        decision: str,
        policy: str,
        reason_code: str,
        details: Dict[str, Any] = None,
    ):
        """
        Record a callback policy decision in the trace event stream.
        """
        self.log_event(
            f"{hook}_{policy}_{decision}",
            {
                "hook": hook,
                "decision": decision,
                "policy": policy,
                "reason_code": reason_code,
                **(details or {}),
            },
            event_type="policy_decision",
        )

    def set_metadata(self, key: str, value: Any):
        """
        Set top-level run metadata.
        """
        self.metadata[key] = value

    def save_trace(self, output_dir: str = "outputs/traces") -> Path:
        """
        Serialize trace data and write to outputs/traces/.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"run_trace_{self.run_id}.json"
        trace_file = out_path / filename

        trace_data = {
            "run_id": self.run_id,
            "session_id": self.metadata.get("session_id", self.run_id),
            "app_name": self.metadata.get("application", APPLICATION_NAME),
            "root_agent": self.metadata.get("root_agent", "portfolio_agent"),
            "timestamp": self.timestamp,
            "started_at": self.timestamp,
            "completed_at": datetime.datetime.utcnow().isoformat() + "Z",
            "dataset_path": self.dataset_path,
            "input_dataset": self.dataset_path,
            "config": {
                "latest_month": self.metadata.get("latest_month"),
                "threshold_profile": self.metadata.get("threshold_profile"),
                "execution_mode": self.metadata.get("execution_mode"),
                "model": self.metadata.get("model"),
            },
            "metadata": self.metadata,
            "security_flags": self.metadata.get("security_flags", []),
            "human_review": {
                "required": self.metadata.get("requires_human_review", False),
                "reasons": self.metadata.get("human_review_reasons", []),
            },
            "final_report_path": self.metadata.get("report_path"),
            "final_status": self.metadata.get("run_status"),
            "events": self.events
        }

        trace_file.write_text(json.dumps(trace_data, indent=2), encoding="utf-8")
        return trace_file
