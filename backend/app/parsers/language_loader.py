"""Singleton loader for tree-sitter languages."""

import logging
import tree_sitter

logger = logging.getLogger(__name__)

class LanguageLoader:
    """Lazy-loads and caches tree-sitter language bindings."""

    _instance = None
    _languages: dict[str, tree_sitter.Language] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LanguageLoader, cls).__new__(cls)
        return cls._instance

    def get_language(self, language_name: str) -> tree_sitter.Language | None:
        """Returns the tree-sitter Language object for a given language name."""
        if language_name in self._languages:
            return self._languages[language_name]

        try:
            lang = None
            if language_name == "Python":
                import tree_sitter_python
                lang = tree_sitter.Language(tree_sitter_python.language())
            elif language_name == "JavaScript":
                import tree_sitter_javascript
                lang = tree_sitter.Language(tree_sitter_javascript.language())
            elif language_name == "TypeScript":
                import tree_sitter_typescript
                lang = tree_sitter.Language(tree_sitter_typescript.language_typescript())
            elif language_name == "TSX" or language_name == "JSX":
                import tree_sitter_typescript
                lang = tree_sitter.Language(tree_sitter_typescript.language_tsx())
            
            if lang:
                self._languages[language_name] = lang
                return lang
        except ImportError as e:
            logger.warning(f"Failed to import tree-sitter grammar for {language_name}: {e}")
        except Exception as e:
            logger.warning(f"Error loading tree-sitter grammar for {language_name}: {e}")
            
        return None

language_loader = LanguageLoader()
