"""Debug chunker.chunk_file specifically."""
import sys
print('Setting up...', flush=True)
from app.rag.chunker import Chunker, Chunk
from app.parsers.ast_models import FileParsingResult
from pathlib import Path
import tempfile, os

code = "def hello_world():\n    pass\n\nclass MyClass:\n    def method1(self):\n        return 1\n"
with open(tempfile.mktemp(suffix='.py'), 'w', encoding='utf-8') as f:
    f.write(code)
    fpath = f.name

file_path = Path(fpath)
print(f'File: {file_path}', flush=True)

parsing_result = FileParsingResult(
    path='test.py',
    language='Python',
    functions=['hello_world'],
    classes=['MyClass'],
    methods=['method1', 'method2'],
)
chunker = Chunker()

# Step through manually
print('Reading file...', flush=True)
with open(file_path, 'r', encoding='utf-8') as f:
    source_code = f.read()
print(f'Read {len(source_code)} chars', flush=True)

print('Checking supports_ast_chunking...', flush=True)
supports = chunker._supports_ast_chunking('Python')
print(f'Supports: {supports}', flush=True)

print('Calling _chunk_by_ast...', flush=True)
chunks = chunker._chunk_by_ast(source_code, file_path, 'test.py', 'Python', 'test-upload', parsing_result)
print(f'AST chunks: {len(chunks)}', flush=True)

if not chunks:
    print('Fallback to _chunk_by_size...', flush=True)
    chunks = chunker._chunk_by_size(source_code, file_path, 'test.py', 'Python', 'test-upload')
    print(f'Size chunks: {len(chunks)}', flush=True)

os.unlink(fpath)
print('DONE', flush=True)
