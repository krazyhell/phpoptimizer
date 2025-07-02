# PHP Code Optimizer

A PHP code analysis and optimization tool written in Python with a **modular architecture** and **advanced suggestion system**.

## ✨ New Features v2.2.0

### 🎯 **Detailed Fix Suggestions**
- **Before/After Examples**: Real PHP code with applied corrections
- **Contextual Solutions**: Suggestions tailored to the exact detected problem
- **One-Click Copy**: Buttons to copy correction examples
- **Modern Interface**: Interactive HTML reports with responsive design

### 💡 **Available Suggestion Types**
- **🔐 Security**: SQL injection → Prepared statements, XSS → htmlspecialchars()
- **⚡ Performance**: Loops → count() optimization, Memory → unset()
- **📚 Best Practices**: Documentation → PHPDoc, Naming → Conventions
- **🔧 Quality**: Unused variables → Cleanup, Null checks → try/catch

## 🚀 Main Features

- 🔍 **Advanced Static Analysis** – Detects **25+ problem types** with fix suggestions
- 🏗️ **Modular Architecture** – Specialized analyzers for performance, security, memory, loops, errors
- 💡 **Smart Suggestions** – Ready-to-copy PHP code examples
- ⚡ **Memory Optimization** – Detects missing `unset()` for large arrays (>10k elements)
- ❌ **Error Prevention** – Detects `foreach` on non-iterable variables
- 🗃️ **N+1 Detection** – Identifies inefficient SQL queries in loops
- 🔄 **Algorithmic Complexity** – Detects O(n²) patterns and suggests O(1) optimizations
- 🎯 **Smart XPath Analysis** – Analyzes slow XPath selectors (`//*`, `contains()`, etc.)
- 🛡️ **Security Scanner** – SQL injection, XSS, weak hashing, dangerous includes
- 📊 **Multi-format Reports** – Colored console, interactive HTML, JSON for CI/CD
- 🧪 **Extensible System** – Easy to add new analyzers and rules
- 🔧 **Comprehensive Tests** – Test suite with real-world PHP examples

## 📋 Installation

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

## 🎮 Usage

### Analyze a PHP file with detailed suggestions

```bash
phpoptimizer analyze examples/performance_test.php --verbose
```

### Generate an interactive HTML report

```bash
phpoptimizer analyze examples/ --output-format html --output report.html
```

### Analyze a folder recursively

```bash
phpoptimizer analyze src/ --recursive --output-format html --output report.html
```

## 💡 Suggestion Examples

### 🔐 Security - SQL Injection
```php
// ❌ Vulnerable code detected
$result = mysql_query("SELECT * FROM users WHERE id = " . $_GET['id']);

// ✅ Suggested fix
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
$stmt->execute([$_GET['id']]);
$result = $stmt->fetchAll();
```

### ⚡ Performance - Inefficient Loops
```php
// ❌ Inefficient code detected
for ($i = 0; $i < count($array); $i++) {
    echo $array[$i];
}

// ✅ Suggested fix
$length = count($array);
for ($i = 0; $i < $length; $i++) {
    echo $array[$i];
}
// Or even better with foreach
foreach ($array as $value) {
    echo $value;
}
```

### 🧠 Memory Management
```php
// ❌ Memory-hungry code
$huge_array = range(1, 1000000);
$result = array_sum($huge_array);
return $result; // $huge_array remains in memory

// ✅ Suggested fix
$huge_array = range(1, 1000000);
$result = array_sum($huge_array);
unset($huge_array); // Frees memory immediately
return $result;
```

## 📊 Example Console Output

```
============================================================
  PHP OPTIMIZER ANALYSIS REPORT
============================================================
📊 General stats: 1 file analyzed, 12 issues detected
🎯 By severity: 2 errors, 3 warnings, 7 infos

📄 test_performance.php
   📍 Line 13: count() call in for loop condition (inefficient)
      💡 Solution: Avoid calling count() on every loop iteration.
      📝 Fix example:
         // ❌ Inefficient code - count() called every iteration
         // for ($i = 0; $i < count($array); $i++) { echo $array[$i]; }
         
         // ✅ Optimized code - count() called once
         $length = count($array);
         for ($i = 0; $i < $length; $i++) { echo $array[$i]; }

🏆 Top issues: performance.inefficient_loops (3x), security.sql_injection (2x)
```

## ⚙️ Available Options

- `--verbose, -v`: Detailed output with suggestions and fix examples
- `--recursive, -r`: Recursively analyze subfolders
- `--output-format`: Output format (console, json, html)
- `--output, -o`: Output file
- `--rules`: Custom rules configuration file
- `--severity`: Minimum severity level (info, warning, error)
- `--exclude-rules`: Exclude specific rules from the report (e.g. `--exclude-rules=best_practices.missing_docstring`)
- `--include-rules`: Only include specified rules (e.g. `--include-rules=performance.unused_variables,security.sql_injection`)

### 🎯 Filter Detected Issue Types

You can choose to exclude or target specific types of issues during analysis:

- **Exclude detection of uncommented functions** :
  ```bash
  python -m phpoptimizer analyze myfile.php --exclude-rules=best_practices.missing_docstring
  ```
- **Show only security issues** :
  ```bash
  python -m phpoptimizer analyze myfile.php --include-rules=security.sql_injection,security.xss_vulnerability
  ```

### 🏷️ Example Rule Names for Filtering

You can use the following rule names with `--include-rules` or `--exclude-rules`:

- `performance.constant_propagation` — Replace variables assigned to a constant value with their literal value
- `performance.inefficient_loops` — Detect inefficient loop patterns (e.g. count() in loop conditions, deep nesting)
- `performance.unused_variables` — Detect variables that are declared but never used
- `performance.repeated_calculations` — Detect repeated identical calculations that could be cached
- `performance.large_arrays` — Detect potentially large array declarations
- `performance.unused_global_variable` — Detect global variables declared but never used in a function
- `performance.global_could_be_local` — Detect global variables that could be local to a function
- `security.sql_injection` — Detect possible SQL injection vulnerabilities
- `security.xss_vulnerability` — Detect possible XSS vulnerabilities (unescaped output)
- `security.weak_password_hashing` — Detect use of weak password hashing (e.g. md5)
- `best_practices.psr_compliance` — Detect code that does not comply with PSR standards (e.g. line length)
- `best_practices.function_complexity` — Detect functions that are too complex (too many parameters, etc.)
- `best_practices.missing_docstring` — Detect public functions missing documentation
- `best_practices.line_length` — Detect lines that are too long (>120 characters)
- `best_practices.naming` — Detect non-descriptive or generic variable names
- `best_practices.function_naming` — Detect non-descriptive function names
- `best_practices.too_many_parameters` — Detect functions with too many parameters
- `best_practices.complex_condition` — Detect overly complex conditions (e.g. too many && or ||)
- `best_practices.multiple_statements` — Detect multiple statements on a single line
- `best_practices.brace_style` — Detect opening braces on a separate line (non K&R style)
- `error.foreach_non_iterable` — Detect foreach used on a non-iterable variable
- `dead_code.unreachable_after_return` — Detect unreachable code after return/exit/die/throw statements
- `dead_code.always_false_condition` — Detect always-false conditional blocks
- `dead_code.unreachable_after_break` — Detect unreachable code after break/continue statements
- `analyzer.error` — Internal error in an analyzer (for debugging)

> You can find the rule name in the `rule_name` field of each issue in the report.

## 🌐 Interactive HTML Report

The new HTML report offers a modern and interactive experience :

### 🎨 Visual Features
- **Modern Design**: Responsive interface with gradients and animations
- **Statistics Dashboard**: Metric cards colored by severity
- **Intuitive Navigation**: Clear organization by file and line

### 🔧 Interactive Features
- **📋 One-Click Copy**: Buttons to copy fix examples
- **📂 Quick Navigation**: Copy file paths
- **✅ Visual Feedback**: Action confirmation with animations
- **📝 Detailed Examples**: PHP code formatted with syntax highlighting

### 📱 Responsive Design
- Desktop, tablet, and mobile compatible
- Optimized for all modern browsers
- Accessible and ergonomic interface

## 🧪 Supported Analysis Types


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
- **Dead code elimination**: Detects unreachable code after return/exit/die/throw statements
- **Always-false conditions**: Identifies conditional blocks that will never execute
- **Unreachable code after break/continue**: Code that follows break or continue statements


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

// ❌ Detected issue: Dead code after return
function processData($input) {
    if ($input === null) {
        return false;
        echo "This will never execute"; // Dead code
        $cleanup = true; // Dead code
    }
    return process($input);
}
// Suggestion: Remove unreachable code after return/exit/die/throw

// ❌ Detected issue: Always-false condition
if (false) {
    echo "This code is never executed"; // Dead code
    $result = calculateValue(); // Dead code
}
// Suggestion: Remove or fix the always-false condition

// ❌ Detected issue: Code after break/continue
foreach ($items as $item) {
    if ($item->skip) {
        continue;
        echo "Unreachable"; // Dead code after continue
    }
    process($item);
}
// Suggestion: Remove code after break/continue statements

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
│   │   ├── code_quality_analyzer.py # Code quality and best practices
│   │   └── dead_code_analyzer.py  # Dead code detection and elimination
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
- **Dead code detection**: Unreachable code after flow control statements

#### ☠️ Dead Code Analyzer (`dead_code_analyzer.py`)
- **Flow control analysis**: Code after return, exit, die, throw statements
- **Conditional logic**: Always-false conditions (if(false), while(0), etc.)
- **Loop control**: Unreachable code after break/continue statements
- **Exception handling**: Dead code in try/catch/finally blocks

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
    CodeQualityAnalyzer(),
    DeadCodeAnalyzer()
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
    CodeQualityAnalyzer(),
    DeadCodeAnalyzer()
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

✅ Detection of **25+ different types of issues** across 7 specialized analyzers
✅ Memory management: detection of missing `unset()` with scope analysis
✅ Algorithmic complexity: O(n²) detection and optimization suggestions
✅ Heavy I/O functions: `file_get_contents`, `glob`, `curl_exec` in loops
✅ Error prevention: `foreach` on non-iterable variables with type tracking
✅ Security scanning: SQL injection, XSS, weak hashing detection
✅ Inefficient XPath patterns inside loops with performance impact analysis
✅ SQL queries inside loops (N+1 issue) with contextual suggestions
✅ Obsolete PHP functions (mysql_*, ereg, etc.) with modern alternatives
✅ Dead code elimination: Detection of unreachable code after flow control statements
✅ Always-false conditions: Identification of conditional blocks that never execute
✅ Multi-format reports (console, HTML, JSON) with detailed descriptions
✅ Modular architecture with 7 specialized analyzers
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

