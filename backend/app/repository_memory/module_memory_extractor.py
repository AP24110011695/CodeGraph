import re
from typing import Dict, List
from app.schemas.repository_memory import ModuleMemory, MemoryMetadata
from app.analyzers.architecture_models import ArchitectureResult

class ModuleMemoryExtractor:
    @staticmethod
    def extract(repository_id: str, architecture_result: ArchitectureResult) -> Dict[str, ModuleMemory]:
        modules: Dict[str, ModuleMemory] = {}

        if not architecture_result or not architecture_result.modules:
            return modules

        # Pre-compute dependencies based on relationships
        module_deps: Dict[str, set] = {m.name: set() for m in architecture_result.modules}
        if architecture_result.relationships:
            for rel in architecture_result.relationships:
                # Assuming source/target can be mapped to modules if they match
                # Let's extract module names from relationships if possible
                pass

        for module in architecture_result.modules:
            metadata = MemoryMetadata(
                repository_id=repository_id,
                evidence_sources=[f"module:{module.name}"] + module.files
            )

            responsibilities = set()
            public_interfaces = set()

            # Detect responsibilities from name
            responsibilities.add(module.name)
            if module.type:
                responsibilities.add(module.type)
            if module.layer:
                responsibilities.add(f"{module.layer} layer")

            for comp in module.components:
                # Add component names as responsibilities
                clean_name = comp.name.lower().replace("controller", "").replace("service", "").replace("manager", "")
                if clean_name:
                    responsibilities.add(clean_name.strip())
                
                # If it's a controller/route/api, it's likely a public interface
                if "controller" in comp.name.lower() or "route" in comp.name.lower() or "api" in comp.name.lower():
                    public_interfaces.add(comp.name)
            
            # Clean up responsibilities to be human readable
            cleaned_responsibilities = list(set([r for r in responsibilities if r and len(r) > 2]))

            modules[module.name] = ModuleMemory(
                metadata=metadata,
                module_name=module.name,
                files=module.files,
                responsibilities=cleaned_responsibilities,
                public_interfaces=list(public_interfaces),
                dependencies=list(module_deps.get(module.name, []))
            )

        return modules

module_memory_extractor = ModuleMemoryExtractor()
