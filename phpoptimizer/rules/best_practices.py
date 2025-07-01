"""
Règles de bonnes pratiques
"""

from typing import List, Dict, Any
import re

from . import BaseRule
from ..analyzer import Issue, IssueType


class PSRComplianceRule(BaseRule):
    """Vérifie la conformité aux standards PSR"""
    
    def get_rule_name(self) -> str:
        return "best_practices.psr_compliance"
    
    def get_description(self) -> str:
        return "Vérifie la conformité aux standards PSR (PHP Standards Recommendations)"
    
    def get_issue_type(self) -> IssueType:
        return IssueType.BEST_PRACTICES
    
    def analyze(self, parse_result: Dict[str, Any]) -> List[Issue]:
        issues = []
        content = parse_result.get('content', '')
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # PSR-1: Balises PHP
            if line_num == 1 and not line.startswith('<?php'):
                if line.strip() and not line.startswith('<?php'):
                    issues.append(self.create_issue(
                        message="Fichier PHP doit commencer par <?php",
                        line=line_num,
                        column=0,
                        suggestion="Ajouter <?php au début du fichier",
                        code_snippet=line.strip()
                    ))
            
            # PSR-2: Indentation (4 espaces)
            if line.startswith('\t'):
                issues.append(self.create_issue(
                    message="Utilisation de tabulations au lieu d'espaces pour l'indentation",
                    line=line_num,
                    column=0,
                    suggestion="Utiliser 4 espaces pour l'indentation (PSR-2)",
                    code_snippet=line[:20] + "..." if len(line) > 20 else line
                ))
            
            # PSR-2: Lignes trop longues
            if len(line) > 120:
                issues.append(self.create_issue(
                    message=f"Ligne trop longue ({len(line)} caractères)",
                    line=line_num,
                    column=120,
                    suggestion="Limiter les lignes à 120 caractères maximum",
                    code_snippet=line[:50] + "..."
                ))
            
            # PSR-2: Espaces autour des opérateurs
            if re.search(r'[a-zA-Z0-9_]\+[a-zA-Z0-9_]', line):
                issues.append(self.create_issue(
                    message="Manque d'espaces autour de l'opérateur +",
                    line=line_num,
                    column=0,
                    suggestion="Ajouter des espaces: a + b au lieu de a+b",
                    code_snippet=line.strip()
                ))
            
            # PSR-12: Déclarations de fonctions
            if re.search(r'function\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*{', line):
                if not re.search(r'function\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*\n', line):
                    issues.append(self.create_issue(
                        message="Accolade ouvrante de fonction doit être sur une nouvelle ligne",
                        line=line_num,
                        column=0,
                        suggestion="Placer { sur la ligne suivante",
                        code_snippet=line.strip()
                    ))
        
        return issues


class FunctionComplexityRule(BaseRule):
    """Analyse la complexité des fonctions"""
    
    def get_rule_name(self) -> str:
        return "best_practices.function_complexity"
    
    def get_description(self) -> str:
        return "Analyse la complexité cyclomatique des fonctions"
    
    def get_issue_type(self) -> IssueType:
        return IssueType.MAINTAINABILITY
    
    def analyze(self, parse_result: Dict[str, Any]) -> List[Issue]:
        issues = []
        content = parse_result.get('content', '')
        lines = content.split('\n')
        
        max_complexity = self.get_param('max_complexity', 10)
        
        current_function = None
        function_start_line = 0
        complexity = 0
        brace_count = 0
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Détecter le début d'une fonction
            function_match = re.search(r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)', line_stripped)
            if function_match:
                current_function = function_match.group(1)
                function_start_line = line_num
                complexity = 1  # Complexité de base
                brace_count = 0
            
            if current_function:
                # Compter les accolades pour détecter la fin de fonction
                brace_count += line_stripped.count('{') - line_stripped.count('}')
                
                # Compter les structures de contrôle qui augmentent la complexité
                control_structures = ['if', 'else', 'elseif', 'for', 'foreach', 
                                    'while', 'switch', 'case', 'catch', '?', '&&', '||']
                
                for structure in control_structures:
                    if structure == '?' and '?' in line_stripped:
                        complexity += line_stripped.count('?')
                    elif structure in ['&&', '||']:
                        complexity += line_stripped.count(structure)
                    elif re.search(rf'\b{re.escape(structure)}\b', line_stripped):
                        complexity += 1
                
                # Fin de fonction détectée
                if brace_count <= 0 and current_function and line_stripped.endswith('}'):
                    if complexity > max_complexity:
                        issues.append(self.create_issue(
                            message=f"Fonction '{current_function}' trop complexe (complexité: {complexity})",
                            line=function_start_line,
                            column=0,
                            suggestion=f"Réduire la complexité en dessous de {max_complexity} (extraire du code en fonctions séparées)",
                            code_snippet=f"function {current_function}..."
                        ))
                    
                    current_function = None
        
        return issues


class MissingDocumentationRule(BaseRule):
    """Détecte les fonctions et classes sans documentation"""
    
    def get_rule_name(self) -> str:
        return "best_practices.missing_documentation"
    
    def get_description(self) -> str:
        return "Détecte les fonctions et classes publiques sans documentation"
    
    def get_issue_type(self) -> IssueType:
        return IssueType.MAINTAINABILITY
    
    def analyze(self, parse_result: Dict[str, Any]) -> List[Issue]:
        issues = []
        content = parse_result.get('content', '')
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Détecter les fonctions publiques
            if re.search(r'(public\s+)?function\s+[a-zA-Z_][a-zA-Z0-9_]*', line_stripped):
                # Vérifier s'il y a un commentaire DocBlock avant
                has_docblock = False
                
                # Chercher dans les lignes précédentes
                for i in range(max(0, line_num - 10), line_num - 1):
                    if i < len(lines):
                        prev_line = lines[i].strip()
                        if prev_line.startswith('/**') or '/**' in prev_line:
                            has_docblock = True
                            break
                        elif prev_line and not prev_line.startswith('//') and not prev_line.startswith('*'):
                            break
                
                if not has_docblock:
                    function_name = re.search(r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)', line_stripped)
                    if function_name:
                        issues.append(self.create_issue(
                            message=f"Fonction '{function_name.group(1)}' sans documentation",
                            line=line_num,
                            column=0,
                            suggestion="Ajouter un bloc de commentaires DocBlock avant la fonction",
                            code_snippet=line.strip()
                        ))
            
            # Détecter les classes publiques
            if re.search(r'class\s+[A-Z][a-zA-Z0-9_]*', line_stripped):
                # Vérifier s'il y a un commentaire DocBlock avant
                has_docblock = False
                
                for i in range(max(0, line_num - 10), line_num - 1):
                    if i < len(lines):
                        prev_line = lines[i].strip()
                        if prev_line.startswith('/**') or '/**' in prev_line:
                            has_docblock = True
                            break
                        elif prev_line and not prev_line.startswith('//') and not prev_line.startswith('*'):
                            break
                
                if not has_docblock:
                    class_name = re.search(r'class\s+([A-Z][a-zA-Z0-9_]*)', line_stripped)
                    if class_name:
                        issues.append(self.create_issue(
                            message=f"Classe '{class_name.group(1)}' sans documentation",
                            line=line_num,
                            column=0,
                            suggestion="Ajouter un bloc de commentaires DocBlock avant la classe",
                            code_snippet=line.strip()
                        ))
        
        return issues


class MissingConstructorRule(BaseRule):
    """Détecte les classes déclarées sans constructeur"""
    
    def get_rule_name(self) -> str:
        return "best_practices.missing_constructor"
    
    def get_description(self) -> str:
        return "Détecte les classes déclarées sans constructeur explicite"
    
    def get_issue_type(self) -> IssueType:
        return IssueType.MAINTAINABILITY
    
    def analyze(self, parse_result: Dict[str, Any]) -> List[Issue]:
        issues = []
        content = parse_result.get('content', '')
        lines = content.split('\n')
        
        current_class = None
        class_start_line = 0
        brace_count = 0
        has_constructor = False
        class_has_properties = False
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Détecter le début d'une classe
            class_match = re.search(r'class\s+([A-Z][a-zA-Z0-9_]*)', line_stripped)
            if class_match:
                # Si on était déjà dans une classe, vérifier si elle avait un constructeur
                if current_class and not has_constructor and class_has_properties:
                    issues.append(self.create_issue(
                        message=f"Classe '{current_class}' sans constructeur explicite",
                        line=class_start_line,
                        column=0,
                        suggestion="Ajouter un constructeur __construct() pour initialiser les propriétés",
                        code_snippet=f"class {current_class}"
                    ))
                
                current_class = class_match.group(1)
                class_start_line = line_num
                brace_count = 0
                has_constructor = False
                class_has_properties = False
            
            if current_class:
                # Compter les accolades pour détecter la fin de classe
                brace_count += line_stripped.count('{') - line_stripped.count('}')
                
                # Détecter un constructeur
                if re.search(r'function\s+__construct', line_stripped):
                    has_constructor = True
                
                # Détecter des propriétés de classe (variables d'instance)
                if re.search(r'(private|protected|public)\s+\$[a-zA-Z_][a-zA-Z0-9_]*', line_stripped):
                    class_has_properties = True
                
                # Fin de classe détectée
                if brace_count <= 0 and current_class and line_stripped == '}':
                    if not has_constructor and class_has_properties:
                        issues.append(self.create_issue(
                            message=f"Classe '{current_class}' sans constructeur explicite",
                            line=class_start_line,
                            column=0,
                            suggestion="Ajouter un constructeur __construct() pour initialiser les propriétés",
                            code_snippet=f"class {current_class}"
                        ))
                    
                    current_class = None
        
        # Vérifier la dernière classe si le fichier se termine sans accolade fermante claire
        if current_class and not has_constructor and class_has_properties:
            issues.append(self.create_issue(
                message=f"Classe '{current_class}' sans constructeur explicite",
                line=class_start_line,
                column=0,
                suggestion="Ajouter un constructeur __construct() pour initialiser les propriétés",
                code_snippet=f"class {current_class}"
            ))
        
        return issues
