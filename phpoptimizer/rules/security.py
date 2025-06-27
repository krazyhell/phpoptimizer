"""
Règles de sécurité
"""

from typing import List, Dict, Any
import re

from . import BaseRule
from ..analyzer import Issue, IssueType


class SQLInjectionRule(BaseRule):
    """Détecte les vulnérabilités d'injection SQL potentielles"""
    
    def get_rule_name(self) -> str:
        return "security.sql_injection"
    
    def get_description(self) -> str:
        return "Détecte les requêtes SQL potentiellement vulnérables aux injections"
    
    def get_issue_type(self) -> IssueType:
        return IssueType.SECURITY
    
    def analyze(self, parse_result: Dict[str, Any]) -> List[Issue]:
        issues = []
        content = parse_result.get('content', '')
        lines = content.split('\n')
        
        # Patterns dangereux pour l'injection SQL
        dangerous_patterns = [
            r'mysql_query\s*\(\s*["\'].*\$.*["\']',  # mysql_query avec variables
            r'mysqli_query\s*\(.*["\'].*\$.*["\']',   # mysqli_query avec variables
            r'query\s*\(\s*["\'].*\$.*["\']',         # query générique avec variables
            r'execute\s*\(\s*["\'].*\$.*["\']',       # execute avec variables
            r'SELECT.*\$.*FROM',                      # SELECT avec variables
            r'INSERT.*\$.*INTO',                      # INSERT avec variables
            r'UPDATE.*SET.*\$',                       # UPDATE avec variables
            r'DELETE.*WHERE.*\$',                     # DELETE avec variables
        ]
        
        for line_num, line in enumerate(lines, 1):
            line_upper = line.upper()
            
            for pattern in dangerous_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(self.create_issue(
                        message="Requête SQL potentiellement vulnérable à l'injection",
                        line=line_num,
                        column=0,
                        suggestion="Utiliser des requêtes préparées (prepare/bind) au lieu de concaténation",
                        code_snippet=line.strip()
                    ))
                    break
        
        return issues


class XSSVulnerabilityRule(BaseRule):
    """Détecte les vulnérabilités XSS potentielles"""
    
    def get_rule_name(self) -> str:
        return "security.xss_vulnerability"
    
    def get_description(self) -> str:
        return "Détecte les sorties non échappées pouvant causer des XSS"
    
    def get_issue_type(self) -> IssueType:
        return IssueType.SECURITY
    
    def analyze(self, parse_result: Dict[str, Any]) -> List[Issue]:
        issues = []
        content = parse_result.get('content', '')
        lines = content.split('\n')
        
        # Patterns dangereux pour XSS
        dangerous_patterns = [
            r'echo\s+\$_GET\[',      # echo $_GET direct
            r'echo\s+\$_POST\[',     # echo $_POST direct
            r'print\s+\$_GET\[',     # print $_GET direct
            r'print\s+\$_POST\[',    # print $_POST direct
            r'<\?=\s*\$_GET\[',      # <?= $_GET direct
            r'<\?=\s*\$_POST\[',     # <?= $_POST direct
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in dangerous_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(self.create_issue(
                        message="Sortie de données utilisateur non échappée (risque XSS)",
                        line=line_num,
                        column=0,
                        suggestion="Utiliser htmlspecialchars() ou filter_var() pour échapper les données",
                        code_snippet=line.strip()
                    ))
                    break
        
        return issues


class WeakPasswordHashingRule(BaseRule):
    """Détecte l'utilisation d'algorithmes de hachage faibles"""
    
    def get_rule_name(self) -> str:
        return "security.weak_password_hashing"
    
    def get_description(self) -> str:
        return "Détecte l'utilisation d'algorithmes de hachage faibles pour les mots de passe"
    
    def get_issue_type(self) -> IssueType:
        return IssueType.SECURITY
    
    def analyze(self, parse_result: Dict[str, Any]) -> List[Issue]:
        issues = []
        content = parse_result.get('content', '')
        lines = content.split('\n')
        
        # Fonctions de hachage faibles
        weak_hash_functions = [
            r'md5\s*\(',
            r'sha1\s*\(',
            r'hash\s*\(\s*["\']md5["\']',
            r'hash\s*\(\s*["\']sha1["\']',
            r'crypt\s*\(',  # Sans salt approprié
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in weak_hash_functions:
                if re.search(pattern, line, re.IGNORECASE):
                    # Vérifier si c'est dans un contexte de mot de passe
                    if any(keyword in line.lower() for keyword in ['password', 'passwd', 'pwd', 'pass']):
                        issues.append(self.create_issue(
                            message="Algorithme de hachage faible utilisé pour un mot de passe",
                            line=line_num,
                            column=0,
                            suggestion="Utiliser password_hash() avec PASSWORD_DEFAULT ou bcrypt",
                            code_snippet=line.strip()
                        ))
                        break
        
        return issues


class FileInclusionRule(BaseRule):
    """Détecte les vulnérabilités d'inclusion de fichier"""
    
    def get_rule_name(self) -> str:
        return "security.file_inclusion"
    
    def get_description(self) -> str:
        return "Détecte les inclusions de fichiers potentiellement dangereuses"
    
    def get_issue_type(self) -> IssueType:
        return IssueType.SECURITY
    
    def analyze(self, parse_result: Dict[str, Any]) -> List[Issue]:
        issues = []
        content = parse_result.get('content', '')
        lines = content.split('\n')
        
        # Patterns dangereux pour l'inclusion de fichiers
        dangerous_patterns = [
            r'include\s*\(\s*\$_GET\[',      # include($_GET[...])
            r'include_once\s*\(\s*\$_GET\[', # include_once($_GET[...])
            r'require\s*\(\s*\$_GET\[',      # require($_GET[...])
            r'require_once\s*\(\s*\$_GET\[', # require_once($_GET[...])
            r'include\s*\(\s*\$_POST\[',     # include($_POST[...])
            r'include_once\s*\(\s*\$_POST\[',# include_once($_POST[...])
            r'require\s*\(\s*\$_POST\[',     # require($_POST[...])
            r'require_once\s*\(\s*\$_POST\[',# require_once($_POST[...])
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in dangerous_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(self.create_issue(
                        message="Inclusion de fichier basée sur des données utilisateur",
                        line=line_num,
                        column=0,
                        suggestion="Valider et filtrer le nom du fichier, ou utiliser une whitelist",
                        code_snippet=line.strip()
                    ))
                    break
        
        return issues
