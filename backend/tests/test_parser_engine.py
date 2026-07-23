import pytest
from pathlib import Path

from app.parsers.parser_engine import ParserEngine
from app.parsers.language_loader import language_loader
from app.parsers.parser_registry import ParserRegistry
from app.services.scanner_service import ScanResult, FileInfo


def test_language_loader():
    lang = language_loader.get_language("Python")
    assert lang is not None
    lang_invalid = language_loader.get_language("UnknownLang")
    assert lang_invalid is None


def test_parser_registry():
    query = ParserRegistry.get_query("Python")
    assert query is not None
    query_invalid = ParserRegistry.get_query("UnknownLang")
    assert query_invalid is None


def test_python_parsing(tmp_path):
    source = """
import os
from sys import path

@my_decorator
class MyClass:
    def my_method(self):
        pass

async def my_async_func():
    my_var = 1
"""
    test_file = tmp_path / "test.py"
    test_file.write_text(source)
    
    result = ParserEngine.parse_file(test_file, "test.py", "Python")
    assert result is not None
    assert "MyClass" in result.classes
    assert "my_async_func" in result.functions
    assert "my_var" in result.variables
    assert "@my_decorator" in result.decorators


def test_javascript_parsing(tmp_path):
    source = """
import { something } from 'module';
export const myVar = 1;

class JSClass {
    myMethod() {}
}

const myArrow = async () => {};
function regularFunc() {}
"""
    test_file = tmp_path / "test.js"
    test_file.write_text(source)
    
    result = ParserEngine.parse_file(test_file, "test.js", "JavaScript")
    assert result is not None
    assert "JSClass" in result.classes
    assert "myMethod" in result.methods
    assert "regularFunc" in result.functions
    assert "myArrow" in result.variables
    # "myVar" should also be in variables
    assert "myVar" in result.variables


def test_typescript_parsing(tmp_path):
    source = """
interface MyInterface {
    value: string;
}
enum MyEnum {
    A, B
}
"""
    test_file = tmp_path / "test.ts"
    test_file.write_text(source)
    
    result = ParserEngine.parse_file(test_file, "test.ts", "TypeScript")
    assert result is not None
    assert "MyInterface" in result.interfaces
    assert "MyEnum" in result.enums


def test_tsx_parsing(tmp_path):
    source = """
const MyComponent = () => {
    return <div>Hello</div>;
}
"""
    test_file = tmp_path / "test.tsx"
    test_file.write_text(source)
    
    result = ParserEngine.parse_file(test_file, "test.tsx", "TSX")
    assert result is not None
    assert "MyComponent" in result.variables


def test_malformed_code(tmp_path):
    source = """
def this is not python
class { 
"""
    test_file = tmp_path / "test_malformed.py"
    test_file.write_text(source)
    
    # Tree-sitter still parses best-effort
    result = ParserEngine.parse_file(test_file, "test_malformed.py", "Python")
    assert result is not None


def test_project_parsing(tmp_path):
    (tmp_path / "main.py").write_text("class MainClass:\n    pass")
    (tmp_path / "script.js").write_text("function myJsFunc() {}")
    (tmp_path / "ignore.json").write_text("{}")
    
    scan_result = ScanResult(
        project_name="test_proj",
        root_path=str(tmp_path),
        total_files=3,
        files=[
            FileInfo(name="main.py", path="main.py", extension=".py", language="Python", size=20, folder=""),
            FileInfo(name="script.js", path="script.js", extension=".js", language="JavaScript", size=20, folder=""),
            FileInfo(name="ignore.json", path="ignore.json", extension=".json", language="JSON", size=2, folder="")
        ]
    )
    
    project_result = ParserEngine.parse_project(tmp_path, scan_result)
    assert len(project_result.files) == 2
    assert any(f.language == "Python" for f in project_result.files)
    assert any(f.language == "JavaScript" for f in project_result.files)


def test_unsupported_extensions(tmp_path):
    (tmp_path / "script.min.js").write_text("function myJsFunc() {}")
    scan_result = ScanResult(
        project_name="test_proj",
        root_path=str(tmp_path),
        total_files=1,
        files=[
            FileInfo(name="script.min.js", path="script.min.js", extension=".min.js", language="JavaScript", size=20, folder="")
        ]
    )
    project_result = ParserEngine.parse_project(tmp_path, scan_result)
    assert len(project_result.files) == 0


def test_large_file(tmp_path):
    source = "\n".join(f"class A{i}:\n    pass" for i in range(1000))
    test_file = tmp_path / "large.py"
    test_file.write_text(source)
    
    result = ParserEngine.parse_file(test_file, "large.py", "Python")
    assert result is not None
    assert len(result.classes) == 1000

