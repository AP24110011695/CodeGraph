"""Debug chunk_by_ast step by step."""
import sys
print('Setting up...', flush=True)
from app.rag.chunker import Chunker
from app.parsers.ast_models import FileParsingResult
from app.parsers.language_loader import language_loader
from app.parsers.parser_registry import ParserRegistry
import tree_sitter
from pathlib import Path
import tempfile, os

source_code = "def hello_world():\n    pass\n\nclass MyClass:\n    def method1(self):\n        return 1\n"
file_path = Path("test.py")
language = "Python"

print('lang = language_loader.get_language(language)', flush=True)
lang = language_loader.get_language(language)

print('query = ParserRegistry.get_query(language)', flush=True)
query = ParserRegistry.get_query(language)

print('parser = tree_sitter.Parser(lang)', flush=True)
parser = tree_sitter.Parser(lang)

print('source_bytes = source_code.encode("utf-8")', flush=True)
source_bytes = source_code.encode("utf-8")

print('tree = parser.parse(source_bytes)', flush=True)
tree = parser.parse(source_bytes)

print('Done parsing', flush=True)

node_types = ["function_definition", "class_definition", "method_definition", "interface_declaration", "enum_declaration"]
for node_type in node_types:
    print(f'node_type: {node_type}', flush=True)
    cursor = tree_sitter.QueryCursor(query)
    print('  cursor created', flush=True)
    captures = cursor.captures(tree.root_node)
    print(f'  captures: {list(captures.keys())}', flush=True)

print('DONE', flush=True)
