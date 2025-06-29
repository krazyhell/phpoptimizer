# PHP Code Optimizer

A PHP code analysis and optimization tool written in Python with **modular architecture**.

## Features

- 🔍 **Advanced Static Analysis** – Detects **25+ types of issues** across 6 specialized domains
- 🏗️ **Modular Architecture** – Specialized analyzers for performance, security, memory, loops, errors, and code quality
- ⚡ **Memory Optimization** – Detects missing `unset()` calls for large arrays (>10k elements)
- ❌ **Error Prevention** – Detects `foreach` usage on non-iterable variables (scalars)
- 🗃️ **N+1 Detection** – Identifies inefficient SQL queries inside loops
- 🔄 **Algorithmic Complexity** – Detects O(n²) patterns and suggests O(1) optimizations
- 🎯 **Smart XPath Analysis** – Analyzes slow XPath selectors (`//*`, `contains()`, etc.)
- 🛡️ **Security Scanning** – SQL injection, XSS, weak hashing, dangerous includes
- 📊 **Multi-format Reports** – Colored console output, interactive HTML, JSON for CI/CD
- 🧪 **Extensible System** – Easy to add new analyzers and rules
- 🔧 **Comprehensive Testing** – Full test suite with real-world PHP examples


## Installation

```bash
# Clone the repository
git clone <your-repo>
cd phpoptimizer

# Create the virtual environment
python -m venv venv

# Activate the environment (Windows)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```


## Usage

### Analyze a PHP file

```bash
phpoptimizer analyze examples/performance_test.php --output-format console
```


### Analyze a folder

```bash
phpoptimizer analyze src/ --recursive --output-format html --output report.html
```


### Sample Output

```
============================================================
  PHP OPTIMIZER ANALYSIS REPORT
============================================================
📊 Statistics: 1 file, 20 issues detected
🎯 Severity: 3 errors, 13 warnings, 4 infos

📄 examples/performance_test.php
   📍 Line 5: foreach on non-iterable variable $scalar (assigned to scalar value)
   📍 Line 71: Large array $large_array (1,000,000 elements) not released
   📍 Line 11: SQL query inside loop (N+1 issue)
   📍 Line 23: count() in for loop condition (inefficient)

🏆 Top issues: performance.obsolete_function (4x), performance.memory_management (2x)
```


### Available Options

- `--recursive, -r`: Recursively analyze subfolders
- `--output-format`: Output format (console, json, html)
- `--output, -o`: Output file
- `--rules`: Custom rules configuration file
- `--severity`: Minimum severity level (info, warning, error)


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

