"""
Analyseur simplifié pour démarrer
"""

from pathlib import Path
from typing import List, Dict, Any
import time
import re

from .config import Config


class SimpleAnalyzer:
    """Analyseur PHP simplifié"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyser un fichier PHP"""
        start_time = time.time()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = []
            lines = content.split('\n')
            
            # Variables pour analyser les boucles imbriquées
            loop_stack = []
            in_loop = False
            
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Détecter le début d'une boucle
                if re.search(r'\b(for|foreach|while)\s*\(', line_stripped):
                    loop_stack.append(line_num)
                    in_loop = True
                    
                    # Détecter count() dans une boucle for
                    if re.search(r'for\s*\([^;]*;\s*[^;]*count\s*\(', line_stripped):
                        issues.append({
                            'rule_name': 'performance.inefficient_loops',
                            'message': 'Appel de count() dans une condition de boucle for (inefficace)',
                            'file_path': str(file_path),
                            'line': line_num,
                            'column': 0,
                            'severity': 'warning',
                            'issue_type': 'performance',
                            'suggestion': 'Stocker count() dans une variable avant la boucle: $length = count($array); for($i = 0; $i < $length; $i++)',
                            'code_snippet': line.strip()
                        })
                    
                    # Détecter boucles trop imbriquées (plus de 3 niveaux)
                    if len(loop_stack) > 3:
                        issues.append({
                            'rule_name': 'performance.deeply_nested_loops',
                            'message': f'Boucle imbriquée trop profonde (niveau {len(loop_stack)})',
                            'file_path': str(file_path),
                            'line': line_num,
                            'column': 0,
                            'severity': 'warning',
                            'issue_type': 'performance',
                            'suggestion': 'Extraire la logique interne en fonction séparée pour réduire la complexité',
                            'code_snippet': line.strip()
                        })
                
                # Détecter la fin d'une boucle (approximatif)
                if line_stripped == '}' and loop_stack:
                    loop_stack.pop()
                    if not loop_stack:
                        in_loop = False
                
                # Détecter count() ou sizeof() dans le corps d'une boucle
                if (in_loop and loop_stack and 
                    re.search(r'\b(count|sizeof)\s*\(', line_stripped) and
                    not re.search(r'for\s*\(', line_stripped)):  # Éviter double détection
                    issues.append({
                        'rule_name': 'performance.function_in_loop',
                        'message': 'Appel de fonction coûteuse (count/sizeof) dans une boucle',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'warning',
                        'issue_type': 'performance',
                        'suggestion': 'Stocker le résultat dans une variable avant la boucle',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les variables non utilisées (simple - chercher "unused" dans le nom)
                if re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*unused[a-zA-Z0-9_]*\s*=', line):
                    issues.append({
                        'rule_name': 'performance.unused_variables',
                        'message': 'Variable potentiellement non utilisée détectée',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'info',
                        'issue_type': 'performance',
                        'suggestion': 'Vérifier si cette variable est vraiment utilisée',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les requêtes SQL dans les boucles
                if (in_loop and loop_stack and 
                    re.search(r'\b(mysql_query|mysqli_query|query|execute)\s*\(', line_stripped)):
                    issues.append({
                        'rule_name': 'performance.query_in_loop',
                        'message': 'Requête de base de données dans une boucle (problème N+1)',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'performance',
                        'suggestion': 'Extraire la requête hors de la boucle ou utiliser une requête groupée',
                        'code_snippet': line.strip()
                    })
                
                # Détecter SELECT * (inefficace)
                if re.search(r'SELECT\s+\*\s+FROM', line_stripped, re.IGNORECASE):
                    issues.append({
                        'rule_name': 'performance.select_star',
                        'message': 'Utilisation de SELECT * au lieu de colonnes spécifiques',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'warning',
                        'issue_type': 'performance',
                        'suggestion': 'Spécifier uniquement les colonnes nécessaires: SELECT col1, col2 FROM...',
                        'code_snippet': line.strip()
                    })
                
                # Détecter concaténation de chaînes inefficace dans les boucles
                if (in_loop and loop_stack and 
                    re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*\s*\.=\s*', line_stripped)):
                    issues.append({
                        'rule_name': 'performance.string_concatenation_in_loop',
                        'message': 'Concaténation de chaînes dans une boucle (inefficace)',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'warning',
                        'issue_type': 'performance',
                        'suggestion': 'Utiliser un tableau et implode() : $parts[] = $value; puis implode("", $parts)',
                        'code_snippet': line.strip()
                    })
                
                # Détecter array_key_exists() au lieu d'isset()
                if re.search(r'\barray_key_exists\s*\(', line_stripped):
                    issues.append({
                        'rule_name': 'performance.inefficient_array_check',
                        'message': 'array_key_exists() est plus lent qu\'isset() pour les vérifications simples',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'info',
                        'issue_type': 'performance',
                        'suggestion': 'Utiliser isset($array[$key]) au lieu de array_key_exists($key, $array) si null est acceptable',
                        'code_snippet': line.strip()
                    })
                
                # Détecter fopen() répétés
                if re.search(r'\bfopen\s*\(', line_stripped):
                    issues.append({
                        'rule_name': 'performance.file_operations',
                        'message': 'Ouverture de fichier détectée - vérifier si optimisable',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'info',
                        'issue_type': 'performance',
                        'suggestion': 'Éviter d\'ouvrir/fermer des fichiers répétitivement, utiliser file_get_contents() pour les petits fichiers',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les fonctions PHP obsolètes
                obsolete_functions = ['mysql_connect', 'mysql_query', 'ereg', 'split', 'each']
                for func in obsolete_functions:
                    if re.search(rf'\b{func}\s*\(', line_stripped):
                        issues.append({
                            'rule_name': 'performance.obsolete_function',
                            'message': f'Fonction obsolète détectée: {func}()',
                            'file_path': str(file_path),
                            'line': line_num,
                            'column': 0,
                            'severity': 'warning',
                            'issue_type': 'performance',
                            'suggestion': f'Remplacer {func}() par son équivalent moderne (mysqli_, PDO, preg_*, etc.)',
                            'code_snippet': line.strip()
                        })
                
                # Détecter les @ (suppression d'erreurs)
                if '@' in line_stripped and re.search(r'@\s*[a-zA-Z_]', line_stripped):
                    issues.append({
                        'rule_name': 'performance.error_suppression',
                        'message': 'Suppression d\'erreurs avec @ détectée (impact performance)',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'warning',
                        'issue_type': 'performance',
                        'suggestion': 'Gérer les erreurs proprement au lieu d\'utiliser @ qui masque tout',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les requêtes XPath inefficaces
                xpath_patterns = [
                    (r'//\*', 'Sélecteur universel descendant "//*" très lent'),
                    (r'//[^/\s\'"]*\[[^\]]*contains\([^\)]*\)', 'contains() dans un sélecteur descendant est très lent'),
                    (r'//[^/\s\'"]*//[^/\s\'"]*', 'Double descendant "//..//.." extrêmement inefficace'),
                    (r'/descendant::', 'Axe descendant:: explicite très lent'),
                    (r'/following::', 'Axe following:: très coûteux'),
                    (r'/preceding::', 'Axe preceding:: très coûteux'),
                    (r'//\w+\[@\w+\]//\w+', 'Combinaison descendant + attribut + descendant inefficace'),
                    (r'//\w+\[position\(\)\s*[><=]', 'position() dans descendant très lent')
                ]
                
                for pattern, description in xpath_patterns:
                    if re.search(pattern, line_stripped):
                        severity = 'error' if in_loop else 'warning'
                        loop_msg = ' dans une boucle' if in_loop else ''
                        
                        issues.append({
                            'rule_name': 'performance.inefficient_xpath',
                            'message': f'XPath inefficace{loop_msg}: {description}',
                            'file_path': str(file_path),
                            'line': line_num,
                            'column': 0,
                            'severity': severity,
                            'issue_type': 'performance',
                            'suggestion': 'Utiliser des sélecteurs XPath plus spécifiques (ex: /root/element au lieu de //element)',
                            'code_snippet': line.strip()
                        })
                        break  # Une seule détection par ligne
                
                # Détecter les méthodes DOM/XPath potentiellement lentes dans les boucles
                if in_loop and loop_stack:
                    slow_dom_methods = [
                        ('xpath', 'Requête XPath'),
                        ('getElementsByTagName', 'getElementsByTagName()'),
                        ('getElementById', 'getElementById()'),
                        ('querySelector', 'querySelector()'),
                        ('querySelectorAll', 'querySelectorAll()'),
                        ('evaluate', 'XPath evaluate()')
                    ]
                    
                    for method, description in slow_dom_methods:
                        if re.search(rf'\b{method}\s*\(', line_stripped):
                            issues.append({
                                'rule_name': 'performance.dom_query_in_loop',
                                'message': f'{description} dans une boucle peut être très lent',
                                'file_path': str(file_path),
                                'line': line_num,
                                'column': 0,
                                'severity': 'warning',
                                'issue_type': 'performance',
                                'suggestion': f'Extraire {description} hors de la boucle et réutiliser le résultat',
                                'code_snippet': line.strip()
                            })
                            break
                
                # Détecter les regex inefficaces
                inefficient_regex = [
                    (r'preg_match\([\'"][^\'"]*\.\*[^\'"]*[\'"]\s*,', 'Regex avec .* peut être très lente'),
                    (r'preg_match\([\'"][^\'"]*\(\.\*\)[^\'"]*[\'"]\s*,', 'Groupe capturant avec .* inefficace'),
                    (r'preg_match\([\'"][^\'"]*\.\+\.\*[^\'"]*[\'"]\s*,', 'Combinaison .+ et .* problématique'),
                    (r'preg_replace\([\'"][^\'"]*\.\*[^\'"]*[\'"]\s*,', 'preg_replace avec .* peut être très lent')
                ]
                
                for pattern, description in inefficient_regex:
                    if re.search(pattern, line_stripped):
                        severity = 'error' if in_loop else 'warning'
                        issues.append({
                            'rule_name': 'performance.inefficient_regex',
                            'message': f'Regex inefficace: {description}',
                            'file_path': str(file_path),
                            'line': line_num,
                            'column': 0,
                            'severity': severity,
                            'issue_type': 'performance',
                            'suggestion': 'Optimiser la regex en utilisant des quantificateurs plus spécifiques (+, ?, {n,m}) au lieu de .*',
                            'code_snippet': line.strip()
                        })
                        break
            
            # Détecter les calculs répétés (après la boucle principale)
            math_expressions = {}
            for line_num, line in enumerate(lines, 1):
                # Rechercher les expressions mathématiques du type $var = $a * $b + $c
                match = re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*(\$[a-zA-Z_][a-zA-Z0-9_]*\s*[\+\-\*\/]\s*\$[a-zA-Z_][a-zA-Z0-9_]*(?:\s*[\+\-\*\/]\s*\$[a-zA-Z_][a-zA-Z0-9_]*)*)', line)
                if match:
                    expr = match.group(1)
                    expr_clean = re.sub(r'\s+', ' ', expr.strip())
                    if expr_clean not in math_expressions:
                        math_expressions[expr_clean] = []
                    math_expressions[expr_clean].append((line_num, line.strip()))
            
            # Signaler les expressions répétées
            for expr, occurrences in math_expressions.items():
                if len(occurrences) >= 2:  # Au moins 2 occurrences
                    first_line, first_code = occurrences[0]
                    issues.append({
                        'rule_name': 'performance.repeated_calculations',
                        'message': f'Calcul répété détecté: {expr} (trouvé {len(occurrences)} fois)',
                        'file_path': str(file_path),
                        'line': first_line,
                        'column': 0,
                        'severity': 'info',
                        'issue_type': 'performance',
                        'suggestion': f'Stocker le résultat de "{expr}" dans une variable réutilisable',
                        'code_snippet': first_code
                    })
                
                # Détecter les injections SQL
                if re.search(r'mysql_query\s*\(.*\$', line):
                    issues.append({
                        'rule_name': 'security.sql_injection',
                        'message': 'Requête SQL potentiellement vulnérable à l\'injection',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'security',
                        'suggestion': 'Utiliser des requêtes préparées',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les XSS
                if re.search(r'echo\s+\$_(GET|POST)\[', line):
                    issues.append({
                        'rule_name': 'security.xss_vulnerability',
                        'message': 'Sortie de données utilisateur non échappée',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'security',
                        'suggestion': 'Utiliser htmlspecialchars() pour échapper les données',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les lignes trop longues
                if len(line) > 120:
                    issues.append({
                        'rule_name': 'best_practices.psr_compliance',
                        'message': f'Ligne trop longue ({len(line)} caractères)',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 120,
                        'severity': 'info',
                        'issue_type': 'best_practices',
                        'suggestion': 'Limiter les lignes à 120 caractères',
                        'code_snippet': line[:80] + '...' if len(line) > 80 else line
                    })
                
                # Détecter les hachages faibles
                if re.search(r'md5\s*\(.*password', line, re.IGNORECASE):
                    issues.append({
                        'rule_name': 'security.weak_password_hashing',
                        'message': 'Algorithme de hachage faible pour mot de passe',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'security',
                        'suggestion': 'Utiliser password_hash() avec PASSWORD_DEFAULT',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les inclusions dangereuses
                if re.search(r'include.*\$_(GET|POST)\[', line):
                    issues.append({
                        'rule_name': 'security.file_inclusion',
                        'message': 'Inclusion de fichier basée sur données utilisateur',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'security',
                        'suggestion': 'Valider et filtrer le nom du fichier',
                        'code_snippet': line.strip()
                    })
            
            # Analyse post-traitement : détection des oublis de unset()
            self._detect_memory_management_issues(content, file_path, issues)
            
            analysis_time = time.time() - start_time
            
            return {
                'file_path': str(file_path),
                'issues': issues,
                'metrics': {
                    'line_count': len(lines),
                    'file_size': len(content)
                },
                'analysis_time': analysis_time,
                'success': True,
                'error_message': ''
            }
            
        except Exception as e:
            analysis_time = time.time() - start_time
            return {
                'file_path': str(file_path),
                'issues': [],
                'metrics': {},
                'analysis_time': analysis_time,
                'success': False,
                'error_message': str(e)
            }
    
    def _detect_memory_management_issues(self, content: str, file_path: Path, issues: List[Dict[str, Any]]) -> None:
        """Détecter les problèmes de gestion mémoire (oublis de unset())"""
        lines = content.split('\n')
        
        # Patterns pour détecter les gros tableaux
        large_array_patterns = [
            (r'\$(\w+)\s*=\s*range\s*\(\s*\d+\s*,\s*(\d+)\s*\)', 2),  # range(1, 1000000) - groupe 2 = taille
            (r'\$(\w+)\s*=\s*array_fill\s*\(\s*\d+\s*,\s*(\d+)\s*,', 2),  # array_fill(0, 500000, 'data') - groupe 2 = taille
            (r'\$(\w+)\s*=\s*array_fill_keys\s*\(\s*range\s*\(\s*\d+\s*,\s*(\d+)\s*\)', 2),  # array_fill_keys
            (r'\$(\w+)\s*=\s*str_repeat\s*\(\s*[\'"][^\'"]*[\'"]\s*,\s*(\d+)\s*\)', 2),  # str_repeat('x', 100000)
        ]
        
        # Variables contenant potentiellement de gros tableaux/données
        large_variables = set()
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Détecter les déclarations de gros tableaux
            for pattern, size_group in large_array_patterns:
                match = re.search(pattern, line_stripped)
                if match:
                    var_name = match.group(1)  # Nom de variable
                    size = int(match.group(size_group))  # Taille
                    
                    # Considérer comme "gros" si > 10000 éléments
                    if size > 10000:
                        large_variables.add(var_name)
                        
                        # Vérifier si cette variable est libérée avec unset()
                        if not self._is_variable_unset(content, var_name, line_num):
                            issues.append({
                                'rule_name': 'performance.memory_management',
                                'message': f'Gros tableau ${var_name} ({size} éléments) non libéré avec unset()',
                                'file_path': str(file_path),
                                'line': line_num,
                                'column': 0,
                                'severity': 'warning',
                                'issue_type': 'performance',
                                'suggestion': f'Ajouter unset(${var_name}) après utilisation pour libérer la mémoire',
                                'code_snippet': line.strip()
                            })
            
            # Détecter les allocations de gros tableaux avec des boucles
            if re.search(r'for\s*\(\s*\$\w+\s*=\s*0\s*;\s*\$\w+\s*<\s*(\d+)', line_stripped):
                loop_size_match = re.search(r'for\s*\(\s*\$\w+\s*=\s*0\s*;\s*\$\w+\s*<\s*(\d+)', line_stripped)
                if loop_size_match:
                    loop_size = int(loop_size_match.group(1))
                    if loop_size > 10000:
                        # Chercher les variables assignées dans cette boucle
                        for i in range(line_num, min(line_num + 10, len(lines))):
                            if i < len(lines):
                                inner_line = lines[i].strip()
                                if re.search(r'\$\w+\[\s*\$\w+\s*\]\s*=', inner_line):
                                    var_match = re.search(r'\$(\w+)\[', inner_line)
                                    if var_match:
                                        var_name = var_match.group(1)
                                        large_variables.add(var_name)
                                        
                                        if not self._is_variable_unset(content, var_name, i + 1):
                                            issues.append({
                                                'rule_name': 'performance.memory_management',
                                                'message': f'Tableau ${var_name} rempli dans une boucle ({loop_size} itérations) non libéré',
                                                'file_path': str(file_path),
                                                'line': i + 1,
                                                'column': 0,
                                                'severity': 'warning',
                                                'issue_type': 'performance',
                                                'suggestion': f'Ajouter unset(${var_name}) après utilisation',
                                                'code_snippet': inner_line
                                            })
                                    break
    
    def _is_variable_unset(self, content: str, var_name: str, after_line: int) -> bool:
        """
        Vérifier si une variable est libérée avec unset() après sa déclaration.
        
        Args:
            content: Le contenu du fichier PHP
            var_name: Le nom de la variable à rechercher (sans le $)
            after_line: La ligne après laquelle commencer la recherche (0-indexed)
            
        Returns:
            True si un unset() de cette variable est trouvé dans la portée actuelle
        """
        lines = content.split('\n')
        
        # Calculer le niveau d'accolades initial pour déterminer la portée
        initial_brace_level = self._calculate_brace_level(lines, after_line - 1)
        
        # Chercher unset() dans les lignes suivantes
        for i in range(after_line, len(lines)):
            line = lines[i].strip()
            
            # Ignorer les lignes vides et les commentaires
            if not line or line.startswith('//') or line.startswith('#') or line.startswith('/*'):
                continue
            
            # Vérifier si la variable est dans un unset()
            # Patterns acceptés: unset($var), unset($var, $other), unset($array[$var])
            unset_patterns = [
                rf'unset\s*\(\s*\${var_name}\b',  # unset($var)
                rf'unset\s*\([^)]*,\s*\${var_name}\b',  # unset($other, $var)
                rf'unset\s*\(\s*\${var_name}\s*,',  # unset($var, $other)
            ]
            
            for pattern in unset_patterns:
                if re.search(pattern, line):
                    return True
            
            # Calculer le niveau d'accolades actuel
            current_brace_level = self._calculate_brace_level(lines, i)
            
            # Si on sort de la portée initiale (niveau d'accolades plus bas), arrêter
            if current_brace_level < initial_brace_level:
                break
            
            # Arrêter à la fin d'une fonction ou classe
            if re.search(r'^\s*}\s*$', line) and current_brace_level <= initial_brace_level:
                # Vérifier si c'est vraiment la fin d'une fonction/classe
                if self._is_end_of_function_or_class(lines, i, initial_brace_level):
                    break
        
        return False
    
    def _calculate_brace_level(self, lines: List[str], line_index: int) -> int:
        """
        Calculer le niveau d'imbrication des accolades jusqu'à une ligne donnée.
        
        Args:
            lines: Liste des lignes du fichier
            line_index: Index de la ligne (0-based)
            
        Returns:
            Le niveau d'accolades (nombre d'accolades ouvrantes - fermantes)
        """
        brace_count = 0
        
        for i in range(min(line_index + 1, len(lines))):
            line = lines[i]
            
            # Ignorer les accolades dans les chaînes de caractères et commentaires
            line_clean = self._remove_strings_and_comments(line)
            
            # Compter les accolades
            brace_count += line_clean.count('{') - line_clean.count('}')
        
        return brace_count
    
    def _remove_strings_and_comments(self, line: str) -> str:
        """
        Supprimer les chaînes de caractères et commentaires d'une ligne pour éviter
        de compter les accolades qui ne sont pas du code.
        """
        # Supprimer les commentaires de ligne
        line = re.sub(r'//.*$', '', line)
        line = re.sub(r'#.*$', '', line)
        
        # Supprimer les chaînes entre guillemets simples et doubles
        # (version simplifiée, ne gère pas les échappements complexes)
        line = re.sub(r"'[^']*'", '', line)
        line = re.sub(r'"[^"]*"', '', line)
        
        return line
    
    def _is_end_of_function_or_class(self, lines: List[str], line_index: int, initial_brace_level: int) -> bool:
        """
        Déterminer si une accolade fermante marque la fin d'une fonction ou classe.
        
        Args:
            lines: Liste des lignes du fichier
            line_index: Index de la ligne avec l'accolade fermante
            initial_brace_level: Niveau d'accolades initial
            
        Returns:
            True si c'est la fin d'une fonction ou classe
        """
        # Chercher en arrière pour trouver la déclaration de fonction/classe correspondante
        brace_count = 1  # On part de 1 car on a trouvé une accolade fermante
        
        for i in range(line_index - 1, -1, -1):
            line = lines[i].strip()
            line_clean = self._remove_strings_and_comments(line)
            
            # Ajuster le compteur d'accolades
            brace_count += line_clean.count('}') - line_clean.count('{')
            
            # Si on équilibre les accolades, on a trouvé le début du bloc
            if brace_count == 0:
                # Vérifier si cette ligne ou les précédentes contiennent une déclaration de fonction/classe
                for j in range(max(0, i - 3), i + 1):
                    check_line = lines[j].strip()
                    if re.search(r'\b(function|class|interface|trait)\s+', check_line):
                        return True
                break
        
        return False
