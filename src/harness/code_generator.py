"""
t_f0087914 — Code Generation Module

Generates code from specifications, templates, and LLM prompts.
"""

from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CodeTemplate:
    """A code template."""
    id: str
    name: str
    language: str
    content: str
    variables: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def render(self, **kwargs: Any) -> str:
        result = self.content
        for var, val in kwargs.items():
            result = result.replace(f"{{{{ {var} }}}}", str(val))
        return result


@dataclass
class GeneratedCode:
    """Generated code result."""
    id: str
    template_id: str
    content: str
    language: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


class CodeGenerator:
    """Generate code from templates and specifications."""

    def __init__(self) -> None:
        self.templates: dict[str, CodeTemplate] = {}
        self.generated: list[GeneratedCode] = []

    def register_template(
        self,
        name: str,
        language: str,
        content: str,
        variables: list[str] | None = None,
    ) -> CodeTemplate:
        """Register a code template."""
        template = CodeTemplate(
            id=str(uuid.uuid4().hex[:8]),
            name=name,
            language=language,
            content=content,
            variables=variables or [],
        )
        self.templates[template.id] = template
        return template

    def generate(self, template_id: str, **kwargs: Any) -> Optional[GeneratedCode]:
        """Generate code from a template."""
        template = self.templates.get(template_id)
        if not template:
            return None
        content = template.render(**kwargs)
        result = GeneratedCode(
            id=str(uuid.uuid4().hex[:8]),
            template_id=template_id,
            content=content,
            language=template.language,
        )
        self.generated.append(result)
        return result

    def generate_function(
        self,
        name: str,
        language: str,
        params: list[str],
        body: str,
        decorator: str = "",
    ) -> str:
        """Generate a function definition."""
        if language == "python":
            decorator_line = f"@{decorator}\n" if decorator else ""
            params_str = ", ".join(params)
            return f"{decorator_line}def {name}({params_str}):\n{body}"
        elif language == "typescript":
            params_str = ", ".join(params)
            return f"function {name}({params_str}): void {{\n{body}\n}}"
        elif language == "bash":
            params_str = " ".join(params)
            return f"{name}() {{\n{body}\n}}"
        return f"// {name} not supported for {language}"

    def generate_class(
        self,
        name: str,
        language: str,
        methods: list[str],
        properties: list[str] | None = None,
    ) -> str:
        """Generate a class definition."""
        if language == "python":
            props = "\n".join(f"        {p} = None" for p in (properties or []))
            methods_str = "\n".join(f"        {m}" for m in methods)
            return f"class {name}:\n    def __init__(self):\n{props}\n\n{methods_str}"
        elif language == "typescript":
            props = "\n".join(f"    {p}: any;" for p in (properties or []))
            methods_str = "\n".join(f"    {m} {{}}" for m in methods)
            return f"class {name} {{\n{props}\n\n{methods_str}\n}}"
        return f"// {name} class not supported for {language}"

    def list_templates(self) -> list[CodeTemplate]:
        return list(self.templates.values())

    def get_template(self, template_id: str) -> Optional[CodeTemplate]:
        return self.templates.get(template_id)
