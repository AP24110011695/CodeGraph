"""Code smell detection rules for CodeGraph.

Deterministic, rule-based thresholds for detecting code smells.
No AI, no heuristics - only measurable metrics.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class SmellThreshold:
    """Threshold configuration for a code smell."""

    name: str
    severity: Literal["critical", "major", "minor"]
    description: str
    threshold: int | float


# File-based thresholds
LARGE_FILE_THRESHOLD = SmellThreshold(
    name="Large File",
    severity="major",
    description="File size exceeds configured threshold (lines or bytes).",
    threshold=500,  # lines
)

LONG_FILE_THRESHOLD = SmellThreshold(
    name="Long File",
    severity="minor",
    description="File is excessively long and should be split.",
    threshold=1000,  # lines
)

# Class-based thresholds
LARGE_CLASS_THRESHOLD = SmellThreshold(
    name="Large Class",
    severity="major",
    description="Class has too many methods or lines.",
    threshold=20,  # methods
)

GOD_OBJECT_THRESHOLD = SmellThreshold(
    name="God Object",
    severity="critical",
    description="Class knows too much or does too much.",
    threshold=50,  # methods
)

TOO_MANY_PUBLIC_METHODS_THRESHOLD = SmellThreshold(
    name="Too Many Public Methods",
    severity="major",
    description="Class has excessive public API surface.",
    threshold=15,  # public methods
)

EMPTY_CLASS_THRESHOLD = SmellThreshold(
    name="Empty Class",
    severity="minor",
    description="Class has no methods or meaningful content.",
    threshold=0,  # methods
)

# Function-based thresholds
LARGE_FUNCTION_THRESHOLD = SmellThreshold(
    name="Large Function",
    severity="major",
    description="Function exceeds configured complexity threshold.",
    threshold=50,  # lines
)

EMPTY_FUNCTION_THRESHOLD = SmellThreshold(
    name="Empty Function",
    severity="minor",
    description="Function has no implementation.",
    threshold=0,  # lines
)

LONG_PARAMETER_LIST_THRESHOLD = SmellThreshold(
    name="Long Parameter List",
    severity="minor",
    description="Function has too many parameters.",
    threshold=5,  # parameters
)

# Module-based thresholds
LARGE_MODULE_THRESHOLD = SmellThreshold(
    name="Large Module",
    severity="major",
    description="Module contains too many files.",
    threshold=20,  # files
)

# Dependency-based thresholds
HIGH_FAN_IN_THRESHOLD = SmellThreshold(
    name="High Fan-In",
    severity="major",
    description="File is depended upon by too many other files.",
    threshold=10,  # incoming edges
)

HIGH_FAN_OUT_THRESHOLD = SmellThreshold(
    name="High Fan-Out",
    severity="major",
    description="File depends on too many other files.",
    threshold=10,  # outgoing edges
)

EXCESSIVE_COUPLING_THRESHOLD = SmellThreshold(
    name="Excessive Coupling",
    severity="critical",
    description="Module has too many dependencies.",
    threshold=20,  # total edges
)

CIRCULAR_DEPENDENCY_THRESHOLD = SmellThreshold(
    name="Circular Dependency",
    severity="critical",
    description="Files have circular import dependencies.",
    threshold=1,  # any cycle
)

# Code quality thresholds
DUPLICATE_IMPORTS_THRESHOLD = SmellThreshold(
    name="Duplicate Imports",
    severity="minor",
    description="File imports the same module multiple times.",
    threshold=1,  # any duplicate
)

MISSING_DOCUMENTATION_THRESHOLD = SmellThreshold(
    name="Missing Documentation",
    severity="minor",
    description="File lacks docstrings or comments.",
    threshold=0,  # any missing
)

# File usage thresholds
DEAD_FILE_THRESHOLD = SmellThreshold(
    name="Dead File",
    severity="major",
    description="File is not imported or used by any other file.",
    threshold=0,  # any dead file
)

UNUSED_FILE_THRESHOLD = SmellThreshold(
    name="Unused File",
    severity="minor",
    description="File has no incoming dependencies.",
    threshold=0,  # any unused file
)


class SmellRules:
    """Container for all code smell detection rules."""

    # File-based rules
    LARGE_FILE = LARGE_FILE_THRESHOLD
    LONG_FILE = LONG_FILE_THRESHOLD

    # Class-based rules
    LARGE_CLASS = LARGE_CLASS_THRESHOLD
    GOD_OBJECT = GOD_OBJECT_THRESHOLD
    TOO_MANY_PUBLIC_METHODS = TOO_MANY_PUBLIC_METHODS_THRESHOLD
    EMPTY_CLASS = EMPTY_CLASS_THRESHOLD

    # Function-based rules
    LARGE_FUNCTION = LARGE_FUNCTION_THRESHOLD
    EMPTY_FUNCTION = EMPTY_FUNCTION_THRESHOLD
    LONG_PARAMETER_LIST = LONG_PARAMETER_LIST_THRESHOLD

    # Module-based rules
    LARGE_MODULE = LARGE_MODULE_THRESHOLD

    # Dependency-based rules
    HIGH_FAN_IN = HIGH_FAN_IN_THRESHOLD
    HIGH_FAN_OUT = HIGH_FAN_OUT_THRESHOLD
    EXCESSIVE_COUPLING = EXCESSIVE_COUPLING_THRESHOLD
    CIRCULAR_DEPENDENCY = CIRCULAR_DEPENDENCY_THRESHOLD

    # Code quality rules
    DUPLICATE_IMPORTS = DUPLICATE_IMPORTS_THRESHOLD
    MISSING_DOCUMENTATION = MISSING_DOCUMENTATION_THRESHOLD

    # File usage rules
    DEAD_FILE = DEAD_FILE_THRESHOLD
    UNUSED_FILE = UNUSED_FILE_THRESHOLD

    @classmethod
    def get_all_rules(cls) -> list[SmellThreshold]:
        """Get all defined smell rules."""
        return [
            cls.LARGE_FILE,
            cls.LONG_FILE,
            cls.LARGE_CLASS,
            cls.GOD_OBJECT,
            cls.TOO_MANY_PUBLIC_METHODS,
            cls.EMPTY_CLASS,
            cls.LARGE_FUNCTION,
            cls.EMPTY_FUNCTION,
            cls.LONG_PARAMETER_LIST,
            cls.LARGE_MODULE,
            cls.HIGH_FAN_IN,
            cls.HIGH_FAN_OUT,
            cls.EXCESSIVE_COUPLING,
            cls.CIRCULAR_DEPENDENCY,
            cls.DUPLICATE_IMPORTS,
            cls.MISSING_DOCUMENTATION,
            cls.DEAD_FILE,
            cls.UNUSED_FILE,
        ]


smell_rules = SmellRules()
