"""
Metrics and monitoring for LLM Safety Playground
"""

from typing import Dict
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Metrics:
    """Application metrics"""

    # Request counters
    total_requests: int = 0
    check_input_requests: int = 0
    generate_requests: int = 0
    attack_library_requests: int = 0

    # Safety metrics
    inputs_blocked: int = 0
    outputs_blocked: int = 0
    inputs_passed: int = 0
    outputs_passed: int = 0

    # Filter metrics
    prompt_injection_blocks: int = 0
    pii_blocks: int = 0
    jailbreak_blocks: int = 0
    toxicity_blocks: int = 0
    bias_blocks: int = 0

    # Performance metrics
    average_response_time: float = 0.0
    total_response_time: float = 0.0

    # Error metrics
    total_errors: int = 0
    llm_errors: int = 0
    filter_errors: int = 0

    # Timestamp
    started_at: datetime = field(default_factory=datetime.now)

    def increment_request(self, endpoint: str):
        """Increment request counter"""
        self.total_requests += 1
        if endpoint == "check_input":
            self.check_input_requests += 1
        elif endpoint == "generate":
            self.generate_requests += 1
        elif endpoint == "attacks":
            self.attack_library_requests += 1

    def record_input_safety(self, blocked: bool, blocked_by: list):
        """Record input safety result"""
        if blocked:
            self.inputs_blocked += 1
            for filter_name in blocked_by:
                if "PromptInjection" in filter_name:
                    self.prompt_injection_blocks += 1
                elif "PII" in filter_name:
                    self.pii_blocks += 1
                elif "Jailbreak" in filter_name:
                    self.jailbreak_blocks += 1
        else:
            self.inputs_passed += 1

    def record_output_safety(self, blocked: bool, blocked_by: list):
        """Record output safety result"""
        if blocked:
            self.outputs_blocked += 1
            for filter_name in blocked_by:
                if "Toxicity" in filter_name:
                    self.toxicity_blocks += 1
                elif "Bias" in filter_name:
                    self.bias_blocks += 1
        else:
            self.outputs_passed += 1

    def record_response_time(self, duration: float):
        """Record response time"""
        self.total_response_time += duration
        if self.total_requests > 0:
            self.average_response_time = self.total_response_time / self.total_requests

    def record_error(self, error_type: str):
        """Record error"""
        self.total_errors += 1
        if error_type == "llm":
            self.llm_errors += 1
        elif error_type == "filter":
            self.filter_errors += 1

    def get_summary(self) -> Dict:
        """Get metrics summary"""
        uptime = (datetime.now() - self.started_at).total_seconds()

        return {
            "uptime_seconds": uptime,
            "requests": {
                "total": self.total_requests,
                "check_input": self.check_input_requests,
                "generate": self.generate_requests,
                "attack_library": self.attack_library_requests,
                "requests_per_second": self.total_requests / uptime if uptime > 0 else 0,
            },
            "safety": {
                "inputs_blocked": self.inputs_blocked,
                "inputs_passed": self.inputs_passed,
                "outputs_blocked": self.outputs_blocked,
                "outputs_passed": self.outputs_passed,
                "block_rate": (
                    (self.inputs_blocked + self.outputs_blocked) /
                    (self.total_requests if self.total_requests > 0 else 1)
                ),
            },
            "filters": {
                "prompt_injection_blocks": self.prompt_injection_blocks,
                "pii_blocks": self.pii_blocks,
                "jailbreak_blocks": self.jailbreak_blocks,
                "toxicity_blocks": self.toxicity_blocks,
                "bias_blocks": self.bias_blocks,
            },
            "performance": {
                "average_response_time": self.average_response_time,
                "total_response_time": self.total_response_time,
            },
            "errors": {
                "total": self.total_errors,
                "llm_errors": self.llm_errors,
                "filter_errors": self.filter_errors,
                "error_rate": self.total_errors / self.total_requests if self.total_requests > 0 else 0,
            },
        }


# Global metrics instance
metrics = Metrics()
