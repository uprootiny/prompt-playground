"""
Prompt template library for testing and comparison
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """Single prompt template"""
    id: str
    name: str
    description: str
    template: str
    variables: List[str]
    system_prompt: str
    category: str
    example_values: Dict[str, str]


# Template library
TEMPLATES = {
    "code_generation": PromptTemplate(
        id="code_generation",
        name="Code Generation",
        description="Generate code in any programming language",
        template="Write a {{language}} function that {{task}}. Include docstrings and type hints.",
        variables=["language", "task"],
        system_prompt="You are an expert programmer who writes clean, efficient, well-documented code.",
        category="coding",
        example_values={"language": "Python", "task": "calculates fibonacci numbers"}
    ),

    "data_extraction": PromptTemplate(
        id="data_extraction",
        name="Data Extraction",
        description="Extract structured data from unstructured text",
        template="Extract {{fields}} from the following text in JSON format:\n\n{{text}}",
        variables=["fields", "text"],
        system_prompt="You are a data extraction specialist. Always respond with valid JSON.",
        category="extraction",
        example_values={
            "fields": "name, email, phone number",
            "text": "Contact John Doe at john@example.com or call 555-1234"
        }
    ),

    "creative_writing": PromptTemplate(
        id="creative_writing",
        name="Creative Writing",
        description="Generate creative content in various styles",
        template="Write a {{length}} {{style}} about {{topic}}.",
        variables=["length", "style", "topic"],
        system_prompt="You are a creative writer with mastery of various literary styles.",
        category="creative",
        example_values={
            "length": "short story",
            "style": "sci-fi thriller",
            "topic": "time travel paradox"
        }
    ),

    "summarization": PromptTemplate(
        id="summarization",
        name="Text Summarization",
        description="Summarize text in specified format",
        template="Summarize the following text in {{format}}, focusing on {{focus}}:\n\n{{text}}",
        variables=["format", "focus", "text"],
        system_prompt="You are an expert at distilling complex information into clear summaries.",
        category="analysis",
        example_values={
            "format": "3 bullet points",
            "focus": "key takeaways",
            "text": "[Insert article or document here]"
        }
    ),

    "translation": PromptTemplate(
        id="translation",
        name="Translation",
        description="Translate text between languages",
        template="Translate the following {{from_lang}} text to {{to_lang}}:\n\n{{text}}",
        variables=["from_lang", "to_lang", "text"],
        system_prompt="You are a professional translator who maintains tone and context.",
        category="language",
        example_values={
            "from_lang": "English",
            "to_lang": "Spanish",
            "text": "Hello, how are you today?"
        }
    ),

    "qa_answering": PromptTemplate(
        id="qa_answering",
        name="Question Answering",
        description="Answer questions with specified detail level",
        template="Answer the following question with {{detail_level}} detail:\n\n{{question}}",
        variables=["detail_level", "question"],
        system_prompt="You are a knowledgeable assistant who provides accurate, well-structured answers.",
        category="qa",
        example_values={
            "detail_level": "comprehensive",
            "question": "How does photosynthesis work?"
        }
    ),

    "code_review": PromptTemplate(
        id="code_review",
        name="Code Review",
        description="Review code for quality and issues",
        template="Review this {{language}} code for {{focus}}:\n\n```{{language}}\n{{code}}\n```",
        variables=["language", "focus", "code"],
        system_prompt="You are a senior code reviewer focused on best practices and code quality.",
        category="coding",
        example_values={
            "language": "python",
            "focus": "bugs, performance, and readability",
            "code": "def fib(n):\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)"
        }
    ),

    "brainstorming": PromptTemplate(
        id="brainstorming",
        name="Brainstorming",
        description="Generate creative ideas",
        template="Generate {{count}} creative ideas for {{topic}}. Focus on {{criteria}}.",
        variables=["count", "topic", "criteria"],
        system_prompt="You are a creative brainstorming partner who thinks outside the box.",
        category="creative",
        example_values={
            "count": "5",
            "topic": "a mobile app for pet owners",
            "criteria": "unique features and monetization"
        }
    ),

    "email_generation": PromptTemplate(
        id="email_generation",
        name="Email Generation",
        description="Write professional emails",
        template="Write a {{tone}} email to {{recipient}} about {{subject}}.",
        variables=["tone", "recipient", "subject"],
        system_prompt="You are a professional communication specialist.",
        category="writing",
        example_values={
            "tone": "formal and friendly",
            "recipient": "a potential client",
            "subject": "proposal for web development project"
        }
    ),

    "explain_concept": PromptTemplate(
        id="explain_concept",
        name="Concept Explanation",
        description="Explain complex concepts simply",
        template="Explain {{concept}} to a {{audience}} using {{approach}}.",
        variables=["concept", "audience", "approach"],
        system_prompt="You are an expert educator who excels at making complex topics accessible.",
        category="education",
        example_values={
            "concept": "quantum entanglement",
            "audience": "high school student",
            "approach": "everyday analogies"
        }
    ),
}


def render_template(template: PromptTemplate, values: Dict[str, str]) -> str:
    """
    Render a template with provided values

    Args:
        template: PromptTemplate to render
        values: Dict mapping variable names to values

    Returns:
        Rendered prompt string
    """
    prompt = template.template

    for var in template.variables:
        placeholder = f"{{{{{var}}}}}"
        value = values.get(var, f"[{var}]")
        prompt = prompt.replace(placeholder, value)

    return prompt


def get_template(template_id: str) -> PromptTemplate:
    """Get template by ID"""
    if template_id not in TEMPLATES:
        raise ValueError(f"Template '{template_id}' not found")
    return TEMPLATES[template_id]


def get_templates_by_category(category: str) -> List[PromptTemplate]:
    """Get all templates in a category"""
    return [t for t in TEMPLATES.values() if t.category == category]


def get_all_categories() -> List[str]:
    """Get all unique categories"""
    return list(set(t.category for t in TEMPLATES.values()))
