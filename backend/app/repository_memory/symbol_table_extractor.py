from typing import Dict, List
from datetime import datetime
from app.schemas.repository_memory import SymbolMemory, MemoryMetadata
from app.parsers.ast_models import ProjectParsingResult

class SymbolTableExtractor:
    @staticmethod
    def extract(repository_id: str, parsing_result: ProjectParsingResult) -> Dict[str, SymbolMemory]:
        symbols: Dict[str, SymbolMemory] = {}
        
        if not parsing_result or not parsing_result.files:
            return symbols

        for file_info in parsing_result.files:
            metadata = MemoryMetadata(
                repository_id=repository_id,
                evidence_sources=[file_info.path]
            )

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

        return symbols

symbol_table_extractor = SymbolTableExtractor()
