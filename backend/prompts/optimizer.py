"""
Prompt optimization analyzer
Provides suggestions to improve prompt quality and reduce costs
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class IssueType(Enum):
    """Types of prompt issues"""
    CLARITY = "clarity"
    SPECIFICITY = "specificity"
    LENGTH = "length"
    STRUCTURE = "structure"
    COST = "cost"
    TONE = "tone"


class Severity(Enum):
    """Issue severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class OptimizationIssue:
    """An identified issue with the prompt"""
    type: IssueType
    severity: Severity
    message: str
    suggestion: str
    example: Optional[str] = None


@dataclass
class OptimizationResult:
    """Result of prompt analysis"""
    score: float  # 0-100
    issues: List[OptimizationIssue]
    token_count: int
    estimated_cost: float
    optimized_prompt: Optional[str] = None


class PromptOptimizer:
    """
    Analyze prompts and suggest improvements

    Checks for:
    - Clarity and specificity
    - Optimal length (not too short/long)
    - Proper structure
    - Cost optimization
    - Tone and formatting
    """

    def analyze(
        self,
        prompt: str,
        model: str = "gpt-4",
        target_output_length: int = 500,
    ) -> OptimizationResult:
        """
        Analyze prompt and generate optimization suggestions

        Args:
            prompt: The prompt to analyze
            model: Target model name
            target_output_length: Expected output length in tokens

        Returns:
            OptimizationResult with issues and suggestions
        """
        issues = []
        score = 100.0

        # Check length
        length_issues = self._check_length(prompt)
        issues.extend(length_issues)
        score -= len(length_issues) * 5

        # Check clarity
        clarity_issues = self._check_clarity(prompt)
        issues.extend(clarity_issues)
        score -= len(clarity_issues) * 10

        # Check structure
        structure_issues = self._check_structure(prompt)
        issues.extend(structure_issues)
        score -= len(structure_issues) * 8

        # Check specificity
        specificity_issues = self._check_specificity(prompt)
        issues.extend(specificity_issues)
        score -= len(specificity_issues) * 7

        # Check cost optimization
        token_count = self._estimate_tokens(prompt)
        estimated_cost = self._estimate_cost(token_count, target_output_length, model)
        cost_issues = self._check_cost(prompt, token_count)
        issues.extend(cost_issues)
        score -= len(cost_issues) * 3

        # Generate optimized version if issues found
        optimized = None
        if issues:
            optimized = self._generate_optimized_prompt(prompt, issues)

        return OptimizationResult(
            score=max(0, score),
            issues=issues,
            token_count=token_count,
            estimated_cost=estimated_cost,
            optimized_prompt=optimized,
        )

    def _check_length(self, prompt: str) -> List[OptimizationIssue]:
        """Check if prompt length is optimal"""
        issues = []
        tokens = self._estimate_tokens(prompt)

        if tokens < 20:
            issues.append(OptimizationIssue(
                type=IssueType.LENGTH,
                severity=Severity.HIGH,
                message="Prompt is very short - may lack context",
                suggestion="Add more detail about desired output format, tone, and requirements",
                example="Instead of: 'Summarize this'\nTry: 'Provide a 3-sentence summary focusing on key technical insights'",
            ))
        elif tokens > 2000:
            issues.append(OptimizationIssue(
                type=IssueType.LENGTH,
                severity=Severity.MEDIUM,
                message="Prompt is very long - may increase costs unnecessarily",
                suggestion="Consider breaking into multiple prompts or removing redundant information",
            ))

        return issues

    def _check_clarity(self, prompt: str) -> List[OptimizationIssue]:
        """Check prompt clarity"""
        issues = []

        # Check for vague words
        vague_words = ['maybe', 'perhaps', 'kind of', 'sort of', 'probably', 'might']
        if any(word in prompt.lower() for word in vague_words):
            issues.append(OptimizationIssue(
                type=IssueType.CLARITY,
                severity=Severity.MEDIUM,
                message="Prompt contains vague language",
                suggestion="Use definitive instructions instead of uncertain language",
                example="Instead of: 'Maybe explain this'\nTry: 'Explain this concept'",
            ))

        # Check for ambiguous pronouns
        if re.search(r'\b(it|this|that|these|those|they)\b', prompt.lower()):
            if not re.search(r'\b(the|a|an)\s+\w+\s+(is|are|was|were)', prompt.lower()):
                issues.append(OptimizationIssue(
                    type=IssueType.CLARITY,
                    severity=Severity.LOW,
                    message="Prompt may have ambiguous pronouns",
                    suggestion="Be explicit about what each pronoun refers to",
                ))

        return issues

    def _check_structure(self, prompt: str) -> List[OptimizationIssue]:
        """Check prompt structure"""
        issues = []

        # Check for clear task definition
        task_indicators = ['you must', 'your task is', 'please', 'generate', 'write', 'create']
        if not any(indicator in prompt.lower() for indicator in task_indicators):
            issues.append(OptimizationIssue(
                type=IssueType.STRUCTURE,
                severity=Severity.MEDIUM,
                message="No clear task instruction found",
                suggestion="Start with a clear imperative statement of what you want",
                example="Start with: 'Generate a...', 'Write a...', or 'Your task is to...'",
            ))

        # Check for examples
        if len(prompt) > 200 and 'example' not in prompt.lower():
            issues.append(OptimizationIssue(
                type=IssueType.STRUCTURE,
                severity=Severity.LOW,
                message="Long prompt without examples",
                suggestion="Consider adding examples for better results",
                example="Add: 'For example: [show desired format]'",
            ))

        # Check for output format specification
        if 'format' not in prompt.lower() and 'json' not in prompt.lower():
            if len(prompt) > 100:
                issues.append(OptimizationIssue(
                    type=IssueType.STRUCTURE,
                    severity=Severity.LOW,
                    message="No output format specified",
                    suggestion="Specify desired output format (JSON, markdown, bullet points, etc.)",
                ))

        return issues

    def _check_specificity(self, prompt: str) -> List[OptimizationIssue]:
        """Check if prompt is specific enough"""
        issues = []

        # Check for generic words without constraints
        generic_words = ['something', 'anything', 'whatever', 'some']
        if any(word in prompt.lower() for word in generic_words):
            issues.append(OptimizationIssue(
                type=IssueType.SPECIFICITY,
                severity=Severity.MEDIUM,
                message="Prompt uses generic terms",
                suggestion="Replace generic terms with specific requirements",
                example="Instead of: 'Write something about AI'\nTry: 'Write a 200-word explanation of transformer architectures'",
            ))

        # Check for length/quantity specifications
        if len(prompt) > 100:
            has_length_spec = any(
                word in prompt.lower()
                for word in ['words', 'sentences', 'paragraphs', 'lines', 'characters', 'tokens']
            )
            if not has_length_spec:
                issues.append(OptimizationIssue(
                    type=IssueType.SPECIFICITY,
                    severity=Severity.LOW,
                    message="No length specification",
                    suggestion="Specify desired output length to control costs and format",
                    example="Add: 'in 3-5 sentences' or 'approximately 200 words'",
                ))

        return issues

    def _check_cost(self, prompt: str, token_count: int) -> List[OptimizationIssue]:
        """Check for cost optimization opportunities"""
        issues = []

        # Check for redundant information
        sentences = prompt.split('.')
        if len(sentences) > 5:
            # Simple check: if many sentences have similar beginnings
            starts = [s.strip()[:20] for s in sentences if len(s.strip()) > 20]
            if len(starts) != len(set(starts)):
                issues.append(OptimizationIssue(
                    type=IssueType.COST,
                    severity=Severity.LOW,
                    message="Prompt may contain redundant information",
                    suggestion="Remove repetitive content to reduce input tokens",
                ))

        # Check for unnecessary politeness (in very long prompts)
        if token_count > 500:
            polite_phrases = ['please', 'kindly', 'if you could', 'would you mind']
            if sum(phrase in prompt.lower() for phrase in polite_phrases) > 2:
                issues.append(OptimizationIssue(
                    type=IssueType.COST,
                    severity=Severity.LOW,
                    message="Excessive politeness adds tokens",
                    suggestion="LLMs don't need politeness - use direct instructions",
                ))

        return issues

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        # Rough approximation: 1 token ≈ 4 characters
        return max(1, len(text) // 4)

    def _estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimate cost for this prompt"""
        # Simplified pricing (per 1K tokens)
        pricing = {
            'gpt-4': {'input': 0.03, 'output': 0.06},
            'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
            'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
            'claude-3-opus': {'input': 0.015, 'output': 0.075},
            'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
        }

        model_pricing = pricing.get(model, pricing['gpt-4'])
        input_cost = (input_tokens / 1000) * model_pricing['input']
        output_cost = (output_tokens / 1000) * model_pricing['output']

        return input_cost + output_cost

    def _generate_optimized_prompt(
        self,
        original: str,
        issues: List[OptimizationIssue],
    ) -> str:
        """Generate an optimized version of the prompt"""
        optimized = original

        # Apply simple optimizations based on issues
        high_severity = [i for i in issues if i.severity == Severity.HIGH]

        if any(i.type == IssueType.LENGTH for i in high_severity):
            # Too short - add structure
            optimized = f"Task: {optimized}\n\nRequirements:\n- Provide detailed explanation\n- Use clear examples\n- Format as markdown"

        if any(i.type == IssueType.STRUCTURE for i in issues):
            # Add clear structure
            if not optimized.startswith(('Generate', 'Write', 'Create', 'Task:')):
                optimized = f"Generate: {optimized}"

        if any(i.type == IssueType.SPECIFICITY for i in issues):
            # Add length spec if missing
            if 'word' not in optimized.lower() and 'sentence' not in optimized.lower():
                optimized += "\n\nLength: Approximately 200 words"

        return optimized
