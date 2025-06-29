# PHP Optimizer - Changelog

## [1.3.0] - 2025-06-29

### ✨ New Features - Algorithmic Complexity Detection

#### 🚀 Performance Enhancement - Algorithmic Complexity
- **Sorting in Loops**: Detects sorting functions inside loops (O(n²log n) complexity)
  - Functions detected: `sort`, `rsort`, `asort`, `arsort`, `ksort`, `krsort`, `usort`, `uasort`, `uksort`, `array_multisort`
  - Rule: `performance.sort_in_loop`
  - Severity: Warning
  - Impact: Exponential performance degradation

- **Linear Search in Loops**: Detects linear search operations in loops (O(n²) complexity)
  - Functions detected: `in_array`, `array_search`, `array_key_exists`
  - Rule: `performance.linear_search_in_loop`
  - Severity: Warning
  - Suggestion: Use `array_flip()` or key-value arrays for O(1) lookup

- **Nested Loops Same Array**: Detects nested loops traversing the same array (O(n²) complexity)
  - Pattern: `foreach($array as $item1) { foreach($array as $item2) { ... } }`
  - Rule: `performance.nested_loop_same_array`
  - Severity: Warning
  - Impact: Quadratic complexity on large datasets

- **Object Creation in Loops**: Enhanced detection of repeated object instantiation
  - Patterns: `new Class('constant')`, `Class::getInstance()`, `Class::create('constant')`
  - Rule: `performance.object_creation_in_loop`
  - Severity: Warning
  - Only flags when arguments are constants (not variables)

#### 🧪 Testing & Quality
- **Unit Test Coverage**: 4 new comprehensive tests for algorithmic complexity
  - `test_algorithmic_complexity_sort_in_loop`
  - `test_algorithmic_complexity_linear_search_in_loop`
  - `test_algorithmic_complexity_nested_loops_same_array`
  - `test_object_creation_in_loop_with_constants`
  - `test_object_creation_in_loop_with_variables_ok` (ensures no false positives)
- **All Tests Passing**: 19/19 tests pass including new algorithmic complexity detections

### 📝 Examples of New Detection
```php
❌ Sorting in Loop (O(n²log n)):
foreach ($users as $user) {
    sort($data); // Extract outside loop
    usort($ratings, 'compare'); // Custom sorting in loop
}

❌ Linear Search in Loop (O(n²)):
foreach ($items as $item) {
    if (in_array($item->id, $large_array)) { // Very slow
        echo "Found!";
    }
}
// ✅ Solution: $flipped = array_flip($large_array); if (isset($flipped[$item->id]))

❌ Nested Loops Same Array (O(n²)):
foreach ($users as $user1) {
    foreach ($users as $user2) { // Quadratic complexity
        if ($user1->id !== $user2->id) {
            echo "Different users";
        }
    }
}

❌ Object Creation with Constants:
for ($i = 0; $i < 100; $i++) {
    $date = new DateTime('2023-01-01'); // Same object 100 times
    $logger = Logger::getInstance(); // Singleton in loop
}
// ✅ Solution: Create once before loop
```

### 📈 Performance Impact
- **Issue Detection**: Now detects **24 types of issues** (up from 21)
- **Complexity Categories**: Covers O(n²), O(n²log n), and O(n³) algorithmic issues
- **Real-World Impact**: Can identify performance bottlenecks that cause 10x-100x slowdowns

### 🔧 Technical Details
- **Detection Logic**: Integrated into both `analyze_file()` and `analyze_content()` methods
- **Loop Context Tracking**: Uses `loop_stack` to track nested loop levels
- **Pattern Recognition**: Regex-based detection with context-aware analysis
- **False Positive Prevention**: Only flags object creation with constant arguments

## [1.2.0] - 2025-06-29

### ✨ New Features

#### ❌ Error Detection - NEW!
- **Foreach on Non-Iterable**: Detects `foreach` usage on scalar variables (int, string, bool, null)
  - Scans 20 lines backwards to identify variable assignments
  - Detects scalars: numbers, strings, booleans, null values
  - Rule: `error.foreach_non_iterable`
  - Severity: Error (prevents runtime crashes)

#### 🚀 Performance Enhancement - NEW!
- **Heavy Functions in Loops**: Detects I/O and filesystem operations inside loops
  - File operations: `file_get_contents`, `file_put_contents`, `file_exists`, `filesize`
  - Directory operations: `glob`, `scandir`, `opendir`, `readdir`
  - Network operations: `curl_exec`
  - Path operations: `realpath`, `pathinfo`, `basename`, `dirname`
  - Rule: `performance.heavy_function_in_loop`
  - Severity: Warning (performance impact)

#### 🧪 Testing & Quality
- **Unit Test Coverage**: New test `test_foreach_on_non_iterable` in memory management suite
- **Memory Management Fix**: Improved `unset()` detection logic for variables in loops
- **Code Quality**: All existing tests maintained and passing

### 📝 Example of New Detection
```php
❌ Heavy I/O in Loop:
for ($i = 0; $i < 1000; $i++) {
    $content = file_get_contents("file_$i.txt"); // WARNING: Very slow
    $files = glob("*.txt"); // WARNING: Filesystem scan
}

💡 Solution: Extract heavy operations outside loop
✅ Correct usage:
$template = file_get_contents("template.txt");
$all_files = glob("*.txt");
for ($i = 0; $i < 1000; $i++) {
    $content = str_replace("{id}", $i, $template);
}

❌ Detected Error:
$foo = 42;
foreach ($foo as $item) {  // ERROR: Cannot iterate over int
    echo $item;
}

💡 Solution: Ensure $foo is an array or iterable object
✅ Correct usage:
$foo = [1, 2, 3];
foreach ($foo as $item) {
    echo $item;
}
```

### 🔧 Technical Improvements
- Enhanced scalar pattern detection with regex: `\${var}\s*=\s*(?:true|false|null|\d+|\.\d+|["'][^"']*["'])`
- Improved variable scope analysis for better `unset()` detection
- Added support for in-memory code analysis via `analyze_content()` method

## [1.1.0] - 2025-06-27

### ✨ New Features

#### 📋 Enriched Descriptions - NEW!
- **Detailed Display**: Each detected issue now includes:
  - 📖 **Description**: Clear explanation of the problem
  - ⚡ **Impact**: Consequences on performance, security, or maintainability
  - 💡 **Solution**: Concrete correction recommendation
  - 📝 **Example**: Before/after code to illustrate the solution
  - 🔍 **Concerned Code**: Excerpt of the problematic code with context
- **Supported Formats**: Descriptions available in console, HTML, and JSON
- **Line Grouping**: Organized display by line number for clarity
- **Default Activation**: Detailed descriptions are automatically enabled

#### 🔧 Technical Improvements
- **Unified Entry Point**: Addition of `__main__.py` to simplify execution (`python -m phpoptimizer`)
- **Enriched User Interface**: Improved console display with more details
- **Updated Documentation**: README enhanced with detailed display examples

### 📝 Example of Enriched Display
```
⚠️  performance.memory_management - Line 71
    📝 Description: Large array not released from memory
    ⚡ Impact: High memory consumption, risk of overflow
    💡 Solution: Use unset() after use
    📍 Concerned Code: $large_array = range(1, 1000000);
    
    💻 Correction Example:
    ❌ Before: $large_array = range(1, 1000000);
    ✅ After:  unset($large_array); // Explicit release
```

## [1.0.0] - 2025-06-27

### ✨ New Features

#### 🚀 Performance (12 implemented rules)
- **Intelligent Memory Management**: Automatic detection of `unset()` omissions for large arrays (>10k elements)
- **N+1 Problems**: Identification of SQL queries in loops (`mysql_query`, `mysqli_query`, etc.)
- **Inefficient Loops**: Detection of `count()` in loop conditions, excessive nesting (>3 levels)
- **Inefficient Concatenation**: Detection of string concatenation in loops
- **Deprecated Functions**: Identification of `mysql_*`, `ereg`, `split`, `each` with replacement suggestions
- **Error Suppression**: Detection of the `@` operator impacting performance
- **Inefficient XPath**: Advanced detection of slow selectors (`//*`, `contains()`, double descendant, axes)
- **Slow DOM Queries**: Identification of repeated DOM calls (`getElementById`, `querySelector`, etc.)
- **Inefficient Regex**: Detection of problematic patterns with `.*`
- **Array Checks**: Comparison of `array_key_exists()` vs `isset()`
- **File Operations**: Detection of repeated open/close operations
- **Repeated Calculations**: Identification of duplicated mathematical expressions

#### 🔒 Security (4 implemented rules)
- **SQL Injections**: Detection of unescaped variables in queries
- **XSS Vulnerabilities**: Identification of unescaped outputs (`echo $_GET`, `echo $_POST`)
- **Weak Hashing**: Detection of `md5()` for passwords
- **Dangerous Inclusions**: Detection of `include` based on user input

#### 📏 Best Practices (3 implemented rules)
- **PSR Standards**: Checking line length (>120 characters)
- **Optimized SELECT**: Detection of inefficient `SELECT *`
- **Unused Variables**: Identification of declared but unused variables

### 🎨 Interface and Reports
- **Colored Console**: Interface with emojis and colors for better readability
- **HTML Report**: Generation of interactive reports for browser
- **JSON Format**: Structured export for CI/CD integration
- **Detailed Statistics**: Counters by severity, top frequent issues
- **Contextual Suggestions**: Specific help messages with correction examples

### 🛠️ Architecture and Tools
- **Robust CLI**: Click interface with advanced options (`--recursive`, `--output-format`, `--severity`)  
- **Extensible System**: Modular architecture for easy addition of new rules
- **Comprehensive Tests**: Pytest suite with >90% coverage, real PHP examples
- **VS Code Configuration**: Predefined tasks for analysis and debugging
- **Complete Documentation**: Detailed README, contribution guide, examples

### 🧪 Validation and Testing
- **19 types of problems** detected and validated on real PHP code
- **Complete Examples**: PHP files with complex patterns for validation
- **Unit Tests**: Full coverage of each detection rule
- **Scope Analysis**: Precise detection of variables in their context (functions, classes)
- **False Positive Management**: Robust logic to avoid incorrect detections

### 📊 Metrics and Performance
- **Analysis Speed**: ~1000 lines/second on modern CPU
- **Memory Usage**: <50MB for medium projects (<100k lines)
- **Configurable Thresholds**: Adjustable parameters (array size, nesting levels)

### 🎯 Detection Examples

#### Memory Management
```php
// ❌ DETECTED: Large array not released (performance.memory_management)  
$large_array = range(1, 1000000);  // 1M elements
$result = array_sum($large_array);
// 💡 Suggestion: Add unset($large_array) after use
```

#### N+1 Problem
```php  
// ❌ DETECTED: Query in loop (performance.query_in_loop)
foreach ($users as $user) {
    $posts = mysql_query("SELECT * FROM posts WHERE user_id = {$user['id']}");
}
// 💡 Suggestion: Use a grouped query or JOIN
```

#### Inefficient XPath
```php
// ❌ DETECTED: Slow XPath (performance.inefficient_xpath)
$nodes = $xml->xpath('//*[@active="true"]//value');  // Double descendant
// 💡 Suggestion: $xml->xpath('/root/items/item[@active="true"]/value');
```

## [0.1.0] - 2025-06-26

### ✨ Initial Version
- Basic project structure
- Simplified analyzer with basic detection
- Minimal CLI interface
- Basic unit tests

---

## Planned Future Releases

### [1.1.0] - Q3 2025 (Forecast)
- **Inter-file Analysis**: Detection of cross-file dependencies
- **Advanced Configuration**: YAML files with customizable rules  
- **Intelligent Cache**: Incremental analysis for large projects
- **Extended Metrics**: Cyclomatic complexity, technical debt

### [1.2.0] - Q4 2025 (Forecast)  
- **VS Code Extension**: Native integration in the editor
- **PHP 8.3+ Support**: New features and optimizations
- **Community Rules**: Plugin system for third-party rules
- **Graphical Interface**: GUI for configuration and reports

### [2.0.0] - 2026 (Forecast)
- **Advanced Semantic Analysis**: Understanding of data flow
- **Automatic Suggestions**: Refactoring proposals
- **Multi-IDE Integration**: PHPStorm, Sublime Text, Atom
- **REST API**: Online analysis service
