"""
Analyseur spécialisé pour les boucles et leur performance
"""

import re
from pathlib import Path
from typing import List, Dict, Any

from .base_analyzer import BaseAnalyzer


class LoopAnalyzer(BaseAnalyzer):
    """Analyseur spécialisé pour les problèmes liés aux boucles"""
    
    def analyze(self, content: str, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """Analyser les problèmes de boucles dans le code PHP"""
        issues = []
        
        # Variables pour analyser les boucles imbriquées
        loop_stack = []
        in_loop = False
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Ignorer les commentaires et directives Blade
            if self._is_comment_line(line) or self._is_blade_directive(line):
                continue
            
            # Détecter le début d'une boucle
            if re.search(r'\b(for|foreach|while)\s*\(', line_stripped):
                loop_stack.append(line_num)
                in_loop = True
                
                # Détecter foreach sur non-itérable
                self._detect_foreach_non_iterable(line_stripped, line_num, file_path, lines, issues)
                
                # Détecter count() dans une boucle for
                self._detect_count_in_for_loop(line_stripped, line_num, file_path, line, issues)
                
                # Détecter boucles trop imbriquées (plus de 3 niveaux)
                self._detect_deeply_nested_loops(loop_stack, line_num, file_path, line, issues)
            
            # Détecter la fin d'une boucle (approximatif)
            if line_stripped == '}' and loop_stack:
                loop_stack.pop()
                if not loop_stack:
                    in_loop = False
            
            # Analyses pour le contenu des boucles
            if in_loop and loop_stack:
                # Détecter count() ou sizeof() dans le corps d'une boucle
                self._detect_expensive_functions_in_loop(line_stripped, line_num, file_path, line, issues)
                
                # Détecter les requêtes SQL dans les boucles
                self._detect_queries_in_loop(line_stripped, line_num, file_path, line, issues)
                
                # Détecter les fonctions lourdes dans les boucles
                self._detect_heavy_functions_in_loop(line_stripped, line_num, file_path, line, issues)
                
                # Détecter création répétée d'objets dans les boucles
                self._detect_object_creation_in_loop(line_stripped, line_num, file_path, line, issues)
                
                # Détecter les problèmes de complexité algorithmique
                self._detect_algorithmic_complexity_issues(line_stripped, line_num, file_path, line, issues, loop_stack)
                
                # Détecter boucles imbriquées avec même tableau
                self._detect_nested_loops_same_array(line_stripped, line_num, file_path, line, lines, loop_stack, issues)
        
        return issues
    
    def _detect_foreach_non_iterable(self, line_stripped: str, line_num: int, file_path: Path, 
                                   lines: List[str], issues: List[Dict[str, Any]]) -> None:
        """Détecter foreach sur une variable non-itérable"""
        foreach_match = re.search(r'foreach\s*\(\s*\$([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s+', line_stripped)
        if foreach_match:
            var_name = foreach_match.group(1)
            # Chercher dans les lignes précédentes si cette variable a été assignée à un scalaire
            for prev_line_num in range(max(0, line_num - 20), line_num):
                if prev_line_num < len(lines):
                    prev_line = lines[prev_line_num].strip()
                    # Détecter assignation à un scalaire (nombre, chaîne, booléen, null)
                    scalar_pattern = rf'\${var_name}\s*=\s*(?:true|false|null|\d+(?:\.\d+)?|["\'][^"\']*["\'])\s*;'
                    if re.search(scalar_pattern, prev_line, re.IGNORECASE):
                        issues.append(self._create_issue(
                            'error.foreach_non_iterable',
                            f'foreach on non-iterable variable ${var_name} (assigned to scalar value)',
                            file_path,
                            line_num,
                            'error',
                            'error',
                            f'Ensure ${var_name} is an array or iterable object before using foreach',
                            lines[line_num - 1].strip()
                        ))
                        break
    
    def _detect_count_in_for_loop(self, line_stripped: str, line_num: int, file_path: Path, 
                                 line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter count() dans une condition de boucle for"""
        if re.search(r'for\s*\([^;]*;\s*[^;]*count\s*\(', line_stripped):
            issues.append(self._create_issue(
                'performance.inefficient_loops',
                'Appel de count() dans une condition de boucle for (inefficace)',
                file_path,
                line_num,
                'warning',
                'performance',
                'Stocker count() dans une variable avant la boucle: $length = count($array); for($i = 0; $i < $length; $i++)',
                line.strip()
            ))
    
    def _detect_deeply_nested_loops(self, loop_stack: List[int], line_num: int, file_path: Path, 
                                  line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les boucles trop imbriquées"""
        if len(loop_stack) > 3:
            issues.append(self._create_issue(
                'performance.deeply_nested_loops',
                f'Boucle imbriquée trop profonde (niveau {len(loop_stack)})',
                file_path,
                line_num,
                'warning',
                'performance',
                'Extraire la logique interne en fonction séparée pour réduire la complexité',
                line.strip()
            ))
    
    def _detect_expensive_functions_in_loop(self, line_stripped: str, line_num: int, file_path: Path, 
                                          line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les fonctions coûteuses dans les boucles"""
        if (re.search(r'\b(count|sizeof)\s*\(', line_stripped) and
            not re.search(r'for\s*\(', line_stripped)):  # Éviter double détection
            issues.append(self._create_issue(
                'performance.function_in_loop',
                'Appel de fonction coûteuse (count/sizeof) dans une boucle',
                file_path,
                line_num,
                'warning',
                'performance',
                'Stocker le résultat dans une variable avant la boucle',
                line.strip()
            ))
    
    def _detect_queries_in_loop(self, line_stripped: str, line_num: int, file_path: Path, 
                               line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les requêtes SQL dans les boucles"""
        if re.search(r'\b(mysql_query|mysqli_query|query|execute)\s*\(', line_stripped):
            issues.append(self._create_issue(
                'performance.query_in_loop',
                'Requête de base de données dans une boucle (problème N+1)',
                file_path,
                line_num,
                'error',
                'performance',
                'Extraire la requête hors de la boucle ou utiliser une requête groupée',
                line.strip()
            ))
    
    def _detect_heavy_functions_in_loop(self, line_stripped: str, line_num: int, file_path: Path, 
                                      line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter les fonctions lourdes dans les boucles"""
        heavy_functions = [
            ('file_get_contents', 'Lecture de fichier'),
            ('file_put_contents', 'Écriture de fichier'),
            ('glob', 'Recherche de fichiers'),
            ('scandir', 'Lecture de répertoire'),
            ('opendir', 'Ouverture de répertoire'),
            ('readdir', 'Lecture de répertoire'),
            ('curl_exec', 'Requête HTTP/cURL'),
            ('file_exists', 'Vérification d\'existence de fichier'),
            ('is_file', 'Vérification de type de fichier'),
            ('is_dir', 'Vérification de répertoire'),
            ('filemtime', 'Lecture de métadonnées de fichier'),
            ('filesize', 'Lecture de taille de fichier'),
            ('pathinfo', 'Analyse de chemin'),
            ('realpath', 'Résolution de chemin'),
            ('basename', 'Extraction de nom de fichier'),
            ('dirname', 'Extraction de répertoire')
        ]
        
        for func, description in heavy_functions:
            if re.search(rf'\b{func}\s*\(', line_stripped):
                issues.append(self._create_issue(
                    'performance.heavy_function_in_loop',
                    f'{description} dans une boucle peut être très lent',
                    file_path,
                    line_num,
                    'warning',
                    'performance',
                    f'Extraire {func}() hors de la boucle et mettre en cache le résultat',
                    line.strip()
                ))
                break
    
    def _detect_object_creation_in_loop(self, line_stripped: str, line_num: int, file_path: Path, 
                                      line: str, issues: List[Dict[str, Any]]) -> None:
        """Détecter la création répétée d'objets dans les boucles"""
        object_patterns = [
            (r'\$\w+\s*=\s*new\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)\s*;', 'new {class}({args})'),
            (r'\$\w+\s*=\s*([A-Za-z_][A-ZaZ0-9_]*)::\s*getInstance\s*\(\s*\)\s*;', '{class}::getInstance()'),
            (r'\$\w+\s*=\s*([A-Za-z_][A-ZaZ0-9_]*)::\s*create\s*\(([^)]*)\)\s*;', '{class}::create({args})'),
            (r'\$\w+\s*=\s*(DateTime|DateTimeImmutable)\s*\(\s*["\'][^"\']*["\']\s*\)\s*;', 'new {class}()'),
            (r'\$\w+\s*=\s*json_decode\s*\(\s*["\'][^"\']*["\']\s*\)\s*;', 'json_decode()'),
            (r'\$\w+\s*=\s*simplexml_load_string\s*\(\s*["\'][^"\']*["\']\s*\)\s*;', 'simplexml_load_string()'),
            (r'\$\w+\s*=\s*DOMDocument\s*\(\s*\)\s*;', 'new DOMDocument()'),
            (r'\$\w+\s*=\s*PDO\s*\(\s*[^)]+\)\s*;', 'new PDO()'),
        ]
        
        for pattern, description in object_patterns:
            match = re.search(pattern, line_stripped)
            if match:
                class_name = match.group(1) if match.groups() else 'Object'
                args = match.group(2) if len(match.groups()) > 1 else ''
                
                # Vérifier si les arguments sont constants (pas de variables)
                if not re.search(r'\$[a-zA-Z_]', args):  # Pas de variables dans les arguments
                    issues.append(self._create_issue(
                        'performance.object_creation_in_loop',
                        f'Création répétée d\'objet {class_name} dans une boucle avec arguments constants',
                        file_path,
                        line_num,
                        'warning',
                        'performance',
                        f'Extraire la création de {class_name} hors de la boucle et réutiliser l\'instance',
                        line.strip()
                    ))
                    break
    
    def _detect_algorithmic_complexity_issues(self, line_stripped: str, line_num: int, file_path: Path, 
                                            line: str, issues: List[Dict[str, Any]], loop_stack: List[int]) -> None:
        """Détecter les problèmes de complexité algorithmique"""
        # Détecter les tris dans les boucles
        sort_functions = ['sort', 'rsort', 'asort', 'arsort', 'ksort', 'krsort', 'usort', 'uasort', 'uksort', 'array_multisort']
        for sort_func in sort_functions:
            if re.search(rf'\b{sort_func}\s*\(', line_stripped):
                issues.append(self._create_issue(
                    'performance.sort_in_loop',
                    f'Fonction de tri {sort_func}() dans une boucle - complexité O(n²log n) ou pire',
                    file_path,
                    line_num,
                    'warning',
                    'performance',
                    f'Extraire le tri {sort_func}() hors de la boucle pour améliorer les performances',
                    line.strip()
                ))
                break
        
        # Détecter recherche linéaire dans boucle
        search_functions = ['in_array', 'array_search', 'array_key_exists']
        for search_func in search_functions:
            if re.search(rf'\b{search_func}\s*\(', line_stripped):
                issues.append(self._create_issue(
                    'performance.linear_search_in_loop',
                    f'Recherche linéaire {search_func}() dans une boucle - complexité O(n²)',
                    file_path,
                    line_num,
                    'warning',
                    'performance',
                    f'Convertir le tableau en clé-valeur ou utiliser array_flip() avant la boucle pour une recherche O(1)',
                    line.strip()
                ))
                break
    
    def _detect_nested_loops_same_array(self, line_stripped: str, line_num: int, file_path: Path, 
                                      line: str, lines: List[str], loop_stack: List[int], 
                                      issues: List[Dict[str, Any]]) -> None:
        """Détecter les boucles imbriquées sur le même tableau"""
        if len(loop_stack) >= 2:
            foreach_match = re.search(r'foreach\s*\(\s*\$([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s+', line_stripped)
            if foreach_match:
                current_array = foreach_match.group(1)
                # Chercher dans les lignes précédentes pour voir si le même tableau est utilisé
                for prev_line_num in range(max(0, line_num - 10), line_num):
                    if prev_line_num < len(lines):
                        prev_line = lines[prev_line_num].strip()
                        prev_match = re.search(r'foreach\s*\(\s*\$([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s+', prev_line)
                        if prev_match and prev_match.group(1) == current_array:
                            issues.append(self._create_issue(
                                'performance.nested_loop_same_array',
                                f'Boucles imbriquées sur le même tableau ${current_array} - complexité O(n²)',
                                file_path,
                                line_num,
                                'warning',
                                'performance',
                                'Revoir l\'algorithme pour éviter le parcours quadratique du même tableau',
                                line.strip()
                            ))
                            break
