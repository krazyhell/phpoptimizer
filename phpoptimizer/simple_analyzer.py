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
                    
                    # Détecter foreach sur non-itérable
                    foreach_match = re.search(r'foreach\s*\(\s*\$([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s+', line_stripped)
                    if foreach_match:
                        var_name = foreach_match.group(1)
                        # Chercher dans les lignes précédentes si cette variable a été assignée à un scalaire
                        for prev_line_num in range(max(0, line_num - 20), line_num):  # Chercher dans les 20 lignes précédentes
                            if prev_line_num < len(lines):
                                prev_line = lines[prev_line_num].strip()
                                # Détecter assignation à un scalaire (nombre, chaîne, booléen, null)
                                scalar_pattern = rf'\${var_name}\s*=\s*(?:true|false|null|\d+(?:\.\d+)?|["\'][^"\']*["\'])\s*;'
                                if re.search(scalar_pattern, prev_line, re.IGNORECASE):
                                    issues.append({
                                        'rule_name': 'error.foreach_non_iterable',
                                        'message': f'foreach on non-iterable variable ${var_name} (assigned to scalar value)',
                                        'file_path': str(file_path),
                                        'line': line_num,
                                        'column': 0,
                                        'severity': 'error',
                                        'issue_type': 'error',
                                        'suggestion': f'Ensure ${var_name} is an array or iterable object before using foreach',
                                        'code_snippet': line.strip()
                                    })
                                    break
                    
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
                
                # Détecter les fonctions lourdes dans les boucles
                if in_loop and loop_stack:
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
                            issues.append({
                                'rule_name': 'performance.heavy_function_in_loop',
                                'message': f'{description} dans une boucle peut être très lent',
                                'file_path': str(file_path),
                                'line': line_num,
                                'column': 0,
                                'severity': 'warning',
                                'issue_type': 'performance',
                                'suggestion': f'Extraire {func}() hors de la boucle et mettre en cache le résultat',
                                'code_snippet': line.strip()
                            })
                            break
                
                # Détecter création répétée d'objets dans les boucles
                if in_loop and loop_stack:
                    # Patterns d'instanciation d'objets
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
                                issues.append({
                                    'rule_name': 'performance.object_creation_in_loop',
                                    'message': f'Création répétée d\'objet {class_name} dans une boucle avec arguments constants',
                                    'file_path': str(file_path),
                                    'line': line_num,
                                    'column': 0,
                                    'severity': 'warning',
                                    'issue_type': 'performance',
                                    'suggestion': f'Extraire la création de {class_name} hors de la boucle et réutiliser l\'instance',
                                    'code_snippet': line.strip()
                                })
                                break
                
                # Détecter les problèmes de complexité algorithmique
                if in_loop and loop_stack:
                    # Détecter les tris dans les boucles (sort, usort, asort, etc.)
                    sort_functions = ['sort', 'rsort', 'asort', 'arsort', 'ksort', 'krsort', 'usort', 'uasort', 'uksort', 'array_multisort']
                    for sort_func in sort_functions:
                        if re.search(rf'\b{sort_func}\s*\(', line_stripped):
                            issues.append({
                                'rule_name': 'performance.sort_in_loop',
                                'message': f'Fonction de tri {sort_func}() dans une boucle - complexité O(n²log n) ou pire',
                                'file_path': str(file_path),
                                'line': line_num,
                                'column': 0,
                                'severity': 'warning',
                                'issue_type': 'performance',
                                'suggestion': f'Extraire le tri {sort_func}() hors de la boucle pour améliorer les performances',
                                'code_snippet': line.strip()
                            })
                            break
                    
                    # Détecter recherche linéaire dans boucle (in_array, array_search)
                    search_functions = ['in_array', 'array_search', 'array_key_exists']
                    for search_func in search_functions:
                        if re.search(rf'\b{search_func}\s*\(', line_stripped):
                            issues.append({
                                'rule_name': 'performance.linear_search_in_loop',
                                'message': f'Recherche linéaire {search_func}() dans une boucle - complexité O(n²)',
                                'file_path': str(file_path),
                                'line': line_num,
                                'column': 0,
                                'severity': 'warning',
                                'issue_type': 'performance',
                                'suggestion': f'Convertir le tableau en clé-valeur ou utiliser array_flip() avant la boucle pour une recherche O(1)',
                                'code_snippet': line.strip()
                            })
                            break
                    
                    # Détecter boucles imbriquées avec même tableau (parcours O(n²) potentiel)
                    if len(loop_stack) >= 2:
                        # Chercher des patterns comme foreach($array as...) dans foreach($array as...)
                        foreach_match = re.search(r'foreach\s*\(\s*\$([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s+', line_stripped)
                        if foreach_match:
                            current_array = foreach_match.group(1)
                            # Chercher dans les lignes précédentes pour voir si le même tableau est utilisé
                            for prev_line_num in range(max(0, line_num - 10), line_num):
                                if prev_line_num < len(lines):
                                    prev_line = lines[prev_line_num].strip()
                                    prev_match = re.search(r'foreach\s*\(\s*\$([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s+', prev_line)
                                    if prev_match and prev_match.group(1) == current_array:
                                        issues.append({
                                            'rule_name': 'performance.nested_loop_same_array',
                                            'message': f'Boucles imbriquées sur le même tableau ${current_array} - complexité O(n²)',
                                            'file_path': str(file_path),
                                            'line': line_num,
                                            'column': 0,
                                            'severity': 'warning',
                                            'issue_type': 'performance',
                                            'suggestion': 'Revoir l\'algorithme pour éviter le parcours quadratique du même tableau',
                                            'code_snippet': line.strip()
                                        })
                                        break
                
                # Détecter les variables non initialisées (utilisation avant affectation)
                if re.search(r'\b(if|for|while|foreach|switch)\s*\(\s*\$[a-zA-Z_][a-zA-Z0-9_]*\s*\)', line_stripped):
                    var_name = re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*', line_stripped).group(0)
                    
                    # Vérifier si la variable a été initialisée dans les 20 lignes précédentes
                    initialized = False
                    for prev_line_num in range(max(0, line_num - 20), line_num):
                        if re.search(rf'\bvar\s+\{var_name}\b', lines[prev_line_num].strip()):
                            initialized = True
                            break
                    
                    if not initialized:
                        issues.append({
                            'rule_name': 'error.uninitialized_variable',
                            'message': f'Variable non initialisée ${var_name} utilisée dans {line_stripped}',
                            'file_path': str(file_path),
                            'line': line_num,
                            'column': 0,
                            'severity': 'error',
                            'issue_type': 'error',
                            'suggestion': f'Verifiez que ${var_name} est bien initialisée avant utilisation',
                            'code_snippet': line.strip()
                        })
                
                # Détecter les appels de méthode sur des variables potentiellement null
                if re.search(r'\b(null|undefined)\s*\?\s*\$[a-zA-Z_][a-zA-Z0-9_]*\s*:', line_stripped):
                    var_name = re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*', line_stripped).group(0)
                    
                    issues.append({
                        'rule_name': 'error.possible_null_reference',
                        'message': f'Appel de méthode sur ${var_name} qui pourrait être null',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'error',
                        'suggestion': f'Vérifiez que ${var_name} n\'est pas null avant d\'appeler une méthode dessus',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les chaînes de caractères non échappées dans les requêtes SQL
                if re.search(r'query\s*\(\s*["\'].*["\']\s*,\s*\$[a-zA-Z_][a-zA-Z0-9_]*\s*\)', line_stripped):
                    issues.append({
                        'rule_name': 'error.sql_injection_risk',
                        'message': 'Chaîne de requête SQL non échappée détectée',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'error',
                        'suggestion': 'Utiliser des requêtes préparées avec des paramètres liés',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les inclusions de fichiers basées sur des variables non sécurisées
                if re.search(r'include\s*\(\s*\$[a-zA-Z_][a-zA-Z0-9_]*\s*\)', line_stripped):
                    var_name = re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*', line_stripped).group(0)
                    
                    issues.append({
                        'rule_name': 'error.file_inclusion_risk',
                        'message': f'Inclusion de fichier avec une variable non sécurisée ${var_name}',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'error',
                        'suggestion': 'Valider et assainir la variable avant inclusion de fichier',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les erreurs de syntaxe communes
                if re.search(r'\b(if|for|while|foreach|switch)\s*\(\s*[^()]*\s*\)\s*{?', line_stripped):
                    issues.append({
                        'rule_name': 'error.syntax',
                        'message': 'Vérifiez la syntaxe de la structure de contrôle (if, for, while, foreach, switch)',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'error',
                        'suggestion': 'Assurez-vous que la syntaxe est correcte et complète',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les appels de fonction avec un nombre incorrect d'arguments
                if re.search(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*[^()]*\s*\)', line_stripped):
                    func_name = re.search(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*', line_stripped).group(1)
                    
                    # Vérifier les fonctions courantes avec un nombre fixe d'arguments
                    common_functions = {
                        'strpos': 3,
                        'substr': 4,
                        'array_slice': 4,
                        'gethostbyname': 2,
                        'json_decode': 2,
                        'preg_match': 3,
                        'mysqli_query': 3,
                        'fopen': 2,
                        'file_get_contents': 2,
                        'file_put_contents': 3
                    }
                    
                    if func_name in common_functions:
                        expected_args = common_functions[func_name]
                        
                        # Compter le nombre d'arguments dans l'appel
                        args_count = len(re.findall(r',', re.search(r'\(\s*([^()]*)\s*\)', line_stripped).group(1))) + 1
                        
                        if args_count != expected_args:
                            issues.append({
                                'rule_name': 'error.incorrect_argument_count',
                                'message': f'Fonction {func_name}() attend {expected_args} arguments, {args_count} fournis',
                                'file_path': str(file_path),
                                'line': line_num,
                                'column': 0,
                                'severity': 'error',
                                'issue_type': 'error',
                                'suggestion': f'Vérifiez l\'appel de fonction et corrigez le nombre d\'arguments',
                                'code_snippet': line.strip()
                            })
                
                # Détecter les affectations dans les conditions (peut-être une erreur)
                if re.search(r'=\s*[^=]', line_stripped) and re.search(r'\b(if|for|while|foreach|switch)\s*\(\s*[^()]*\s*=\s*[^()]*\s*\)', line_stripped):
                    issues.append({
                        'rule_name': 'error.possible_assignment_in_condition',
                        'message': 'Affectation détectée dans une condition (if, for, while, foreach, switch)',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'error',
                        'suggestion': 'Vérifiez si c\'est bien une affectation voulue et non une erreur',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les chaînes de caractères multiligne non délimitées
                if re.search(r'["\'][^"\']*["\'][\s]*\+[^\s]', line_stripped):
                    issues.append({
                        'rule_name': 'error.missing_string_delimiter',
                        'message': 'Chaîne de caractères multiligne détectée sans délimiteur explicite',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'error',
                        'suggestion': 'Utiliser un point-virgule pour terminer la chaîne ou la décomposer en plusieurs chaînes',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les appels de méthode sur des chaînes sans vérification de type
                if re.search(r'\b(is_string|is_int|is_bool|is_array|is_object|is_null)\s*\(\s*\$[a-zA-Z_][a-zA-Z0-9_]*\s*\)', line_stripped):
                    var_name = re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*', line_stripped).group(0)
                    
                    issues.append({
                        'rule_name': 'error.possible_type_error',
                        'message': f'Vérification de type sur ${var_name} sans garantie de type',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'error',
                        'suggestion': 'Assurez-vous que la variable est bien du type attendu avant d\'appeler la méthode',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les erreurs de typographie courantes
                common_typos = {
                    'echp': 'echo',
                    'prnt': 'print',
                    'var_dumped': 'var_dump',
                    'vardump': 'var_dump',
                    'exit();': 'exit;',
                    'die();': 'die;',
                    'include_once': 'include',
                    'require_once': 'require',
                    'isset()&&': 'isset() &&',
                    'empty()&&': 'empty() &&',
                    'count()&&': 'count() &&',
                    'sizeof()&&': 'sizeof() &&',
                    'array()': '[]',
                    '=>': '->',
                    'null': 'NULL',
                    'true': 'TRUE',
                    'false': 'FALSE'
                }
                
                for typo, correction in common_typos.items():
                    if re.search(rf'\b{typo}\b', line_stripped):
                        issues.append({
                            'rule_name': 'error.typographical_error',
                            'message': f'Erreur de typographie détectée: {typo}',
                            'file_path': str(file_path),
                            'line': line_num,
                            'column': 0,
                            'severity': 'error',
                            'issue_type': 'error',
                            'suggestion': f'Corriger en: {correction}',
                            'code_snippet': line.strip()
                        })
                        break  # Une seule détection par ligne
            
            # Détecter les calculs répétés (après la boucle principale)
            math_expressions = {}
            method_boundaries = self._get_method_boundaries(lines)
            
            for line_num, line in enumerate(lines, 1):
                # Rechercher les expressions mathématiques du type $var = $a * $b + $c
                # Exclure $this qui n'est pas une variable calculable
                match = re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*(\$[a-zA-Z_][a-zA-Z0-9_]*\s*[\+\-\*\/]\s*\$[a-zA-Z_][a-zA-Z0-9_]*(?:\s*[\+\-\*\/]\s*\$[a-zA-Z_][a-zA-Z0-9_]*)*)', line)
                if match:
                    expr = match.group(1)
                    expr_clean = re.sub(r'\s+', ' ', expr.strip())
                    
                    # Ignorer les expressions contenant $this (référence d'objet, pas variable calculable)
                    if '$this' in expr_clean:
                        continue
                    
                    # Ignorer les expressions trop simples (une seule variable)
                    if not re.search(r'[\+\-\*\/]', expr_clean):
                        continue
                    
                    # Déterminer dans quelle méthode se trouve cette ligne
                    method_name = self._get_method_for_line(line_num, method_boundaries)
                    
                    # Créer une clé qui inclut l'expression et la méthode
                    key = f"{expr_clean}__in__{method_name}"
                    
                    if key not in math_expressions:
                        math_expressions[key] = []
                    math_expressions[key].append((line_num, line.strip(), method_name))
            
            # Signaler les expressions répétées dans la MÊME méthode
            for key, occurrences in math_expressions.items():
                if len(occurrences) >= 2:  # Au moins 2 occurrences dans la même méthode
                    expr_clean = key.split('__in__')[0]
                    method_name = key.split('__in__')[1]
                    first_line, first_code, _ = occurrences[0]
                    
                    # Ne signaler que si c'est dans la même méthode et pas 'unknown'
                    if method_name != 'unknown':
                        issues.append({
                            'rule_name': 'performance.repeated_calculations',
                            'message': f'Calcul répété détecté dans {method_name}(): {expr_clean} (trouvé {len(occurrences)} fois)',
                            'file_path': str(file_path),
                            'line': first_line,
                            'column': 0,
                            'severity': 'info',
                            'issue_type': 'performance',
                            'suggestion': f'Stocker le résultat de "{expr_clean}" dans une variable réutilisable',
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
    
    def analyze_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyser du code PHP fourni sous forme de chaîne (pour les tests unitaires)"""
        start_time = time.time()
        try:
            issues = []
            lines = content.split('\n')
            loop_stack = []
            in_loop = False
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                # Copie la logique d'analyse de analyze_file (détection foreach non-itérable incluse)
                # Détecter le début d'une boucle
                if re.search(r'\b(for|foreach|while)\s*\(', line_stripped):
                    loop_stack.append(line_num)
                    in_loop = True
                    
                    # Détecter foreach sur non-itérable
                    foreach_match = re.search(r'foreach\s*\(\s*\$([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s+', line_stripped)
                    if foreach_match:
                        var_name = foreach_match.group(1)
                        # Chercher dans les lignes précédentes si cette variable a été assignée à un scalaire
                        for prev_line_num in range(max(0, line_num - 20), line_num):  # Chercher dans les 20 lignes précédentes
                            if prev_line_num < len(lines):
                                prev_line = lines[prev_line_num].strip()
                                # Détecter assignation à un scalaire (nombre, chaîne, booléen, null)
                                scalar_pattern = rf'\${var_name}\s*=\s*(?:true|false|null|\d+(?:\.\d+)?|["\'][^"\']*["\'])\s*;'
                                if re.search(scalar_pattern, prev_line, re.IGNORECASE):
                                    issues.append({
                                        'rule_name': 'error.foreach_non_iterable',
                                        'message': f'foreach on non-iterable variable ${var_name} (assigned to scalar value)',
                                        'file_path': str(file_path),
                                        'line': line_num,
                                        'column': 0,
                                        'severity': 'error',
                                        'issue_type': 'error',
                                        'suggestion': f'Ensure ${var_name} is an array or iterable object before using foreach',
                                        'code_snippet': line.strip()
                                    })
                                    break
                    
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
                
                # Détecter les fonctions lourdes dans les boucles
                if in_loop and loop_stack:
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
                            issues.append({
                                'rule_name': 'performance.heavy_function_in_loop',
                                'message': f'{description} dans une boucle peut être très lent',
                                'file_path': str(file_path),
                                'line': line_num,
                                'column': 0,
                                'severity': 'warning',
                                'issue_type': 'performance',
                                'suggestion': f'Extraire {func}() hors de la boucle et mettre en cache le résultat',
                                'code_snippet': line.strip()
                            })
                            break
                
                # Détecter création répétée d'objets dans les boucles
                if in_loop and loop_stack:
                    # Patterns d'instanciation d'objets
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
                                issues.append({
                                    'rule_name': 'performance.object_creation_in_loop',
                                    'message': f'Création répétée d\'objet {class_name} dans une boucle avec arguments constants',
                                    'file_path': str(file_path),
                                    'line': line_num,
                                    'column': 0,
                                    'severity': 'warning',
                                    'issue_type': 'performance',
                                    'suggestion': f'Extraire la création de {class_name} hors de la boucle et réutiliser l\'instance',
                                    'code_snippet': line.strip()
                                })
                                break
                
                # Détecter les problèmes de complexité algorithmique
                if in_loop and loop_stack:
                    # Détecter les tris dans les boucles (sort, usort, asort, etc.)
                    sort_functions = ['sort', 'rsort', 'asort', 'arsort', 'ksort', 'krsort', 'usort', 'uasort', 'uksort', 'array_multisort']
                    for sort_func in sort_functions:
                        if re.search(rf'\b{sort_func}\s*\(', line_stripped):
                            issues.append({
                                'rule_name': 'performance.sort_in_loop',
                                'message': f'Fonction de tri {sort_func}() dans une boucle - complexité O(n²log n) ou pire',
                                'file_path': str(file_path),
                                'line': line_num,
                                'column': 0,
                                'severity': 'warning',
                                'issue_type': 'performance',
                                'suggestion': f'Extraire le tri {sort_func}() hors de la boucle pour améliorer les performances',
                                'code_snippet': line.strip()
                            })
                            break
                    
                    # Détecter recherche linéaire dans boucle (in_array, array_search)
                    search_functions = ['in_array', 'array_search', 'array_key_exists']
                    for search_func in search_functions:
                        if re.search(rf'\b{search_func}\s*\(', line_stripped):
                            issues.append({
                                'rule_name': 'performance.linear_search_in_loop',
                                'message': f'Recherche linéaire {search_func}() dans une boucle - complexité O(n²)',
                                'file_path': str(file_path),
                                'line': line_num,
                                'column': 0,
                                'severity': 'warning',
                                'issue_type': 'performance',
                                'suggestion': f'Convertir le tableau en clé-valeur ou utiliser array_flip() avant la boucle pour une recherche O(1)',
                                'code_snippet': line.strip()
                            })
                            break
                    
                    # Détecter boucles imbriquées avec même tableau (parcours O(n²) potentiel)
                    if len(loop_stack) >= 2:
                        # Chercher des patterns comme foreach($array as...) dans foreach($array as...)
                        foreach_match = re.search(r'foreach\s*\(\s*\$([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s+', line_stripped)
                        if foreach_match:
                            current_array = foreach_match.group(1)
                            # Chercher dans les lignes précédentes pour voir si le même tableau est utilisé
                            for prev_line_num in range(max(0, line_num - 10), line_num):
                                if prev_line_num < len(lines):
                                    prev_line = lines[prev_line_num].strip()
                                    prev_match = re.search(r'foreach\s*\(\s*\$([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s+', prev_line)
                                    if prev_match and prev_match.group(1) == current_array:
                                        issues.append({
                                            'rule_name': 'performance.nested_loop_same_array',
                                            'message': f'Boucles imbriquées sur le même tableau ${current_array} - complexité O(n²)',
                                            'file_path': str(file_path),
                                            'line': line_num,
                                            'column': 0,
                                            'severity': 'warning',
                                            'issue_type': 'performance',
                                            'suggestion': 'Revoir l\'algorithme pour éviter le parcours quadratique du même tableau',
                                            'code_snippet': line.strip()
                                        })
                                        break
                
                # Détecter les variables non initialisées (utilisation avant affectation)
                if re.search(r'\b(if|for|while|foreach|switch)\s*\(\s*\$[a-zA-Z_][a-zA-Z0-9_]*\s*\)', line_stripped):
                    var_name = re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*', line_stripped).group(0)
                    
                    # Vérifier si la variable a été initialisée dans les 20 lignes précédentes
                    initialized = False
                    for prev_line_num in range(max(0, line_num - 20), line_num):
                        if re.search(rf'\bvar\s+\{var_name}\b', lines[prev_line_num].strip()):
                            initialized = True
                            break
                    
                    if not initialized:
                        issues.append({
                            'rule_name': 'error.uninitialized_variable',
                            'message': f'Variable non initialisée ${var_name} utilisée dans {line_stripped}',
                            'file_path': str(file_path),
                            'line': line_num,
                            'column': 0,
                            'severity': 'error',
                            'issue_type': 'error',
                            'suggestion': f'Verifiez que ${var_name} est bien initialisée avant utilisation',
                            'code_snippet': line.strip()
                        })
                
                # Détecter les appels de méthode sur des variables potentiellement null
                if re.search(r'\b(null|undefined)\s*\?\s*\$[a-zA-Z_][a-zA-Z0-9_]*\s*:', line_stripped):
                    var_name = re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*', line_stripped).group(0)
                    
                    issues.append({
                        'rule_name': 'error.possible_null_reference',
                        'message': f'Appel de méthode sur ${var_name} qui pourrait être null',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'error',
                        'suggestion': f'Vérifiez que ${var_name} n\'est pas null avant d\'appeler une méthode dessus',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les chaînes de caractères non échappées dans les requêtes SQL
                if re.search(r'query\s*\(\s*["\'].*["\']\s*,\s*\$[a-zA-Z_][a-zA-Z0-9_]*\s*\)', line_stripped):
                    issues.append({
                        'rule_name': 'error.sql_injection_risk',
                        'message': 'Chaîne de requête SQL non échappée détectée',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'error',
                        'suggestion': 'Utiliser des requêtes préparées avec des paramètres liés',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les inclusions de fichiers basées sur des variables non sécurisées
                if re.search(r'include\s*\(\s*\$[a-zA-Z_][a-zA-Z0-9_]*\s*\)', line_stripped):
                    var_name = re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*', line_stripped).group(0)
                    
                    issues.append({
                        'rule_name': 'error.file_inclusion_risk',
                        'message': f'Inclusion de fichier avec une variable non sécurisée ${var_name}',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'error',
                        'suggestion': 'Valider et assainir la variable avant inclusion de fichier',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les erreurs de syntaxe communes
                if re.search(r'\b(if|for|while|foreach|switch)\s*\(\s*[^()]*\s*\)\s*{?', line_stripped):
                    issues.append({
                        'rule_name': 'error.syntax',
                        'message': 'Vérifiez la syntaxe de la structure de contrôle (if, for, while, foreach, switch)',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'error',
                        'suggestion': 'Assurez-vous que la syntaxe est correcte et complète',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les appels de fonction avec un nombre incorrect d'arguments
                if re.search(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*[^()]*\s*\)', line_stripped):
                    func_name = re.search(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*', line_stripped).group(1)
                    
                    # Vérifier les fonctions courantes avec un nombre fixe d'arguments
                    common_functions = {
                        'strpos': 3,
                        'substr': 4,
                        'array_slice': 4,
                        'gethostbyname': 2,
                        'json_decode': 2,
                        'preg_match': 3,
                        'mysqli_query': 3,
                        'fopen': 2,
                        'file_get_contents': 2,
                        'file_put_contents': 3
                    }
                    
                    if func_name in common_functions:
                        expected_args = common_functions[func_name]
                        
                        # Compter le nombre d'arguments dans l'appel
                        args_count = len(re.findall(r',', re.search(r'\(\s*([^()]*)\s*\)', line_stripped).group(1))) + 1
                        
                        if args_count != expected_args:
                            issues.append({
                                'rule_name': 'error.incorrect_argument_count',
                                'message': f'Fonction {func_name}() attend {expected_args} arguments, {args_count} fournis',
                                'file_path': str(file_path),
                                'line': line_num,
                                'column': 0,
                                'severity': 'error',
                                'issue_type': 'error',
                                'suggestion': f'Vérifiez l\'appel de fonction et corrigez le nombre d\'arguments',
                                'code_snippet': line.strip()
                            })
                
                # Détecter les affectations dans les conditions (peut-être une erreur)
                if re.search(r'=\s*[^=]', line_stripped) and re.search(r'\b(if|for|while|foreach|switch)\s*\(\s*[^()]*\s*=\s*[^()]*\s*\)', line_stripped):
                    issues.append({
                        'rule_name': 'error.possible_assignment_in_condition',
                        'message': 'Affectation détectée dans une condition (if, for, while, foreach, switch)',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'error',
                        'suggestion': 'Vérifiez si c\'est bien une affectation voulue et non une erreur',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les chaînes de caractères multiligne non délimitées
                if re.search(r'["\'][^"\']*["\'][\s]*\+[^\s]', line_stripped):
                    issues.append({
                        'rule_name': 'error.missing_string_delimiter',
                        'message': 'Chaîne de caractères multiligne détectée sans délimiteur explicite',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'error',
                        'suggestion': 'Utiliser un point-virgule pour terminer la chaîne ou la décomposer en plusieurs chaînes',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les appels de méthode sur des chaînes sans vérification de type
                if re.search(r'\b(is_string|is_int|is_bool|is_array|is_object|is_null)\s*\(\s*\$[a-zA-Z_][a-zA-Z0-9_]*\s*\)', line_stripped):
                    var_name = re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*', line_stripped).group(0)
                    
                    issues.append({
                        'rule_name': 'error.possible_type_error',
                        'message': f'Vérification de type sur ${var_name} sans garantie de type',
                        'file_path': str(file_path),
                        'line': line_num,
                        'column': 0,
                        'severity': 'error',
                        'issue_type': 'error',
                        'suggestion': 'Assurez-vous que la variable est bien du type attendu avant d\'appeler la méthode',
                        'code_snippet': line.strip()
                    })
                
                # Détecter les erreurs de typographie courantes
                common_typos = {
                    'echp': 'echo',
                    'prnt': 'print',
                    'var_dumped': 'var_dump',
                    'vardump': 'var_dump',
                    'exit();': 'exit;',
                    'die();': 'die;',
                    'include_once': 'include',
                    'require_once': 'require',
                    'isset()&&': 'isset() &&',
                    'empty()&&': 'empty() &&',
                    'count()&&': 'count() &&',
                    'sizeof()&&': 'sizeof() &&',
                    'array()': '[]',
                    '=>': '->',
                    'null': 'NULL',
                    'true': 'TRUE',
                    'false': 'FALSE'
                }
                
                for typo, correction in common_typos.items():
                    if re.search(rf'\b{typo}\b', line_stripped):
                        issues.append({
                            'rule_name': 'error.typographical_error',
                            'message': f'Erreur de typographie détectée: {typo}',
                            'file_path': str(file_path),
                            'line': line_num,
                            'column': 0,
                            'severity': 'error',
                            'issue_type': 'error',
                            'suggestion': f'Corriger en: {correction}',
                            'code_snippet': line.strip()
                        })
                        break  # Une seule détection par ligne
            
            # Détecter les calculs répétés (après la boucle principale)
            math_expressions = {}
            method_boundaries = self._get_method_boundaries(lines)
            
            for line_num, line in enumerate(lines, 1):
                # Rechercher les expressions mathématiques du type $var = $a * $b + $c
                # Exclure $this qui n'est pas une variable calculable
                match = re.search(r'\$[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*(\$[a-zA-Z_][a-zA-Z0-9_]*\s*[\+\-\*\/]\s*\$[a-zA-Z_][a-zA-Z0-9_]*(?:\s*[\+\-\*\/]\s*\$[a-zA-Z_][a-zA-Z0-9_]*)*)', line)
                if match:
                    expr = match.group(1)
                    expr_clean = re.sub(r'\s+', ' ', expr.strip())
                    
                    # Ignorer les expressions contenant $this (référence d'objet, pas variable calculable)
                    if '$this' in expr_clean:
                        continue
                    
                    # Ignorer les expressions trop simples (une seule variable)
                    if not re.search(r'[\+\-\*\/]', expr_clean):
                        continue
                    
                    # Déterminer dans quelle méthode se trouve cette ligne
                    method_name = self._get_method_for_line(line_num, method_boundaries)
                    
                    # Créer une clé qui inclut l'expression et la méthode
                    key = f"{expr_clean}__in__{method_name}"
                    
                    if key not in math_expressions:
                        math_expressions[key] = []
                    math_expressions[key].append((line_num, line.strip(), method_name))
            
            # Signaler les expressions répétées dans la MÊME méthode
            for key, occurrences in math_expressions.items():
                if len(occurrences) >= 2:  # Au moins 2 occurrences dans la même méthode
                    expr_clean = key.split('__in__')[0]
                    method_name = key.split('__in__')[1]
                    first_line, first_code, _ = occurrences[0]
                    
                    # Ne signaler que si c'est dans la même méthode et pas 'unknown'
                    if method_name != 'unknown':
                        issues.append({
                            'rule_name': 'performance.repeated_calculations',
                            'message': f'Calcul répété détecté dans {method_name}(): {expr_clean} (trouvé {len(occurrences)} fois)',
                            'file_path': str(file_path),
                            'line': first_line,
                            'column': 0,
                            'severity': 'info',
                            'issue_type': 'performance',
                            'suggestion': f'Stocker le résultat de "{expr_clean}" dans une variable réutilisable',
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
            
            # Pour les variables de boucle, permettre unset() après la boucle
            # Ne s'arrêter que si on sort vraiment de la fonction/classe
            if current_brace_level < initial_brace_level - 1:
                break
            
            # Arrêter à la fin d'une fonction ou classe (détection plus précise)
            if re.search(r'^\s*}\s*$', line):
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
    
    def _is_comment_line(self, line: str) -> bool:
        """
        Détecter si une ligne est un commentaire ou contient uniquement des commentaires.
        
        Args:
            line: La ligne à analyser
            
        Returns:
            True si la ligne est un commentaire ou ne contient que des commentaires
        """
        line_stripped = line.strip()
        
        # Ligne vide
        if not line_stripped:
            return False
            
        # Commentaire de ligne
        if line_stripped.startswith('//') or line_stripped.startswith('#'):
            return True
            
        # Commentaire PHPDoc ou de bloc
        if line_stripped.startswith('/*') or line_stripped.startswith('/**'):
            return True
            
        # Ligne qui contient uniquement un * (continuation de commentaire PHPDoc)
        if re.match(r'^\s*\*.*$', line_stripped):
            return True
            
        # Fin de commentaire de bloc
        if line_stripped.endswith('*/') and not re.search(r'\S.*\*/', line_stripped):
            return True
            
        return False

    def _remove_strings_and_comments(self, line: str) -> str:
        """
        Supprimer les chaînes de caractères et commentaires d'une ligne pour éviter
        de compter les accolades qui ne sont pas du code.
        """
        # Supprimer les commentaires de ligne
        line = re.sub(r'//.*$', '', line)
        line = re.sub(r'#.*$', '', line)
        
        # Supprimer les commentaires de bloc (/* ... */ sur une ligne)
        line = re.sub(r'/\*.*?\*/', '', line)
        
        # Supprimer les commentaires PHPDoc (/** ... */ sur une ligne)  
        line = re.sub(r'/\*\*.*?\*/', '', line)
        
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

    def _is_blade_directive(self, line: str) -> bool:
        """
        Détecter si une ligne contient une directive Blade Laravel.
        
        Args:
            line: La ligne à analyser
            
        Returns:
            True si la ligne contient une directive Blade (@if, @endif, @auth, etc.)
        """
        line_stripped = line.strip()
        
        # Liste des directives Blade courantes
        blade_directives = [
            'if', 'elseif', 'else', 'endif',
            'unless', 'endunless',
            'auth', 'endauth', 'guest', 'endguest',
            'isset', 'empty',
            'switch', 'case', 'break', 'default', 'endswitch',
            'for', 'endfor', 'foreach', 'endforeach', 'while', 'endwhile',
            'forelse', 'endforelse',
            'continue', 'break',
            'include', 'includeIf', 'includeWhen', 'includeUnless', 'includeFirst',
            'extends', 'section', 'endsection', 'show', 'stop', 'yield', 'parent',
            'push', 'endpush', 'prepend', 'endprepend', 'stack',
            'component', 'endcomponent', 'slot', 'endslot',
            'csrf', 'method', 'error', 'json', 'lang',
            'can', 'cannot', 'endcan', 'endcannot',
            'hasSection', 'sectionMissing',
            'production', 'endproduction', 'env', 'endenv',
            'dd', 'dump',
            'php', 'endphp',
            'verbatim', 'endverbatim',
            'once', 'endonce',
            'aware', 'endaware',
            'props'
        ]
        
        # Vérifier si la ligne contient une directive Blade spécifique
        for directive in blade_directives:
           
            # Pattern pour détecter @directive avec ou sans parenthèses/paramètres
            pattern = rf'@{directive}(?:\s|$|\()'
            if re.search(pattern, line_stripped):
                return True
        
        # Ne pas considérer les autres @ comme Blade - ils seront traités comme suppressions d'erreurs
        return False

    def _get_method_boundaries(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Détecter les limites des méthodes dans le code PHP.
        
        Args:
            lines: Liste des lignes du fichier
            
        Returns:
            Liste des méthodes avec leurs limites (start_line, end_line, name)
        """
        methods = []
        brace_stack = []
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Détecter une déclaration de méthode/fonction
            method_match = re.search(r'\b(?:public|private|protected)?\s*(?:static)?\s*function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', line_stripped)
            if method_match:
                method_name = method_match.group(1)
                
                # Chercher l'accolade ouvrante
                opening_brace_line = line_num
                for i in range(line_num - 1, min(line_num + 5, len(lines))):
                    if '{' in lines[i]:
                        opening_brace_line = i + 1
                        break
                
                methods.append({
                    'name': method_name,
                    'start_line': line_num,
                    'opening_brace_line': opening_brace_line,
                    'end_line': None  # À déterminer
                })
                
                # Ajouter au stack pour suivre les accolades
                brace_stack.append(len(methods) - 1)
            
            # Compter les accolades pour déterminer la fin des méthodes
            line_clean = self._remove_strings_and_comments(line)
            open_braces = line_clean.count('{')
            close_braces = line_clean.count('}')
            
            # Mettre à jour le stack des accolades
            for _ in range(open_braces):
                if brace_stack:  # Il y a une méthode active
                    pass  # On garde le tracking
            
            for _ in range(close_braces):
                if brace_stack:
                    # C'est potentiellement la fin d'une méthode
                    method_index = brace_stack[-1]
                    if methods[method_index]['end_line'] is None:
                        # Vérifier si on est au bon niveau d'accolades
                        current_level = self._calculate_brace_level(lines, line_num - 1)
                        method_start_level = self._calculate_brace_level(lines, methods[method_index]['opening_brace_line'] - 1)
                        
                        if current_level <= method_start_level:
                            methods[method_index]['end_line'] = line_num
                            brace_stack.pop()
        
        return methods

    def _get_method_for_line(self, line_num: int, method_boundaries: List[Dict[str, Any]]) -> str:
        """
        Déterminer dans quelle méthode se trouve une ligne donnée.
        
        Args:
            line_num: Numéro de ligne (1-based)
            method_boundaries: Liste des méthodes avec leurs limites
            
        Returns:
            Le nom de la méthode ou 'unknown' si pas dans une méthode
        """
        for method in method_boundaries:
            start = method['start_line']
            end = method.get('end_line')
            
            if end is None:
                # Méthode sans fin détectée, on assume qu'elle va jusqu'à la fin du fichier
                if line_num >= start:
                    return method['name']
            else:
                if start <= line_num <= end:
                    return method['name']
        
        return 'unknown'
