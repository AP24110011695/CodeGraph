"""Debug script to trace chunker hang."""
print('1: before chunker import')
from app.rag.chunker import Chunker, Chunk
print('2: after chunker import')
from app.parsers.ast_models import FileParsingResult
print('3: after FileParsingResult import')
from pathlib import Path
import tempfile

print('4: Creating file...')
code = "def hello_world():\n    pass\n\nclass MyClass:\n    def method1(self):\n        return 1\n"
file_path = Path(tempfile.mktemp(suffix='.py'))
file_path.write_text(code, encoding='utf-8')
print('5: File created:', file_path)

print('6: Creating parsing result...')
sample_parsing_result = FileParsingResult(
    path='test.py',
    language='Python',
    functions=['hello_world'],
    classes=['MyClass'],
    methods=['method1', 'method2'],
)
print('7: Parsing result created')

print('8: Creating chunker...')
chunker = Chunker()
print('9: Chunker created')

print('10: Calling chunk_file...')
import sys
sys.stdout.flush()
chunks = chunker.chunk_file(
    file_path=file_path,
    rel_path='test.py',
    language='Python',
    upload_id='test-upload',
    parsing_result=sample_parsing_result,
)
print(f'11: Got {len(chunks)} chunks')
file_path.unlink()
print('Done')
