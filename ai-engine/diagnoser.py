"""
🦞 AI Diagnosis Engine
Analyzes K8s pod failures and provides human-readable explanations.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PodStatus:
    name: str
    namespace: str
    phase: str
    conditions: List[Dict]
    container_statuses: List[Dict]
    events: List[str]
    logs: Optional[str] = None


@dataclass
class DiagnosisReport:
    root_cause: str
    explanation: str
    suggested_fix: str
    severity: str  # "critical", "warning", "info"
    confidence: float


# Common K8s error patterns and their diagnoses
ERROR_PATTERNS = {
    "CrashLoopBackOff": {
        "patterns": ["exit code 1", "OOMKilled", "Error", "Killed"],
        "common_causes": [
            "Application crashes on startup",
            "Missing environment variables or ConfigMaps",
            "Insufficient memory (OOMKilled)",
            "Permission denied errors",
        ]
    },
    "ImagePullBackOff": {
        "patterns": ["ErrImagePull", "ImagePullBackOff", "unauthorized"],
        "common_causes": [
            "Image doesn't exist or wrong tag",
            "Private registry without credentials",
            "Network issues reaching registry",
        ]
    },
    "Pending": {
        "patterns": ["Insufficient cpu", "Insufficient memory", "node(s) didn't match"],
        "common_causes": [
            "No nodes with sufficient resources",
            "Node selector/affinity not satisfied",
            "PersistentVolumeClaim not bound",
        ]
    },
    "CreateContainerConfigError": {
        "patterns": ["configmap", "secret", "not found"],
        "common_causes": [
            "Referenced ConfigMap doesn't exist",
            "Referenced Secret doesn't exist",
            "Volume mount path invalid",
        ]
    }
}


DIAGNOSIS_PROMPT_TEMPLATE = """
You are a Kubernetes expert. Analyze the following pod failure and provide a diagnosis.

## Pod Information
- Name: {pod_name}
- Namespace: {namespace}
- Status: {status}

## Events
{events}

## Container Logs (last 50 lines)
{logs}

## Task
1. Identify the root cause of the failure
2. Explain what went wrong in simple terms
3. Provide a specific kubectl command or YAML fix

Respond in JSON format:
{{
    "root_cause": "Brief description of the root cause",
    "explanation": "Detailed explanation for a developer",
    "suggested_fix": "kubectl command or YAML snippet to fix the issue",
    "severity": "critical|warning|info",
    "confidence": 0.0-1.0
}}
"""


class AIDiagnoser:
    """AI-powered Kubernetes diagnostics engine."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.use_local_fallback = not self.api_key
    
    def analyze_pod(self, pod_status: PodStatus) -> DiagnosisReport:
        """
        Analyze a pod's status and return a diagnosis.
        Falls back to pattern matching if no API key is available.
        """
        if self.use_local_fallback:
            return self._pattern_based_diagnosis(pod_status)
        else:
            return self._ai_diagnosis(pod_status)
    
    def _pattern_based_diagnosis(self, pod: PodStatus) -> DiagnosisReport:
        """
        Use pattern matching for diagnosis when AI is not available.
        """
        # Combine all text for pattern matching
        all_text = " ".join([
            pod.phase,
            " ".join(pod.events),
            pod.logs or ""
        ]).lower()
        
        # Check for known error patterns
        for error_type, info in ERROR_PATTERNS.items():
            for pattern in info["patterns"]:
                if pattern.lower() in all_text:
                    return DiagnosisReport(
                        root_cause=f"{error_type}: {info['common_causes'][0]}",
                        explanation=f"The pod is experiencing {error_type}. Common causes include: {', '.join(info['common_causes'])}",
                        suggested_fix=self._get_fix_suggestion(error_type, pod),
                        severity="critical" if error_type in ["CrashLoopBackOff", "CreateContainerConfigError"] else "warning",
                        confidence=0.7
                    )
        
        # Generic fallback
        return DiagnosisReport(
            root_cause="Unknown issue",
            explanation="The pod status is abnormal but the specific cause couldn't be determined automatically.",
            suggested_fix=f"kubectl describe pod {pod.name} -n {pod.namespace}",
            severity="warning",
            confidence=0.3
        )
    
    def _get_fix_suggestion(self, error_type: str, pod: PodStatus) -> str:
        """Generate fix suggestion based on error type."""
        fixes = {
            "CrashLoopBackOff": f"kubectl logs {pod.name} -n {pod.namespace} --previous",
            "ImagePullBackOff": f"kubectl describe pod {pod.name} -n {pod.namespace} | grep -A5 Events",
            "Pending": f"kubectl describe pod {pod.name} -n {pod.namespace} | grep -A10 Events",
            "CreateContainerConfigError": f"kubectl get configmaps,secrets -n {pod.namespace}",
        }
        return fixes.get(error_type, f"kubectl describe pod {pod.name} -n {pod.namespace}")
    
    def _ai_diagnosis(self, pod: PodStatus) -> DiagnosisReport:
        """
        Use LLM for advanced diagnosis.
        TODO: Implement OpenAI/Gemini API call
        """
        # Placeholder - will be implemented with actual API
        prompt = DIAGNOSIS_PROMPT_TEMPLATE.format(
            pod_name=pod.name,
            namespace=pod.namespace,
            status=pod.phase,
            events="\n".join(pod.events),
            logs=pod.logs or "No logs available"
        )
        
        # TODO: Call LLM API here
        # response = openai.chat.completions.create(...)
        
        # For now, fall back to pattern matching
        return self._pattern_based_diagnosis(pod)


# Export for use
diagnoser = AIDiagnoser()
