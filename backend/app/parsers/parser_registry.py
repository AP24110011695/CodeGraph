"""Registry for Tree-sitter queries by language."""

import logging
import tree_sitter

from app.parsers.language_loader import language_loader

logger = logging.getLogger(__name__)

PYTHON_QUERIES = """
(function_definition name: (identifier) @functions)
(class_definition name: (identifier) @classes)
(import_statement name: (dotted_name) @imports)
(import_from_statement module_name: (dotted_name) @imports)
(assignment left: (identifier) @variables)
(decorator) @decorators
"""

JS_QUERIES = """
(function_declaration name: (identifier) @functions)
(class_declaration name: (identifier) @classes)
(method_definition name: (property_identifier) @methods)
(import_statement source: (string) @imports)
(export_statement) @exports
(variable_declarator name: (identifier) @variables)
(arrow_function) @arrow_functions
"""

TS_QUERIES = """
(function_declaration name: (identifier) @functions)
(class_declaration name: (type_identifier) @classes)
(method_definition name: (property_identifier) @methods)
(import_statement source: (string) @imports)
(export_statement) @exports
(variable_declarator name: (identifier) @variables)
(arrow_function) @arrow_functions
(interface_declaration name: (type_identifier) @interfaces)
(enum_declaration name: (identifier) @enums)
"""


LANGUAGE_QUERIES = {
    "Python": PYTHON_QUERIES,
    "JavaScript": JS_QUERIES,
    "TypeScript": TS_QUERIES,
    "TSX": TS_QUERIES,
    "JSX": JS_QUERIES,
}

class ParserRegistry:
    """Provides query access based on language."""
    
    _queries_cache: dict[str, tree_sitter.Query] = {}

    @classmethod
    def get_query(cls, language_name: str) -> tree_sitter.Query | None:
        """Get the parsed tree-sitter Query object for a language."""
        if language_name in cls._queries_cache:
            return cls._queries_cache[language_name]
            
        query_string = LANGUAGE_QUERIES.get(language_name)
        if not query_string:
            return None
            
        lang = language_loader.get_language(language_name)
        if not lang:
            return None
            
        try:
            query = tree_sitter.Query(lang, query_string)
            cls._queries_cache[language_name] = query
            return query
        except Exception as e:
            logger.warning(f"Error compiling tree-sitter query for {language_name}: {e}")
            return None
