"""
Analyseur spécialisé pour les problèmes de performance
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Tuple


from .base_analyzer import BaseAnalyzer
from ..rules.performance import ConstantPropagationRule


class PerformanceAnalyzer(BaseAnalyzer):
    """Analyseur spécialisé pour les problèmes de performance"""
    
    def analyze(self, content: str, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """Analyser les problèmes de performance dans le code PHP"""
        issues = []
        # Exécuter les règles dynamiques (dont propagation de constantes)
        config = self.config
        # On instancie la règle avec la config globale
        const_rule = ConstantPropagationRule(config)
        parse_result = {'content': content, 'lines': lines, 'file_path': str(file_path)}
        try:
            const_issues = const_rule.analyze(parse_result)
            for issue in const_issues:
                # Ajouter le chemin du fichier si absent
                if not issue.get('file_path'):
                    issue['file_path'] = str(file_path)
                issues.append(issue)
        except Exception as e:
            issues.append({
                'rule_name': 'performance.constant_propagation',
                'message': f'Erreur lors de la propagation de constantes: {e}',
                'file_path': str(file_path),
                'line': 0,
                'column': 0,
                'severity': 'error',
                'issue_type': 'performance',
                'suggestion': '',
                'code_snippet': ''
            })
        
        # Détecter les calculs répétés
        self._detect_repeated_calculations(lines, file_path, issues)
        
        # Analyser ligne par ligne
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Ignorer les commentaires et directives Blade
            if self._is_comment_line(line) or self._is_blade_directive(line):
                continue
            
            # Détecter les variables non utilisées
            self._detect_unused_variables(line_stripped, line_num, file_path, line, issues)
            
            # Détecter les fonctions coûteuses utilisées inutilement
            self._detect_expensive_function_calls(line_stripped, line_num, file_path, line, issues)
            
            # Détecter les opérations inefficaces sur les tableaux
            self._detect_inefficient_array_operations(line_stripped, line_num, file_path, line, issues)
            
            # Détecter les problèmes de chaînes de caractères
            self._detect_string_performance_issues(line_stripped, line_num, file_path, line, issues)
            
            # Détecter les problèmes de régularité d'expressions
            self._detect_regex_performance_issues(line_stripped, line_num, file_path, line, issues)
            
            # Détecter les problèmes d'I/O
            self._detect_io_performance_issues(line_stripped, line_num, file_path, line, issues)
        
        return issues
    
    def _detect_repeated_calculations(self, lines: List[str], file_path: Path, 
                                    issues: List[Dict[str, Any]]) -> None:
        """Détecter les calculs répétés dans le même contexte"""
        math_expressions = {}
        
        for line_num, line in enumerate(lines, 1):
            # Rechercher les expressions mathématiques du type $var = $a * $b + $c
            match = re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*(\$[a-zA-Z_][a-zA-Z0-9_]*\s*[\+\-\*\/]\s*\$[a-zA-Z_][a-zA-Z0-9_]*(?:\s*[\+\-\*\/]\s*\$[a-zA-Z_][a-zA-Z0-9_]*)*)', line)
            if match:
                expr = match.group(1)
                expr_clean = re.sub(r'\s+', ' ', expr.strip())
                
                # Ignorer les expressions contenant $this (référence d'objet)
                if '$this' in expr_clean:
                    continue
                
                # Ignorer les expressions trop simples
                if not re.search(r'[\+\-\*\/]', expr_clean):
                    continue
                
                if expr_clean not in math_expressions:
                    math_expressions[expr_clean] = []
                math_expressions[expr_clean].append((line_num, line.strip()))
        
        # Signaler les expressions répétées
        for expr, occurrences in math_expressions.items():
            if len(occurrences) >= 2:
                first_line, first_code = occurrences[0]
                issues.append(self._create_issue(
                    'performance.repeated_calculations',
                    f'Calcul répété détecté: {expr} (trouvé {len(occurrences)} fois)',
                    file_path,
                    first_line,
                    'info',
                    'performance',
                    f'Stocker le résultat de "{expr}" dans une variable réutilisable',
                    first_code
                ))
    
    def _detect_unused_variables(self, line_stripped: str, line_num: int, file_path: Path, 
                                line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les variables potentiellement non utilisées"""
        # Simple détection basée sur le nom (contient "unused" ou similaire)
        unused_patterns = [
            r'\$[a-zA-Z_][a-zA-Z0-9_]*unused[a-zA-Z0-9_]*\s*=',
            r'\$unused[a-zA-Z_][a-zA-Z0-9_]*\s*=',
            r'\$temp[0-9]*\s*=.*(?!temp)',  # variables temp non réutilisées
            r'\$dummy[a-zA-Z0-9_]*\s*='
        ]
        
        for pattern in unused_patterns:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                var_match = re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*', line_stripped)
                if var_match:
                    var_name = var_match.group(0)
                    issues.append(self._create_issue(
                        'performance.unused_variables',
                        f'Variable potentiellement non utilisée: {var_name}',
                        file_path,
                        line_num,
                        'info',
                        'performance',
                        f'Supprimer {var_name} si elle n\'est pas utilisée',
                        line.strip()
                    ))
                break
    
    def _detect_expensive_function_calls(self, line_stripped: str, line_num: int, file_path: Path, 
                                       line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les appels de fonctions coûteuses qui pourraient être optimisés"""
        expensive_functions = [
            ('array_unique', 'array_flip puis array_keys peut être plus rapide'),
            ('array_intersect', 'Considérer array_intersect_key si approprié'),
            ('array_diff', 'Considérer array_diff_key si approprié'),
            ('in_array.*true', 'Utiliser array_key_exists ou array_flip pour de gros tableaux'),
            ('preg_match.*\\.\\*', 'Expression régulière avec .* peut être lente'),
            ('file_get_contents.*http', 'Considérer cURL avec timeout pour les URL HTTP'),
            ('glob', 'Considérer opendir/readdir pour de gros répertoires'),
            ('scandir', 'Filtrer les résultats tôt si possible')
        ]
        
        for func_pattern, suggestion in expensive_functions:
            if re.search(rf'\b{func_pattern}\s*\(', line_stripped, re.IGNORECASE):
                func_name = func_pattern.split('\\.*')[0].split('\\.')[0]  # Nettoyer le nom
                issues.append(self._create_issue(
                    'performance.expensive_function',
                    f'Fonction potentiellement coûteuse: {func_name}()',
                    file_path,
                    line_num,
                    'info',
                    'performance',
                    suggestion,
                    line.strip()
                ))
                break
    
    def _detect_inefficient_array_operations(self, line_stripped: str, line_num: int, file_path: Path, 
                                           line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les opérations inefficaces sur les tableaux"""
        # array_push vs affectation directe
        if re.search(r'array_push\s*\(\s*\$[a-zA-Z_][a-zA-Z0-9_]*\s*,\s*[^,)]+\s*\)', line_stripped):
            issues.append(self._create_issue(
                'performance.array_push_single',
                'array_push() avec un seul élément est moins efficace que l\'affectation directe',
                file_path,
                line_num,
                'info',
                'performance',
                'Utiliser $array[] = $value au lieu de array_push($array, $value)',
                line.strip()
            ))
        
        # Utilisation de count() dans des conditions multiples
        if re.search(r'count\s*\([^)]+\)\s*[><=!]+\s*\d+', line_stripped):
            if re.search(r'count\s*\([^)]+\)\s*>\s*0', line_stripped):
                issues.append(self._create_issue(
                    'performance.count_vs_empty',
                    'count($array) > 0 est moins efficace que !empty($array)',
                    file_path,
                    line_num,
                    'info',
                    'performance',
                    'Utiliser !empty($array) au lieu de count($array) > 0',
                    line.strip()
                ))
        
        # Concatenation de tableaux inefficace
        if re.search(r'array_merge\s*\([^)]*\$[a-zA-Z_][a-zA-Z0-9_]*\s*,\s*array\s*\([^)]*\)\s*\)', line_stripped):
            issues.append(self._create_issue(
                'performance.array_merge_single',
                'array_merge() avec un petit tableau peut être inefficace',
                file_path,
                line_num,
                'info',
                'performance',
                'Considérer l\'opérateur + ou array_push() pour de meilleures performances',
                line.strip()
            ))
    
    def _detect_string_performance_issues(self, line_stripped: str, line_num: int, file_path: Path, 
                                        line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les problèmes de performance liés aux chaînes"""
        # Concaténation de chaînes en boucle (approximatif)
        if re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*\s*\.=', line_stripped):
            issues.append(self._create_issue(
                'performance.string_concatenation',
                'Concaténation de chaînes (.=) peut être inefficace en boucle',
                file_path,
                line_num,
                'info',
                'performance',
                'Considérer utiliser un tableau et implode() pour de nombreuses concaténations',
                line.strip()
            ))
        
        # substr vs array access
        if re.search(r'substr\s*\([^,]+,\s*0\s*,\s*1\s*\)', line_stripped):
            issues.append(self._create_issue(
                'performance.substr_first_char',
                'substr($str, 0, 1) est moins efficace que $str[0]',
                file_path,
                line_num,
                'info',
                'performance',
                'Utiliser $str[0] pour récupérer le premier caractère',
                line.strip()
            ))
        
        # strlen dans les conditions
        if re.search(r'strlen\s*\([^)]+\)\s*[><=!]+\s*0', line_stripped):
            issues.append(self._create_issue(
                'performance.strlen_vs_empty',
                'strlen() pour vérifier si une chaîne est vide est moins efficace',
                file_path,
                line_num,
                'info',
                'performance',
                'Utiliser empty($str) ou $str === \'\' pour vérifier si une chaîne est vide',
                line.strip()
            ))
    
    def _detect_regex_performance_issues(self, line_stripped: str, line_num: int, file_path: Path, 
                                       line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les problèmes de performance avec les expressions régulières"""
        # Regex avec quantificateurs gourmands
        regex_patterns_to_check = [
            (r'preg_match\s*\([^)]*\.\*\.\*', 'Expression régulière avec .*.* peut être très lente'),
            (r'preg_match\s*\([^)]*\.\+\.\+', 'Expression régulière avec .+.+ peut être très lente'),
            (r'preg_replace\s*\([^)]*\.\*', 'preg_replace avec .* peut être inefficace'),
            (r'preg_match_all\s*\([^)]*\.\*', 'preg_match_all avec .* peut consommer beaucoup de mémoire')
        ]
        
        for pattern, message in regex_patterns_to_check:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                issues.append(self._create_issue(
                    'performance.regex_performance',
                    message,
                    file_path,
                    line_num,
                    'warning',
                    'performance',
                    'Optimiser l\'expression régulière ou utiliser des fonctions de chaînes plus simples',
                    line.strip()
                ))
                break
        
        # Utilisation de regex pour des opérations simples
        simple_operations = [
            (r'preg_match\s*\([\'"][^\'"\[\]{}()*+?.\\|^$]*[\'"]', 'Expression régulière simple'),
            (r'preg_replace\s*\([\'"][^\'"\[\]{}()*+?.\\|^$]*[\'"].*[\'"][^\'"\[\]{}()*+?.\\|^$]*[\'"]', 'Remplacement simple')
        ]
        
        for pattern, description in simple_operations:
            if re.search(pattern, line_stripped):
                issues.append(self._create_issue(
                    'performance.regex_overkill',
                    f'{description} - regex peut être excessive',
                    file_path,
                    line_num,
                    'info',
                    'performance',
                    'Considérer str_replace(), strpos(), ou substr() pour des opérations de chaînes simples',
                    line.strip()
                ))
                break
    
    def _detect_io_performance_issues(self, line_stripped: str, line_num: int, file_path: Path, 
                                    line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les problèmes de performance liés aux I/O"""
        # Lecture de fichier ligne par ligne inefficace
        if re.search(r'fgets\s*\(.*fopen\s*\(', line_stripped):
            issues.append(self._create_issue(
                'performance.inefficient_file_reading',
                'Lecture de fichier ligne par ligne avec fopen/fgets peut être inefficace',
                file_path,
                line_num,
                'info',
                'performance',
                'Considérer file() ou file_get_contents() pour les petits fichiers',
                line.strip()
            ))
        
        # Vérifications d'existence de fichier répétées
        file_check_functions = ['file_exists', 'is_file', 'is_dir', 'is_readable', 'is_writable']
        for func in file_check_functions:
            if re.search(rf'\b{func}\s*\([^)]*\$[a-zA-Z_][a-zA-Z0-9_]*\)', line_stripped):
                issues.append(self._create_issue(
                    'performance.repeated_file_checks',
                    f'Vérification de fichier {func}() - considérer la mise en cache si répétée',
                    file_path,
                    line_num,
                    'info',
                    'performance',
                    f'Mettre en cache le résultat de {func}() si appelé plusieurs fois',
                    line.strip()
                ))
                break
        
        # Opérations de base de données sans préparation
        if re.search(r'mysql_query\s*\(.*\$', line_stripped):
            issues.append(self._create_issue(
                'performance.unprepared_query',
                'Requête SQL non préparée - peut être inefficace et dangereuse',
                file_path,
                line_num,
                'warning',
                'performance',
                'Utiliser des requêtes préparées pour de meilleures performances et sécurité',
                line.strip()
            ))
