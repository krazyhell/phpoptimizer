# PHP Optimizer

PHP Optimizer is a static analyzer and optimizer for PHP code, written in Python. It detects common security vulnerabilities, performance issues, and best practice violations in PHP projects, and generates detailed reports with improvement suggestions.

## Features
- Detects security vulnerabilities (SQL injection, XSS, weak password hashing, dangerous file inclusion)
- Identifies performance issues (inefficient loops, repeated calculations, unused variables, inefficient string concatenation, etc.)
- Checks for PHP and PSR best practices
- Generates reports in console, JSON, and HTML (with copy path button for each problematic file)
- CLI interface with Click
- Supports Blade templates and ignores Blade directives for error suppression detection

## Usage

### CLI

```sh
python -m phpoptimizer analyze <file_or_directory> [--recursive] [--output-format html|json|console] [--output <file>]
```

### Example

```sh
python -m phpoptimizer analyze examples/ --recursive --output-format html --output report.html
```

### Features
- Copy Path button in HTML reports: Click to copy the file path of each problematic file (with clipboard fallback and visual feedback).

## Project Structure

- `phpoptimizer/` - Main package
  - `cli.py` - Command-line interface
  - `simple_analyzer.py` - Main simplified analyzer
  - `parser.py` - PHP parser using phply
  - `config.py` - Configuration management
  - `reporter.py` - Report generation (console, JSON, HTML)
  - `rules/` - Optimization rules
    - `performance.py` - Performance rules
    - `security.py` - Security rules
    - `best_practices.py` - Best practices rules
- `examples/` - Example PHP files
- `tests/` - Unit tests

## Requirements
- Python 3.8+
- Click
- phply
- Colorama

## License
MIT
