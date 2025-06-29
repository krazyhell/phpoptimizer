# PHP Code Optimizer

A PHP code analysis and optimization tool written in Python.

## Features

- 🔍 **Advanced Static Analysis** – Detects **19 types of issues** related to performance, security, and best practices
- ⚡ **Memory Optimization** – Detects missing `unset()` calls for large arrays (>10k elements)
- 🗃️ **N+1 Detection** – Identifies inefficient SQL queries inside loops
- 🔄 **Smart XPath** – Analyzes slow XPath selectors (`//*`, `contains()`, etc.)
- 📊 **Multi-format Reports** – Colored console output, interactive HTML, JSON for CI/CD
- 🎯 **Extensible Rules** – Modular architecture to add new rules
- 🧪 **Tested and Validated** – Comprehensive test suite with real-world examples


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
📊 Statistics: 1 file, 19 issues detected
🎯 Severity: 2 errors, 13 warnings, 4 infos

📄 examples/performance_test.php
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

The tool currently detects **over 15 types of issues** across several categories:

### 🚀 Performance

- **Inefficient loops**: `count()` in loop conditions, deeply nested loops
- **Queries in loops**: Detects N+1 issue (SQL queries inside loops)
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


### Detection Examples

```php
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
├── phpoptimizer/           # Main source code
│   ├── __init__.py
│   ├── cli.py             # Command-line interface
│   ├── simple_analyzer.py # Main analyzer (pattern detection)
│   ├── config.py          # Configuration
│   ├── reporter.py        # Report generators (console, HTML, JSON)
│   └── rules/             # Optimization rules (future extensibility)
├── tests/                 # Unit tests
├── examples/              # PHP examples with detectable issues
│   ├── performance_test.php  # Advanced performance issues
│   ├── xpath_test.php       # XPath/XML issues
│   └── unset_test.php       # Memory management tests
└── .vscode/               # VS Code config with tasks.json
```


### Features Tested and Validated

✅ Detection of **19 different types of issues**
✅ Memory management: detection of missing `unset()`
✅ Inefficient XPath patterns inside loops
✅ SQL queries inside loops (N+1 issue)
✅ Obsolete PHP functions (mysql_*, ereg, etc.)
✅ Multi-format reports (console, HTML, JSON)
✅ Unit tests with pytest
✅ CLI interface with Click

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

