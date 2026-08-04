from typing import Dict, List
from datetime import datetime
import logging
from app.schemas.repository_memory import SymbolMemory, MemoryMetadata
from app.parsers.ast_models import ProjectParsingResult

logger = logging.getLogger(__name__)

class SymbolTableExtractor:
    @staticmethod
    def extract(repository_id: str, parsing_result: ProjectParsingResult) -> Dict[str, SymbolMemory]:
        logger.info("=" * 80)
        logger.info("SYMBOL_TABLE_EXTRACTOR: extract() called")
        logger.info("=" * 80)
        logger.info("Repository ID: %s", repository_id)
        logger.info("Parsing result available: %s", parsing_result is not None)
        
        symbols: Dict[str, SymbolMemory] = {}
        
        if not parsing_result or not parsing_result.files:
            logger.warning("SYMBOL_TABLE_EXTRACTOR: No parsing result or no files available for symbol extraction")
            logger.info("SYMBOL_TABLE_EXTRACTOR: Total symbols extracted: 0")
            logger.info("=" * 80)
            return symbols

        logger.info("SYMBOL_TABLE_EXTRACTOR: Files available for parsing: %d", len(parsing_result.files))
        
        total_symbols = 0
        for file_info in parsing_result.files:
            metadata = MemoryMetadata(
                repository_id=repository_id,
                evidence_sources=[file_info.path]
            )

            logger.debug("Processing file: %s", file_info.path)
            logger.debug("  Classes: %d", len(file_info.classes) if hasattr(file_info, "classes") else 0)
            logger.debug("  Functions: %d", len(file_info.functions) if hasattr(file_info, "functions") else 0)

            # Extract Classes
            for class_name in file_info.classes:
                symbol_id = f"{file_info.path}::{class_name}"
                symbols[symbol_id] = SymbolMemory(
                    metadata=metadata,
                    symbol_name=class_name,
                    symbol_type="class",
                    file_path=file_info.path,
                    methods=file_info.methods if hasattr(file_info, "methods") else []
                )
                total_symbols += 1

            # Extract Functions
            all_functions = []
            if hasattr(file_info, "functions"):
                all_functions.extend(file_info.functions)
            if hasattr(file_info, "async_functions"):
                all_functions.extend(file_info.async_functions)
            if hasattr(file_info, "arrow_functions"):
                all_functions.extend(file_info.arrow_functions)

            for func_name in all_functions:
                symbol_id = f"{file_info.path}::{func_name}"
                symbols[symbol_id] = SymbolMemory(
                    metadata=metadata,
                    symbol_name=func_name,
                    symbol_type="function",
                    file_path=file_info.path
                )
                total_symbols += 1

            # Extract Interfaces
            if hasattr(file_info, "interfaces"):
                for interface_name in file_info.interfaces:
                    symbol_id = f"{file_info.path}::{interface_name}"
                    symbols[symbol_id] = SymbolMemory(
                        metadata=metadata,
                        symbol_name=interface_name,
                        symbol_type="interface",
                        file_path=file_info.path
                    )
                    total_symbols += 1
            
            # Extract Enums
            if hasattr(file_info, "enums"):
                for enum_name in file_info.enums:
                    symbol_id = f"{file_info.path}::{enum_name}"
                    symbols[symbol_id] = SymbolMemory(
                        metadata=metadata,
                        symbol_name=enum_name,
                        symbol_type="enum",
                        file_path=file_info.path
                    )
                    total_symbols += 1

            # Extract Variables (Constants/Config)
            if hasattr(file_info, "variables"):
                for var_name in file_info.variables:
                    symbol_id = f"{file_info.path}::{var_name}"
                    symbols[symbol_id] = SymbolMemory(
                        metadata=metadata,
                        symbol_name=var_name,
                        symbol_type="variable",
                        file_path=file_info.path
                    )
                    total_symbols += 1

        logger.info("SYMBOL_TABLE_EXTRACTOR: Total symbols extracted: %d", total_symbols)
        logger.info("SYMBOL_TABLE_EXTRACTOR: Symbol types breakdown:")
        symbol_types = {}
        for symbol in symbols.values():
            stype = symbol.symbol_type
            symbol_types[stype] = symbol_types.get(stype, 0) + 1
        for stype, count in symbol_types.items():
            logger.info("  %s: %d", stype, count)
        logger.info("=" * 80)
        
        return symbols

symbol_table_extractor = SymbolTableExtractor()
