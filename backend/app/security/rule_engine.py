"""Rule engine for security vulnerability detection.

Defines rule-based patterns for detecting common security issues
without using AI or LLMs. All detection is deterministic.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Pattern


class Severity(Enum):
    """Severity levels for security issues."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class SecurityRule:
    """A security detection rule."""
    
    name: str
    description: str
    severity: Severity
    pattern: Pattern[str]
    languages: list[str] = field(default_factory=list)
    file_patterns: list[str] = field(default_factory=list)


class RuleEngine:
    """Manages security detection rules."""
    
    def __init__(self):
        """Initialize the rule engine with default rules."""
        self.rules = self._load_default_rules()
    
    def _load_default_rules(self) -> list[SecurityRule]:
        """Load default security detection rules."""
        rules = []
        
        # Hardcoded API Keys
        rules.append(SecurityRule(
            name="Hardcoded API Key",
            description="Possible hardcoded API key detected",
            severity=Severity.CRITICAL,
            pattern=re.compile(r'(?:api[_-]?key|apikey)["\']?\s*[:=]\s*["\']([a-zA-Z0-9_-]{20,})["\']', re.IGNORECASE),
            languages=["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C#", "PHP"],
        ))
        
        # OpenAI Keys
        rules.append(SecurityRule(
            name="OpenAI API Key",
            description="Possible OpenAI API key detected",
            severity=Severity.CRITICAL,
            pattern=re.compile(r'sk-[a-zA-Z0-9]{48}', re.IGNORECASE),
            languages=["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C#", "PHP"],
        ))
        
        # AWS Keys
        rules.append(SecurityRule(
            name="AWS Access Key",
            description="Possible AWS access key detected",
            severity=Severity.CRITICAL,
            pattern=re.compile(r'AKIA[0-9A-Z]{16}', re.IGNORECASE),
            languages=["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C#", "PHP"],
        ))
        
        # GitHub Tokens
        rules.append(SecurityRule(
            name="GitHub Token",
            description="Possible GitHub personal access token detected",
            severity=Severity.CRITICAL,
            pattern=re.compile(r'ghp_[a-zA-Z0-9]{36}', re.IGNORECASE),
            languages=["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C#", "PHP"],
        ))
        
        # Google API Keys
        rules.append(SecurityRule(
            name="Google API Key",
            description="Possible Google API key detected",
            severity=Severity.HIGH,
            pattern=re.compile(r'AIza[0-9A-Za-z_-]{35}', re.IGNORECASE),
            languages=["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C#", "PHP"],
        ))
        
        # Hardcoded Passwords
        rules.append(SecurityRule(
            name="Hardcoded Password",
            description="Possible hardcoded password detected",
            severity=Severity.HIGH,
            pattern=re.compile(r'(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']([^"\']{4,})["\']', re.IGNORECASE),
            languages=["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C#", "PHP"],
        ))
        
        # Private Keys
        rules.append(SecurityRule(
            name="Private Key",
            description="Possible private key detected",
            severity=Severity.CRITICAL,
            pattern=re.compile(r'-----BEGIN (?:RSA )?PRIVATE KEY-----', re.IGNORECASE),
            languages=["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C#", "PHP"],
        ))
        
        # JWT Secrets
        rules.append(SecurityRule(
            name="JWT Secret",
            description="Possible JWT secret key detected",
            severity=Severity.HIGH,
            pattern=re.compile(r'(?:jwt[_-]?secret|secret[_-]?jwt)["\']?\s*[:=]\s*["\']([^"\']{10,})["\']', re.IGNORECASE),
            languages=["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C#", "PHP"],
        ))
        
        # Debug Mode (Python)
        rules.append(SecurityRule(
            name="Debug Mode Enabled",
            description="Debug mode may be enabled in production",
            severity=Severity.MEDIUM,
            pattern=re.compile(r'debug\s*=\s*True', re.IGNORECASE),
            languages=["Python"],
        ))
        
        # Debug Mode (JavaScript/Node)
        rules.append(SecurityRule(
            name="Debug Mode Enabled",
            description="Debug mode may be enabled in production",
            severity=Severity.MEDIUM,
            pattern=re.compile(r'debug\s*:\s*true', re.IGNORECASE),
            languages=["JavaScript", "TypeScript"],
        ))
        
        # Dangerous CORS
        rules.append(SecurityRule(
            name="Dangerous CORS Configuration",
            description="CORS configuration allows all origins",
            severity=Severity.HIGH,
            pattern=re.compile(r'(?:allow[_-]?origins|cors)["\']?\s*[:=]\s*["\']?\*["\']?', re.IGNORECASE),
            languages=["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C#", "PHP"],
        ))
        
        # SQL Injection Risk (Python)
        rules.append(SecurityRule(
            name="SQL Injection Risk",
            description="Possible SQL injection vulnerability",
            severity=Severity.HIGH,
            pattern=re.compile(r'(?:execute|executemany)\s*\(\s*[\'"]\s*%s', re.IGNORECASE),
            languages=["Python"],
        ))
        
        # SQL Injection Risk (JavaScript/TypeScript)
        rules.append(SecurityRule(
            name="SQL Injection Risk",
            description="Possible SQL injection vulnerability",
            severity=Severity.HIGH,
            pattern=re.compile(r'(?:query|execute)\s*\(\s*[\'"]\s*\$\{', re.IGNORECASE),
            languages=["JavaScript", "TypeScript"],
        ))
        
        # Shell Command Execution (Python)
        rules.append(SecurityRule(
            name="Unsafe Shell Command",
            description="Unsafe shell command execution detected",
            severity=Severity.HIGH,
            pattern=re.compile(r'(?:os\.system|subprocess\.(?:call|run|Popen))\s*\(\s*[\'"]', re.IGNORECASE),
            languages=["Python"],
        ))
        
        # Shell Command Execution (JavaScript/Node)
        rules.append(SecurityRule(
            name="Unsafe Shell Command",
            description="Unsafe shell command execution detected",
            severity=Severity.HIGH,
            pattern=re.compile(r'(?:exec|spawn)\s*\(\s*[\'"]', re.IGNORECASE),
            languages=["JavaScript", "TypeScript"],
        ))
        
        # Unsafe eval() (Python)
        rules.append(SecurityRule(
            name="Unsafe eval()",
            description="Unsafe eval() function detected",
            severity=Severity.HIGH,
            pattern=re.compile(r'\beval\s*\(', re.IGNORECASE),
            languages=["Python", "JavaScript", "TypeScript"],
        ))
        
        # Unsafe exec() (Python)
        rules.append(SecurityRule(
            name="Unsafe exec()",
            description="Unsafe exec() function detected",
            severity=Severity.HIGH,
            pattern=re.compile(r'\bexec\s*\(', re.IGNORECASE),
            languages=["Python"],
        ))
        
        # Pickle Deserialization (Python)
        rules.append(SecurityRule(
            name="Unsafe Pickle Deserialization",
            description="Unsafe pickle deserialization detected",
            severity=Severity.CRITICAL,
            pattern=re.compile(r'pickle\.(?:load|loads)\s*\(', re.IGNORECASE),
            languages=["Python"],
        ))
        
        # Weak Cryptography (MD5, SHA1)
        rules.append(SecurityRule(
            name="Weak Cryptography",
            description="Weak cryptographic algorithm detected",
            severity=Severity.MEDIUM,
            pattern=re.compile(r'(?:md5|sha1)\s*\(', re.IGNORECASE),
            languages=["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C#", "PHP"],
        ))
        
        # Directory Traversal Risk
        rules.append(SecurityRule(
            name="Directory Traversal Risk",
            description="Possible directory traversal vulnerability",
            severity=Severity.HIGH,
            pattern=re.compile(r'(?:open|read)\s*\(\s*[\'"]\.\.', re.IGNORECASE),
            languages=["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C#", "PHP"],
        ))
        
        # Insecure File Upload
        rules.append(SecurityRule(
            name="Insecure File Upload",
            description="Possible insecure file upload logic",
            severity=Severity.HIGH,
            pattern=re.compile(r'(?:save|upload)\s*\(\s*[\'"]\.\.', re.IGNORECASE),
            languages=["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C#", "PHP"],
        ))
        
        # Exposed Secrets in Environment Variables
        rules.append(SecurityRule(
            name="Exposed Secret in Environment Variable",
            description="Possible secret exposed in environment variable assignment",
            severity=Severity.MEDIUM,
            pattern=re.compile(r'(?:password|secret|key|token)["\']?\s*=\s*os\.environ', re.IGNORECASE),
            languages=["Python"],
        ))
        
        return rules
    
    def get_rules_for_language(self, language: str) -> list[SecurityRule]:
        """Get rules applicable to a specific language."""
        return [rule for rule in self.rules if not rule.languages or language in rule.languages]
    
    def get_all_rules(self) -> list[SecurityRule]:
        """Get all security rules."""
        return self.rules


rule_engine = RuleEngine()
