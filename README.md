# PHP Code Optimizer

Un outil d'analyse et d'optimisation de code PHP écrit en Python avec **architecture modulaire** et **système de suggestions avancé**.

## ✨ Nouvelles Fonctionnalités v2.2.0

### 🎯 **Suggestions de Correction Détaillées**
- **Exemples "Avant/Après"** : Code PHP réel avec corrections appliquées
- **Solutions Contextuelles** : Suggestions adaptées au problème exact détecté
- **Copie en Un Clic** : Boutons pour copier les exemples de correction
- **Interface Moderne** : Rapports HTML interactifs avec design responsive

### 💡 **Types de Suggestions Disponibles**
- **🔐 Sécurité** : Injections SQL → Requêtes préparées, XSS → htmlspecialchars()
- **⚡ Performance** : Boucles → Optimisation count(), Mémoire → unset()
- **📚 Bonnes Pratiques** : Documentation → PHPDoc, Nommage → Conventions
- **🔧 Qualité** : Variables inutilisées → Nettoyage, Null checks → try/catch

## 🚀 Fonctionnalités Principales

- 🔍 **Analyse Statique Avancée** – Détecte **25+ types de problèmes** avec suggestions de correction
- 🏗️ **Architecture Modulaire** – Analyseurs spécialisés pour performance, sécurité, mémoire, boucles, erreurs
- 💡 **Suggestions Intelligentes** – Exemples de code PHP prêts à copier-coller
- ⚡ **Optimisation Mémoire** – Détecte les `unset()` manquants pour gros tableaux (>10k éléments)
- ❌ **Prévention d'Erreurs** – Détecte l'usage de `foreach` sur variables non-itérables
- 🗃️ **Détection N+1** – Identifie les requêtes SQL inefficaces dans les boucles
- 🔄 **Complexité Algorithmique** – Détecte les patterns O(n²) et suggère des optimisations O(1)
- 🎯 **Analyse XPath Intelligente** – Analyse les sélecteurs XPath lents (`//*`, `contains()`, etc.)
- 🛡️ **Scanner de Sécurité** – Injection SQL, XSS, hachage faible, inclusions dangereuses
- 📊 **Rapports Multi-formats** – Console colorée, HTML interactif, JSON pour CI/CD
- 🧪 **Système Extensible** – Facile d'ajouter de nouveaux analyseurs et règles
- 🔧 **Tests Complets** – Suite de tests avec exemples PHP du monde réel

## 📋 Installation

```bash
# Cloner le repository
git clone <your-repo>
cd phpoptimizer

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt

# Installer en mode développement
pip install -e .
```

## 🎮 Utilisation

### Analyser un fichier PHP avec suggestions détaillées

```bash
phpoptimizer analyze examples/performance_test.php --verbose
```

### Générer un rapport HTML interactif

```bash
phpoptimizer analyze examples/ --output-format html --output rapport.html
```

### Analyser un dossier recursif

```bash
phpoptimizer analyze src/ --recursive --output-format html --output rapport.html
```

## 💡 Exemples de Suggestions

### 🔐 Sécurité - Injection SQL
```php
// ❌ Code vulnérable détecté
$result = mysql_query("SELECT * FROM users WHERE id = " . $_GET['id']);

// ✅ Suggestion de correction
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
$stmt->execute([$_GET['id']]);
$result = $stmt->fetchAll();
```

### ⚡ Performance - Boucles Inefficaces
```php
// ❌ Code inefficace détecté
for ($i = 0; $i < count($array); $i++) {
    echo $array[$i];
}

// ✅ Suggestion de correction
$length = count($array);
for ($i = 0; $i < $length; $i++) {
    echo $array[$i];
}
// Ou encore mieux avec foreach
foreach ($array as $value) {
    echo $value;
}
```

### 🧠 Gestion Mémoire
```php
// ❌ Code gourmand en mémoire
$huge_array = range(1, 1000000);
$result = array_sum($huge_array);
return $result; // $huge_array reste en mémoire

// ✅ Suggestion de correction
$huge_array = range(1, 1000000);
$result = array_sum($huge_array);
unset($huge_array); // Libère la mémoire immédiatement
return $result;
```

## 📊 Exemple de Sortie Console

```
============================================================
  RAPPORT D'ANALYSE PHP OPTIMIZER
============================================================
📊 Statistiques générales: 1 fichier analysé, 12 problèmes détectés
🎯 Répartition par sévérité: 2 erreurs, 3 avertissements, 7 infos

📄 test_performance.php
   📍 Ligne 13: Appel de count() dans une condition de boucle for (inefficace)
      💡 Solution: Évitez d'appeler count() à chaque itération de boucle.
      📝 Exemple de correction:
         // ❌ Code inefficace - count() appelé à chaque itération
         // for ($i = 0; $i < count($array); $i++) { echo $array[$i]; }
         
         // ✅ Code optimisé - count() appelé une seule fois
         $length = count($array);
         for ($i = 0; $i < $length; $i++) { echo $array[$i]; }

🏆 Top des problèmes: performance.inefficient_loops (3x), security.sql_injection (2x)
```

## ⚙️ Options Disponibles

- `--verbose, -v`: Affichage détaillé avec suggestions et exemples de correction
- `--recursive, -r`: Analyser récursivement les sous-dossiers
- `--output-format`: Format de sortie (console, json, html)
- `--output, -o`: Fichier de sortie
- `--rules`: Fichier de configuration des règles personnalisées
- `--severity`: Niveau de sévérité minimum (info, warning, error)

## 🌐 Rapport HTML Interactif

Le nouveau rapport HTML offre une expérience moderne et interactive :

### 🎨 Fonctionnalités Visuelles
- **Design Moderne** : Interface responsive avec dégradés et animations
- **Dashboard Statistiques** : Cartes métriques colorées par sévérité
- **Navigation Intuitive** : Organisation claire par fichier et ligne

### 🔧 Fonctionnalités Interactives
- **📋 Copie en Un Clic** : Boutons pour copier les exemples de correction
- **📂 Navigation Rapide** : Copie des chemins de fichiers
- **✅ Feedback Visuel** : Confirmation des actions avec animations
- **📝 Exemples Détaillés** : Code PHP formaté avec coloration syntaxique

### 📱 Responsive Design
- Compatible desktop, tablette et mobile
- Optimisé pour tous les navigateurs modernes
- Interface accessible et ergonomique

## 🧪 Types d'Analyses Supportés


## Optimization Rules

The tool currently detects **over 25 types of issues** across several categories:

### 🚀 Performance

- **Inefficient loops**: `count()` in loop conditions, deeply nested loops
- **Queries in loops**: Detects N+1 issue (SQL queries inside loops)
- **Heavy functions in loops**: I/O operations (`file_get_contents`, `glob`, `curl_exec`, etc.)
- **Algorithmic complexity**: Sort functions (`sort`, `usort`) in loops, linear search (`in_array`, `array_search`) in loops
- **Nested loops optimization**: Detection of nested loops on the same array (O(n²) complexity)
- **Object creation in loops**: Repeated instantiation with constant arguments (`new DateTime('constant')`, singletons)
- **Superglobal access in loops**: Repeated access to `$_SESSION`, `$_GET`, `$_POST`, etc. in loops
- **Global variable optimization**: Detection of unused global variables and variables that could be local
- **Memory management**: Large arrays not released with `unset()` (>10,000 elements)
- **Inefficient concatenation**: String concatenation inside loops
- **Obsolete functions**: `mysql_query()`, `ereg()`, `split()`, `each()`
- **Error suppression**: Use of `@` affecting performance
- **Inefficient XPath**: Descendant selectors (`//*`), `contains()`, double descendant
- **Slow DOM**: `getElementById()`, `getElementsByTagName()` inside loops
- **Inefficient regex**: Patterns with problematic `.*`
- **Miscellaneous optimizations**: `array_key_exists()` vs `isset()`, repeated file openings


### 🔒 Security

- **SQL injections**: Unescaped variables in queries
- **XSS vulnerabilities**: Unescaped output from `$_GET`/`$_POST`
- **Weak hashing**: `md5()` for passwords
- **Dangerous includes**: `include` based on user input


### 📏 Best Practices

- **PSR standards**: Lines too long (>120 characters)
- **Optimized SELECT**: Detects inefficient `SELECT *`
- **Unused variables**: Declared but never used
- **Repeated calculations**: Duplicate mathematical expressions


### ❌ Error Detection

- **Foreach on non-iterable**: Detects `foreach` usage on scalar variables (int, string, bool, null)


### Detection Examples

```php
// ❌ Detected issue: Sort function in loop - O(n²log n) complexity
foreach ($items as $item) {
    sort($data); // Very inefficient!
    usort($user_data, 'compare_func'); // Custom sort in loop
}
// Suggestion: Extract sort() outside loop

// ❌ Detected issue: Linear search in loop - O(n²) complexity
foreach ($items as $item) {
    if (in_array($item->id, $large_array)) { // Linear search
        echo "Found!";
    }
}
// Suggestion: Convert array to key-value or use array_flip() before loop

// ❌ Detected issue: Nested loops on same array - O(n²) complexity
foreach ($users as $user1) {
    foreach ($users as $user2) { // Same array!
        if ($user1->id !== $user2->id) {
            echo "Different users";
        }
    }
}
// Suggestion: Review algorithm to avoid quadratic traversal

// ❌ Detected issue: Repeated object creation with constant arguments
for ($i = 0; $i < 1000; $i++) {
    $date = new DateTime('2023-01-01'); // Same arguments!
    $logger = Logger::getInstance(); // Singleton called repeatedly
}
// Suggestion: Extract object creation outside loop

// ❌ Detected issue: Repeated superglobal access in loop
foreach ($items as $item) {
    $sessionData = $_SESSION['user_data']; // Slow access
    $userId = $_GET['id']; // Repeated superglobal access
}
// Suggestion: Store superglobals in local variables before loop

// ❌ Detected issue: Unused global variable
function test_function() {
    global $unused_var; // Never used in function
    echo "Function body";
}
// Suggestion: Remove unused global declaration

// ❌ Detected issue: Global variable could be local
function process_data() {
    global $local_candidate; // Only used in this function
    $local_candidate = "process here";
    return $local_candidate;
}
// Suggestion: Convert to local variable

// ❌ Detected issue: Heavy I/O in loop
for ($i = 0; $i < 1000; $i++) {
    $content = file_get_contents("file_$i.txt"); // Very slow!
    $files = glob("*.txt"); // Filesystem scan in loop
}
// Suggestion: Extract file_get_contents() outside loop and cache result

// ❌ Detected issue: foreach on non-iterable variable
$scalar = 42;
foreach ($scalar as $item) {
    echo $item; // ERROR: Cannot iterate over scalar
}
// Suggestion: Ensure $scalar is an array or iterable object

// ❌ Detected issue: Large array not released
$large_array = range(1, 1000000);
$result = array_sum($large_array);
// Suggestion: Add unset($large_array)

// ❌ Detected issue: Query inside loop (N+1)
foreach ($users as $user) {
    $posts = mysql_query("SELECT * FROM posts WHERE user_id = $user[id]");
}

// ❌ Detected issue: Inefficient XPath
$nodes = $xml->xpath('//*[@active="true"]'); // Very slow

// ✅ Recommended solution
$nodes = $xml->xpath('/root/items/item[@active="true"]'); // Faster
```


## Development

### Project Structure

```
phpoptimizer/
├── phpoptimizer/                    # Main source code
│   ├── __init__.py                 # Package initialization
│   ├── __main__.py                 # Direct execution support
│   ├── cli.py                      # Command-line interface
│   ├── simple_analyzer.py          # Main analyzer orchestrator
│   ├── config.py                   # Configuration management
│   ├── reporter.py                 # Report generators (console, HTML, JSON)
│   ├── parser.py                   # PHP parsing utilities
│   ├── analyzers/                  # Modular analyzer system
│   │   ├── __init__.py            # Analyzer package init
│   │   ├── base_analyzer.py       # Abstract base analyzer
│   │   ├── loop_analyzer.py       # Loop performance analysis
│   │   ├── security_analyzer.py   # Security vulnerability detection
│   │   ├── error_analyzer.py      # Syntax and runtime error detection
│   │   ├── performance_analyzer.py # General performance optimization
│   │   ├── memory_analyzer.py     # Memory management analysis
│   │   └── code_quality_analyzer.py # Code quality and best practices
│   └── rules/                      # Configuration-based rules (extensible)
│       ├── __init__.py            # Rules package init
│       ├── performance.py         # Performance rule definitions
│       ├── security.py            # Security rule definitions
│       └── best_practices.py      # Best practice rule definitions
├── tests/                          # Comprehensive unit test suite
│   ├── __init__.py                # Test package init
│   ├── test_analyzer.py           # Core analyzer tests
│   ├── test_imports.py            # Import validation tests
│   └── test_memory_management.py  # Memory analysis tests
├── examples/                       # PHP test files with detectable issues
│   ├── performance_test.php       # Advanced performance issues
│   ├── xpath_test.php             # XPath/XML optimization examples
│   ├── unset_test.php             # Memory management test cases
│   ├── security_test.php          # Security vulnerability examples
│   └── demo_complet.php           # Comprehensive demonstration file
└── .vscode/                        # VS Code configuration
    └── tasks.json                  # Predefined analysis tasks
```

### Modular Architecture

The analyzer uses a **modular architecture** with specialized analyzers for different concern areas:

#### 🔍 Base Analyzer (`base_analyzer.py`)
- **Abstract base class** for all specialized analyzers
- Common utilities for pattern matching, issue creation, and code parsing
- Shared methods for comment detection, string handling, and context analysis

#### 🔄 Loop Analyzer (`loop_analyzer.py`)
- **Algorithmic complexity detection**: O(n²) patterns, nested loops
- **Sort functions in loops**: `sort()`, `usort()`, `array_multisort()` etc.
- **Linear search optimization**: `in_array()`, `array_search()` in loops
- **Heavy I/O operations**: File system calls inside iterations
- **Object creation patterns**: Repeated instantiation with constant arguments

#### 🛡️ Security Analyzer (`security_analyzer.py`)
- **SQL injection detection**: Unescaped variables in database queries
- **XSS vulnerability detection**: Unescaped output from user input
- **Weak cryptography**: `md5()` for password hashing
- **Dangerous file operations**: User-controlled include/require statements

#### ❌ Error Analyzer (`error_analyzer.py`)
- **Runtime error prevention**: `foreach` on non-iterable variables
- **Type checking**: Scalar values used as arrays or objects
- **Scope analysis**: Variable usage tracking across function boundaries

#### ⚡ Performance Analyzer (`performance_analyzer.py`)
- **Function optimization**: Deprecated and obsolete function usage
- **String operations**: Inefficient concatenation and regex patterns
- **Array operations**: `array_key_exists()` vs `isset()` comparisons
- **Error suppression**: Performance impact of `@` operator usage

#### 💾 Memory Analyzer (`memory_analyzer.py`)
- **Large array management**: Missing `unset()` calls for big datasets (>10k elements)
- **Resource leak detection**: Unclosed file handles, database connections
- **Excessive memory usage**: File operations on large datasets
- **Circular reference detection**: Self-referencing object patterns

#### 📊 Code Quality Analyzer (`code_quality_analyzer.py`)
- **Global variable optimization**: Unused globals, variables that should be local
- **PSR compliance**: Line length, coding standards
- **Code organization**: Repeated calculations, unused variables
- **Best practices**: SQL query optimization, superglobal usage

### Analyzer Orchestration

The main `SimpleAnalyzer` class coordinates all specialized analyzers:

```python
# Simplified orchestration logic
analyzers = [
    LoopAnalyzer(),
    SecurityAnalyzer(), 
    ErrorAnalyzer(),
    PerformanceAnalyzer(),
    MemoryAnalyzer(),
    CodeQualityAnalyzer()
]

for analyzer in analyzers:
    issues.extend(analyzer.analyze(content, file_path, lines))

# Deduplication and filtering
return self._deduplicate_issues(issues)
```


### Analyzer Orchestration

The main `SimpleAnalyzer` class coordinates all specialized analyzers:

```python
# Simplified orchestration logic
analyzers = [
    LoopAnalyzer(),
    SecurityAnalyzer(), 
    ErrorAnalyzer(),
    PerformanceAnalyzer(),
    MemoryAnalyzer(),
    CodeQualityAnalyzer()
]

for analyzer in analyzers:
    issues.extend(analyzer.analyze(content, file_path, lines))

# Deduplication and filtering
return self._deduplicate_issues(issues)
```

### Adding Custom Analyzers

The modular architecture makes it easy to add new analyzers:

```python
from phpoptimizer.analyzers.base_analyzer import BaseAnalyzer

class CustomAnalyzer(BaseAnalyzer):
    """Custom analyzer for specific patterns"""
    
    def analyze(self, content: str, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """Analyze custom patterns in PHP code"""
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            # Custom analysis logic
            if self._detect_custom_pattern(line):
                issues.append(self._create_issue(
                    'custom.pattern_detected',
                    'Custom pattern detected',
                    file_path,
                    line_num,
                    'warning',
                    'custom',
                    'Consider refactoring this pattern',
                    line.strip()
                ))
        
        return issues
    
    def _detect_custom_pattern(self, line: str) -> bool:
        """Implement custom pattern detection"""
        # Your custom logic here
        return False
```

### Features Tested and Validated

✅ Detection of **25+ different types of issues** across 6 specialized analyzers
✅ Memory management: detection of missing `unset()` with scope analysis
✅ Algorithmic complexity: O(n²) detection and optimization suggestions
✅ Heavy I/O functions: `file_get_contents`, `glob`, `curl_exec` in loops
✅ Error prevention: `foreach` on non-iterable variables with type tracking
✅ Security scanning: SQL injection, XSS, weak hashing detection
✅ Inefficient XPath patterns inside loops with performance impact analysis
✅ SQL queries inside loops (N+1 issue) with contextual suggestions
✅ Obsolete PHP functions (mysql_*, ereg, etc.) with modern alternatives
✅ Multi-format reports (console, HTML, JSON) with detailed descriptions
✅ Modular architecture with 6 specialized analyzers
✅ Comprehensive unit tests with pytest (100% coverage for core features)
✅ CLI interface with Click and advanced configuration options

### Running Tests

```bash
python -m pytest tests/
```


### Debugging in VS Code

Use F5 to start the debugger with the predefined configuration.

## Contribution

Contributions are welcome! See the CONTRIBUTING.md file for more details.

## License

MIT License – see the LICENSE file for more details.

<div style="text-align: center">⁂</div>

[^1]: README.md

