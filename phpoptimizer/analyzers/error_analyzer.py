"""
Analyseur spécialisé pour la détection d'erreurs
"""

import re
from pathlib import Path
from typing import List, Dict, Any

from .base_analyzer import BaseAnalyzer


class ErrorAnalyzer(BaseAnalyzer):
    """Analyseur spécialisé pour la détection d'erreurs de code"""
    
    def analyze(self, content: str, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """Analyser les erreurs dans le code PHP"""
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Ignorer les commentaires et directives Blade
            if self._is_comment_line(line) or self._is_blade_directive(line):
                continue
            
            # Détecter les erreurs de syntaxe communes
            self._detect_syntax_errors(line_stripped, line_num, file_path, line, issues)
            
            # Détecter les appels de méthode sur null
            self._detect_null_method_calls(line_stripped, line_num, file_path, line, issues)
            
            # Détecter les variables non initialisées
            self._detect_uninitialized_variables(line_stripped, line_num, file_path, line, lines, issues)
            
            # Détecter les erreurs d'arguments de fonction
            self._detect_function_argument_errors(line_stripped, line_num, file_path, line, issues)
            
            # Détecter les affectations dans les conditions
            self._detect_assignment_in_conditions(line_stripped, line_num, file_path, line, issues)
            
            # Détecter les erreurs de typographie
            self._detect_typos(line_stripped, line_num, file_path, line, issues)
            
            # Détecter les problèmes de chaînes de caractères
            self._detect_string_issues(line_stripped, line_num, file_path, line, issues)
            
            # Détecter les problèmes de type
            self._detect_type_errors(line_stripped, line_num, file_path, line, issues)
            
            # Détecter les erreurs de logique
            self._detect_logic_errors(line_stripped, line_num, file_path, line, issues)
        
        return issues
    
    def _detect_syntax_errors(self, line_stripped: str, line_num: int, file_path: Path, 
                             line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les erreurs de syntaxe communes"""
        # Parenthèses non fermées dans les structures de contrôle
        if re.search(r'\b(if|for|while|foreach|switch)\s*\([^)]*$', line_stripped):
            issues.append(self._create_issue(
                'error.syntax_parentheses',
                'Parenthèse non fermée dans la structure de contrôle',
                file_path,
                line_num,
                'error',
                'error',
                'Vérifier que toutes les parenthèses sont correctement fermées',
                line.strip()
            ))
        
        # Accolades non ouvertes après structure de contrôle
        if re.search(r'\b(if|for|while|foreach|switch)\s*\([^)]*\)\s*$', line_stripped):
            issues.append(self._create_issue(
                'error.syntax_braces',
                'Structure de contrôle sans accolade ouvrante ou instruction',
                file_path,
                line_num,
                'warning',
                'error',
                'Ajouter une accolade ouvrante { ou une instruction sur la ligne suivante',
                line.strip()
            ))
        
        # Point-virgule manquant
        if (re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^;]*$', line_stripped) and
            not re.search(r'(if|for|while|foreach|switch|function|class|interface|trait)', line_stripped)):
            issues.append(self._create_issue(
                'error.syntax_semicolon',
                'Point-virgule potentiellement manquant à la fin de l\'instruction',
                file_path,
                line_num,
                'warning',
                'error',
                'Ajouter un point-virgule à la fin de l\'instruction',
                line.strip()
            ))
    
    def _detect_null_method_calls(self, line_stripped: str, line_num: int, file_path: Path, 
                                 line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les appels de méthode sur des variables potentiellement null"""
        # Patterns pour détecter les appels sur variables potentiellement null
        null_patterns = [
            (r'\$[a-zA-Z_][a-zA-Z0-9_]*\s*->\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\(', 'Appel de méthode sur variable potentiellement null'),
            (r'\$[a-zA-Z_][a-zA-Z0-9_]*\[.*\]\s*->\s*[a-zA-Z_][a-zA-Z0-9_]*', 'Appel de méthode sur élément de tableau potentiellement null')
        ]
        
        for pattern, description in null_patterns:
            if re.search(pattern, line_stripped):
                # Chercher si il y a une vérification isset/null dans les lignes précédentes
                has_null_check = False
                var_match = re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*', line_stripped)
                if var_match:
                    var_name = var_match.group(0)
                    # Vérifier dans les 5 lignes précédentes
                    for i in range(max(0, line_num - 5), line_num):
                        if i < len(line_stripped) and re.search(rf'isset\s*\(\s*{re.escape(var_name)}\s*\)|{re.escape(var_name)}\s*!==?\s*null|{re.escape(var_name)}\s*!=\s*null', line_stripped):
                            has_null_check = True
                            break
                
                if not has_null_check:
                    issues.append(self._create_issue(
                        'error.null_method_call',
                        description,
                        file_path,
                        line_num,
                        'warning',
                        'error',
                        'Vérifier que la variable n\'est pas null avant l\'appel de méthode avec isset() ou une condition',
                        line.strip()
                    ))
                break
    
    def _detect_uninitialized_variables(self, line_stripped: str, line_num: int, file_path: Path, 
                                      line: str, lines: List[str], issues: List[Dict[str, Any]]) -> None:
        """Détecter les variables potentiellement non initialisées"""
        # Chercher les utilisations de variables dans les conditions
        if re.search(r'\b(if|while|for)\s*\([^)]*\$[a-zA-Z_][a-zA-Z0-9_]*', line_stripped):
            var_matches = re.findall(r'\$[a-zA-Z_][a-zA-Z0-9_]*', line_stripped)
            for var_name in var_matches:
                # Chercher une initialisation dans les lignes précédentes
                initialized = False
                for prev_line_num in range(max(0, line_num - 20), line_num):
                    if prev_line_num < len(lines):
                        prev_line = lines[prev_line_num]
                        if re.search(rf'{re.escape(var_name)}\s*=', prev_line):
                            initialized = True
                            break
                
                if not initialized:
                    issues.append(self._create_issue(
                        'error.uninitialized_variable',
                        f'Variable {var_name} potentiellement non initialisée',
                        file_path,
                        line_num,
                        'warning',
                        'error',
                        f'S\'assurer que {var_name} est initialisée avant utilisation',
                        line.strip()
                    ))
    
    def _detect_function_argument_errors(self, line_stripped: str, line_num: int, file_path: Path, 
                                       line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les erreurs d'arguments de fonction"""
        # Fonctions avec nombre d'arguments fixes (simplifié)
        function_args = {
            'strpos': (2, 3),  # min, max arguments
            'substr': (2, 3),
            'array_slice': (2, 4),
            'preg_match': (2, 5),
            'json_decode': (1, 4),
            'fopen': (2, 4),
            'file_get_contents': (1, 5),
            'mysqli_query': (2, 3)
        }
        
        func_match = re.search(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)', line_stripped)
        if func_match:
            func_name = func_match.group(1)
            args_str = func_match.group(2).strip()
            
            if func_name in function_args:
                # Compter les arguments (approximatif)
                if args_str:
                    args_count = len(re.split(r',(?![^(]*\))', args_str))
                else:
                    args_count = 0
                
                min_args, max_args = function_args[func_name]
                
                if args_count < min_args or args_count > max_args:
                    issues.append(self._create_issue(
                        'error.incorrect_argument_count',
                        f'Fonction {func_name}() : nombre d\'arguments incorrect ({args_count}), attendu: {min_args}-{max_args}',
                        file_path,
                        line_num,
                        'error',
                        'error',
                        f'Vérifier la documentation de {func_name}() et corriger le nombre d\'arguments',
                        line.strip()
                    ))
    
    def _detect_assignment_in_conditions(self, line_stripped: str, line_num: int, file_path: Path, 
                                        line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les affectations dans les conditions"""
        # Détecter = au lieu de == dans les conditions
        condition_patterns = [
            r'\bif\s*\([^)]*\$[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^=]',
            r'\bwhile\s*\([^)]*\$[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^=]',
            r'\belseif\s*\([^)]*\$[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^=]'
        ]
        
        for pattern in condition_patterns:
            if re.search(pattern, line_stripped):
                issues.append(self._create_issue(
                    'error.assignment_in_condition',
                    'Affectation (=) détectée dans une condition, vouliez-vous utiliser == ou === ?',
                    file_path,
                    line_num,
                    'error',
                    'error',
                    'Remplacer = par == pour une comparaison ou === pour une comparaison stricte',
                    line.strip()
                ))
                break
    
    def _detect_typos(self, line_stripped: str, line_num: int, file_path: Path, 
                     line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les erreurs de typographie courantes"""
        common_typos = {
            'echp': 'echo',
            'prnt': 'print',
            'var_dumped': 'var_dump',
            'vardump': 'var_dump',
            'lenght': 'length',
            'widht': 'width',
            'heigh': 'height',
            'retrun': 'return',
            'fucntion': 'function',
            'calss': 'class',
            'pubilc': 'public',
            'privte': 'private',
            'protcted': 'protected'
        }
        
        for typo, correction in common_typos.items():
            if re.search(rf'\b{typo}\b', line_stripped, re.IGNORECASE):
                issues.append(self._create_issue(
                    'error.typo',
                    f'Erreur de typographie: "{typo}"',
                    file_path,
                    line_num,
                    'warning',
                    'error',
                    f'Corriger en: "{correction}"',
                    line.strip()
                ))
                break
    
    def _detect_string_issues(self, line_stripped: str, line_num: int, file_path: Path, 
                             line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les problèmes de chaînes de caractères"""
        # Guillemets non fermés (approximatif)
        single_quote_count = line_stripped.count("'") - line_stripped.count("\\'")
        double_quote_count = line_stripped.count('"') - line_stripped.count('\\"')
        
        if single_quote_count % 2 != 0:
            issues.append(self._create_issue(
                'error.unclosed_quotes',
                'Guillemets simples potentiellement non fermés',
                file_path,
                line_num,
                'error',
                'error',
                'Vérifier que tous les guillemets simples sont correctement fermés',
                line.strip()
            ))
        
        if double_quote_count % 2 != 0:
            issues.append(self._create_issue(
                'error.unclosed_quotes',
                'Guillemets doubles potentiellement non fermés',
                file_path,
                line_num,
                'error',
                'error',
                'Vérifier que tous les guillemets doubles sont correctement fermés',
                line.strip()
            ))
    
    def _detect_type_errors(self, line_stripped: str, line_num: int, file_path: Path, 
                           line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les erreurs de type potentielles"""
        # Opérations mathématiques sur des chaînes
        if re.search(r'["\'][^"\']*["\'][\s]*[\+\-\*\/][\s]*["\'][^"\']*["\']', line_stripped):
            issues.append(self._create_issue(
                'error.string_math_operation',
                'Opération mathématique entre chaînes de caractères',
                file_path,
                line_num,
                'warning',
                'error',
                'Vérifier que les valeurs sont numériques ou utiliser la concaténation (.)',
                line.strip()
            ))
        
        # Comparaison avec des types différents
        type_comparison_patterns = [
            (r'["\'][^"\']*["\'][\s]*===?[\s]*\d+', 'Comparaison chaîne/nombre'),
            (r'\d+[\s]*===?[\s]*["\'][^"\']*["\']', 'Comparaison nombre/chaîne'),
            (r'true[\s]*===?[\s]*\d+', 'Comparaison booléen/nombre'),
            (r'\d+[\s]*===?[\s]*true', 'Comparaison nombre/booléen')
        ]
        
        for pattern, description in type_comparison_patterns:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                issues.append(self._create_issue(
                    'error.type_comparison',
                    f'Comparaison de types différents: {description}',
                    file_path,
                    line_num,
                    'warning',
                    'error',
                    'Vérifier que les types sont compatibles ou utiliser une conversion explicite',
                    line.strip()
                ))
                break
    
    def _detect_logic_errors(self, line_stripped: str, line_num: int, file_path: Path, 
                            line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les erreurs de logique"""
        # Conditions toujours vraies ou fausses
        always_true_patterns = [
            r'\btrue\s*==\s*true\b',
            r'\b1\s*==\s*1\b',
            r'\$[a-zA-Z_][a-zA-Z0-9_]*\s*==\s*\$[a-zA-Z_][a-zA-Z0-9_]*'  # même variable
        ]
        
        for pattern in always_true_patterns:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                issues.append(self._create_issue(
                    'error.always_true_condition',
                    'Condition qui semble toujours vraie',
                    file_path,
                    line_num,
                    'warning',
                    'error',
                    'Vérifier la logique de la condition',
                    line.strip()
                ))
                break
        
        # Return dans une boucle
        if re.search(r'\breturn\b', line_stripped) and re.search(r'(for|foreach|while)', line_stripped):
            issues.append(self._create_issue(
                'error.return_in_loop',
                'Return détecté dans une structure de boucle',
                file_path,
                line_num,
                'info',
                'error',
                'Vérifier si le return est intentionnel ou si une variable de contrôle serait plus appropriée',
                line.strip()
            ))
