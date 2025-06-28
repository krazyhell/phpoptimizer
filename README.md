# PHP Optimizer

PHP Optimizer is a static analyzer and optimizer for PHP code, written in Python. It detects common security vulnerabilities, performance issues, and best practice violations in PHP projects, and generates detailed reports with improvement suggestions.

## Features
- Detects security vulnerabilities (SQL injection, XSS, weak password hashing, dangerous file inclusion)
- Identifies performance issues (inefficient loops, repeated calculations, unused variables, inefficient string concatenation, inefficient XPath, slow DOM queries, inefficient regex, etc.)
- Checks for PHP and PSR best practices (line length, unused variables, SELECT *)
- Generates reports in console, JSON, and HTML (with Copy Path button for each problematic file)
- CLI interface with Click
- Supports Blade templates and ignores Blade directives for error suppression detection
- Extensible rule system (add your own rules)
- Detailed suggestions and code examples for each issue

## Installation

```bash
# Clone the repository
 git clone https://github.com/your-username/phpoptimizer.git
 cd phpoptimizer

# Create a virtual environment (recommended)
 python -m venv venv
 source venv/bin/activate  # Linux/Mac
 # or .\venv\Scripts\Activate  # Windows

# Install dependencies
 pip install -r requirements.txt
 pip install -e .
```

## Usage

### CLI

```sh
python -m phpoptimizer analyze <file_or_directory> [--recursive] [--output-format html|json|console] [--output <file>]
```

#### Example

```sh
python -m phpoptimizer analyze examples/ --recursive --output-format html --output report.html
```

### VS Code Tasks
- Use the predefined tasks in `.vscode/tasks.json` for quick analysis and HTML report generation.

### Features
- **Copy Path button in HTML reports**: Click to copy the file path of each problematic file (with clipboard fallback and visual feedback).

## Configuration

- Default configuration is managed in `phpoptimizer/config.py`.
- You can customize rules, severity levels, excluded paths, and file extensions.
- To save a custom config, use the `Config.save_default_config()` method or edit the config file directly.

## Advanced Usage

- **Thresholds**: Adjust parameters like max array size, max loop nesting, etc. in the config.
- **Exclusions**: Exclude files or folders from analysis by editing the config.
- **Custom Rules**: Add new detection rules in `phpoptimizer/simple_analyzer.py` or as modules in `phpoptimizer/rules/`.
- **Unit Tests**: Run `python -m pytest tests/` to validate all rules.

## Project Structure

- `phpoptimizer/` - Main package
  - `cli.py` - Command-line interface
  - `simple_analyzer.py` - Main simplified analyzer (add your rules here)
  - `parser.py` - PHP parser using phply
  - `config.py` - Configuration management
  - `reporter.py` - Report generation (console, JSON, HTML)
  - `rules/` - Modular rules system
    - `performance.py` - Performance rules
    - `security.py` - Security rules
    - `best_practices.py` - Best practices rules
- `examples/` - Example PHP files (for testing and validation)
- `tests/` - Unit tests (pytest)

## Detection Examples

### Memory Management
```php
// ❌ DETECTED: Large array not released (performance.memory_management)  
$large_array = range(1, 1000000);  // 1M elements
$result = array_sum($large_array);
// 💡 Suggestion: Add unset($large_array) after use
```

### N+1 Problem
```php  
// ❌ DETECTED: Query in loop (performance.query_in_loop)
foreach ($users as $user) {
    $posts = mysql_query("SELECT * FROM posts WHERE user_id = {$user['id']}");
}
// 💡 Suggestion: Use a grouped query or JOIN
```

### Inefficient XPath
```php
// ❌ DETECTED: Slow XPath (performance.inefficient_xpath)
$nodes = $xml->xpath('//*[@active="true"]//value');  // Double descendant
// 💡 Suggestion: $xml->xpath('/root/items/item[@active="true"]/value');
```

## Contribution

- See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on reporting bugs, proposing features, and contributing code or rules.

## License
MIT
