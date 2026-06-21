import json
import datetime
from pathlib import Path
from typing import List, Dict, Any

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

    def log_event(self, name: str, details: Dict[str, Any] = None):
        """
        Record a pipeline milestone or tool execution.
        """
        self.events.append({
            "event_name": name,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "details": details or {}
        })

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
            "timestamp": self.timestamp,
            "dataset_path": self.dataset_path,
            "metadata": self.metadata,
            "events": self.events
        }

        trace_file.write_text(json.dumps(trace_data, indent=2), encoding="utf-8")
        return trace_file
