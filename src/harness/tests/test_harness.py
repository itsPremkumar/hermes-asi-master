"""Tests for code generator and other harness modules."""
import pytest
from harness.code_generator import CodeGenerator, CodeTemplate


class TestCodeTemplate:
    def test_create(self):
        t = CodeTemplate(id="t1", name="test", language="python", content="def {{ name }}():")
        assert t.name == "test"

    def test_render(self):
        t = CodeTemplate(id="t1", name="test", language="python", content="def {{ name }}():")
        result = t.render(name="hello")
        assert result == "def hello():"


class TestCodeGenerator:
    def test_register_template(self):
        gen = CodeGenerator()
        t = gen.register_template("py-func", "python", "def {{ name }}():")
        assert t.id in gen.templates

    def test_generate(self):
        gen = CodeGenerator()
        t = gen.register_template("py-func", "python", "def {{ name }}():")
        result = gen.generate(t.id, name="hello")
        assert result is not None
        assert result.content == "def hello():"

    def test_generate_function_python(self):
        gen = CodeGenerator()
        func = gen.generate_function("add", "python", ["a", "b"], "    return a + b")
        assert "def add(a, b):" in func
        assert "return a + b" in func

    def test_generate_function_typescript(self):
        gen = CodeGenerator()
        func = gen.generate_function("add", "typescript", ["a", "b"], "    return a + b")
        assert "function add(a, b)" in func

    def test_generate_class_python(self):
        gen = CodeGenerator()
        cls = gen.generate_class("MyClass", "python", ["def method(self):"], ["x"])
        assert "class MyClass:" in cls

    def test_generate_class_typescript(self):
        gen = CodeGenerator()
        cls = gen.generate_class("MyClass", "typescript", ["method()"], ["x"])
        assert "class MyClass" in cls

    def test_list_templates(self):
        gen = CodeGenerator()
        gen.register_template("py-func", "python", "def {{ name }}():")
        gen.register_template("ts-func", "typescript", "function {{ name }}():")
        assert len(gen.list_templates()) == 2

    def test_get_template(self):
        gen = CodeGenerator()
        t = gen.register_template("py-func", "python", "def {{ name }}():")
        retrieved = gen.get_template(t.id)
        assert retrieved is not None
        assert retrieved.name == "py-func"
