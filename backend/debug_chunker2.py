"""Debug chunker internals."""
import sys
print('Importing...', flush=True)
from app.parsers.language_loader import language_loader
from app.parsers.parser_registry import ParserRegistry
import tree_sitter
from pathlib import Path

print('Checking lang...', flush=True)
lang = language_loader.get_language('Python')
print(f'Lang: {lang}', flush=True)

print('Getting query...', flush=True)
query = ParserRegistry.get_query('Python')
print(f'Query: {query}', flush=True)

print('Parsing source...', flush=True)
code = "def hello_world():\n    pass\n\nclass MyClass:\n    def method1(self):\n        return 1\n"
parser = tree_sitter.Parser(lang)
print('Parser created', flush=True)

source_bytes = code.encode('utf-8')
print('Parsing...', flush=True)
tree = parser.parse(source_bytes)
print(f'Tree: {tree}', flush=True)

lines = code.split('\n')
node_types = ["function_definition", "class_definition", "method_definition", "interface_declaration", "enum_declaration"]

for node_type in node_types:
    print(f'Processing node_type: {node_type}', flush=True)
    cursor = tree_sitter.QueryCursor(query)
    print(f'  cursor created', flush=True)
    captures = cursor.captures(tree.root_node)
    print(f'  captures keys: {list(captures.keys())}', flush=True)
    if node_type in captures:
        print(f'  Found {len(captures[node_type])} nodes', flush=True)
        for node in captures[node_type]:
            start_line = node.start_point[0]
            end_line = node.end_point[0]
            context_start = max(0, start_line - 2)
            context_end = min(len(lines), end_line + 3)
            chunk_content = '\n'.join(lines[context_start:context_end])
            print(f'  Node: {start_line}-{end_line}', flush=True)
    else:
        print(f'  Not in captures (keys are: {list(captures.keys())})', flush=True)

print('ALL DONE', flush=True)
