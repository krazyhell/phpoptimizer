"""
Règles d'optimisation de performance
"""

from typing import List, Dict, Any
import re

from . import BaseRule


class UnusedVariablesRule(BaseRule):
    """Détecte les variables déclarées mais non utilisées"""
    
    def get_rule_name(self) -> str:
        return "performance.unused_variables"
    
    def get_description(self) -> str:
        return "Détecte les variables déclarées mais jamais utilisées"
    
    def get_issue_type(self) -> IssueType:
        return IssueType.PERFORMANCE
    
    def analyze(self, parse_result: Dict[str, Any]) -> List[Issue]:
        issues = []
        content = parse_result.get('content', '')
        metadata = parse_result.get('metadata', {})
        
        # Analyser les variables déclarées
        declared_vars = set()
        used_vars = set()
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Rechercher les déclarations de variables
            var_declarations = re.findall(r'\$([a-zA-Z_][a-zA-Z0-9_]*)\s*=', line)
            declared_vars.update(var_declarations)
            
            # Rechercher les utilisations de variables
            var_usages = re.findall(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', line)
            used_vars.update(var_usages)
        
        # Trouver les variables non utilisées
        unused_vars = declared_vars - used_vars
        
        for var_name in unused_vars:
            # Trouver la ligne de déclaration
            for line_num, line in enumerate(lines, 1):
                if f'${var_name}' in line and '=' in line:
                    issues.append(self.create_issue(
                        message=f"Variable '${var_name}' déclarée mais jamais utilisée",
                        line=line_num,
                        column=line.find(f'${var_name}'),
                        suggestion=f"Supprimer la variable '${var_name}' ou l'utiliser",
                        code_snippet=line.strip()
                    ))
                    break
        
        return issues


class InefficientLoopsRule(BaseRule):
    """Détecte les boucles potentiellement inefficaces"""
    
    def get_rule_name(self) -> str:
        return "performance.inefficient_loops"
    
    def get_description(self) -> str:
        return "Détecte les boucles avec des patterns inefficaces"
    
    def get_issue_type(self) -> IssueType:
        return IssueType.PERFORMANCE
    
    def analyze(self, parse_result: Dict[str, Any]) -> List[Issue]:
        issues = []
        content = parse_result.get('content', '')
        lines = content.split('\n')
        
        max_nested_loops = self.get_param('max_nested_loops', 3)
        
        # Analyser les boucles imbriquées
        loop_stack = []
        
        for line_num, line in enumerate(lines, 1):
            line_trimmed = line.strip()
            
            # Détecter le début d'une boucle
            if (re.search(r'\b(for|foreach|while)\s*\(', line_trimmed) or
                'do' in line_trimmed):
                loop_stack.append(line_num)
                
                # Vérifier le niveau d'imbrication
                if len(loop_stack) > max_nested_loops:
                    issues.append(self.create_issue(
                        message=f"Boucle imbriquée trop profonde (niveau {len(loop_stack)})",
                        line=line_num,
                        column=0,
                        suggestion="Considérer extraire la logique en fonction séparée",
                        code_snippet=line.strip()
                    ))
            
            # Détecter la fin d'une boucle (approximatif)
            if line_trimmed == '}' and loop_stack:
                loop_stack.pop()
            
            # Détecter les appels de fonction dans les boucles
            if (loop_stack and 
                re.search(r'(count|sizeof|strlen)\s*\(', line_trimmed) and
                re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*', line_trimmed)):
                
                issues.append(self.create_issue(
                    message="Appel de function coûteuse dans une boucle",
                    line=line_num,
                    column=0,
                    suggestion="Stocker le résultat dans une variable avant la boucle",
                    code_snippet=line.strip()
                ))
        
        return issues


class RepeatedCalculationsRule(BaseRule):
    """Détecte les calculs répétés qui pourraient être mis en cache"""
    
    def get_rule_name(self) -> str:
        return "performance.repeated_calculations"
    
    def get_description(self) -> str:
        return "Détecte les calculs identiques répétés"
    
    def get_issue_type(self) -> IssueType:
        return IssueType.PERFORMANCE
    
    def analyze(self, parse_result: Dict[str, Any]) -> List[Issue]:
        issues = []
        content = parse_result.get('content', '')
        lines = content.split('\n')
        
        # Rechercher les expressions mathématiques répétées
        math_expressions = {}
        
        for line_num, line in enumerate(lines, 1):
            # Rechercher les expressions mathématiques
            expressions = re.findall(r'[a-zA-Z_$][a-zA-Z0-9_$]*\s*[\+\-\*\/]\s*[a-zA-Z0-9_$]+', line)
            
            for expr in expressions:
                expr_clean = re.sub(r'\s+', ' ', expr.strip())
                if expr_clean not in math_expressions:
                    math_expressions[expr_clean] = []
                math_expressions[expr_clean].append((line_num, line.strip()))
        
        # Signaler les expressions répétées
        for expr, occurrences in math_expressions.items():
            if len(occurrences) > 1:
                first_line, first_code = occurrences[0]
                issues.append(self.create_issue(
                    message=f"Expression mathématique répétée: {expr}",
                    line=first_line,
                    column=0,
                    suggestion=f"Stocker le résultat de '{expr}' dans une variable",
                    code_snippet=first_code
                ))
        
        return issues


class LargeArraysRule(BaseRule):
    """Détecte les tableaux potentiellement trop volumineux"""
    
    def get_rule_name(self) -> str:
        return "performance.large_arrays"
    
    def get_description(self) -> str:
        return "Détecte les déclarations de tableaux volumineux"
    
    def get_issue_type(self) -> IssueType:
        return IssueType.PERFORMANCE
    
    def analyze(self, parse_result: Dict[str, Any]) -> List[Issue]:
        issues = []
        content = parse_result.get('content', '')
        lines = content.split('\n')
        
        max_array_size = self.get_param('max_array_size', 1000)
        
        for line_num, line in enumerate(lines, 1):
            # Rechercher les déclarations de tableaux avec beaucoup d'éléments
            if 'array(' in line or '[' in line:
                # Compter les virgules comme approximation du nombre d'éléments
                comma_count = line.count(',')
                
                if comma_count > max_array_size / 10:  # Estimation approximative
                    issues.append(self.create_issue(
                        message=f"Tableau potentiellement volumineux (~{comma_count + 1} éléments)",
                        line=line_num,
                        column=0,
                        suggestion="Considérer charger les données depuis une source externe ou les paginer",
                        code_snippet=line.strip()[:100] + "..." if len(line.strip()) > 100 else line.strip()
                    ))
        
        return issues
