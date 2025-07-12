# PHP Code Optimizer

A PHP code analysis and optimization tool written in Python with a **modular architecture** and **advanced suggestion system**.

## ✨ New Features v2.5.1

### 🎯 **Smart Filtering by Categories and Severity Weights** (NEW!)
- **7 Rule Categories**: Security (critical), Error (high), Performance.Critical (high), Performance.General (medium), Memory (medium), Code_Quality (low), PSR (very low)
- **Intelligent Filtering**: Target specific types of issues with `--include-categories=security,error` or `--min-weight=3`
- **Use Case Profiles**: Security audit, performance optimization, code review, CI/CD integration
- **Legacy Compatibility**: Existing `--include-rules`/`--exclude-rules` options still supported
- **Streamlined Workflow**: Replace tedious individual rule selection with smart category-based filtering

### 🎯 **PHP Version-Aware Type Hints**
- **Multi-Version Support**: Automatically adapts suggestions for PHP 7.0, 7.1, 7.4, 8.0, 8.1, 8.2+
- **Smart Type Inference**: Detects missing parameter and return types with contextual analysis
- **JIT Optimization**: Improves performance up to 15% with proper type hints on PHP 8+ JIT
- **Union Types**: `int|float` for PHP 8.0+, converts to `float` for older versions
- **Nullable Types**: `?string` suggested only for PHP 7.1+, avoided for PHP 7.0
- **Mixed Type**: Suggested only for PHP 8.0+, alternatives provided for older versions

### 🚀 **Intelligent Type Suggestions**
- **Parameter Analysis**: Detects array usage (`foreach`, `count`), arithmetic (`+`, `-`, `*`), string operations (`trim`, `concat`)
- **Return Type Detection**: Analyzes return statements for `bool`, `int`, `string`, `array`, `?mixed` inference
- **Version Compatibility**: CLI option `--php-version 7.4` to target specific PHP versions
- **Backward Compatibility**: Suggestions remain valid when upgrading PHP versions

### 🔄 **Intelligent Loop Fusion** 
- **Smart Detection**: Identifies consecutive loops that can be merged for better performance
- **Variable Adaptation**: Automatically adapts variable names in fusion suggestions  
- **Interference Prevention**: Prevents unsafe fusions when variables would conflict
- **Pattern Recognition**: Handles different foreach patterns (with/without keys)
- **Performance Boost**: Reduces loop overhead and improves cache locality

### 📊 **Repetitive Array Access Optimization**
- **Smart Detection**: Identifies repeated access to the same array/object paths
- **Automatic Variable Naming**: Generates descriptive temporary variable names
- **Modification Awareness**: Avoids optimization when values may change between accesses
- **Multi-Scope Analysis**: Works within functions, methods, and global code
- **Performance Gain**: Reduces redundant array lookups and improves code readability

### 🎯 **Detailed Fix Suggestions**
- **Before/After Examples**: Real PHP code with applied corrections
- **Contextual Solutions**: Suggestions tailored to the exact detected problem
- **Version-Aware Examples**: PHP code adapted to your target version
- **Modern Interface**: Interactive HTML reports with responsive design

### 🚀 **Dynamic Calls Optimization**
- **Smart Detection**: Identifies dynamic method/function calls that can be replaced with direct calls
- **Performance Boost**: Converts `$object->$method()` → `$object->methodName()` and `$function()` → `functionName()`
- **Confidence Analysis**: Only suggests optimizations for variables with constant values
- **Reassignment Aware**: Avoids suggestions when variables are modified or conditionally set
- **Real-world Impact**: 5-15% performance improvement on repetitive operations

### 💡 **Available Suggestion Types**
- **🎯 Type Hints**: Parameter types, return types, nullable types, union types (version-aware)
- **🔐 Security**: SQL injection → Prepared statements, XSS → htmlspecialchars()
- **⚡ Performance**: Loops → count() optimization, Memory → unset(), Dynamic calls → Direct calls
- **📚 Best Practices**: Documentation → PHPDoc, Naming → Conventions
- **🔧 Quality**: Unused variables → Cleanup, Null checks → try/catch

## 🚀 Main Features

- 🔍 **Advanced Static Analysis** – Detects **28+ problem types** with fix suggestions
- 🏗️ **Modular Architecture** – Specialized analyzers for performance, security, memory, loops, errors
- 💡 **Smart Suggestions** – Ready-to-copy PHP code examples
- 🔄 **Intelligent Loop Fusion** – Detects consecutive loops that can be merged with smart variable adaptation
- 📊 **Array Access Optimization** – Detects repetitive array/object access and suggests temporary variables
- 🚀 **Dynamic Calls Optimization** – Converts dynamic calls to direct calls for better performance
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

### 🎯 **NEW** : Smart Filtering by Categories and Severity Weights

PHP Optimizer now features an advanced filtering system allowing you to precisely target the types of issues to detect:

```bash
# Security audit only
phpoptimizer analyze myproject/ --include-categories=security --recursive

# Critical and high severity issues only (weight ≥ 3)
phpoptimizer analyze myproject/ --min-weight=3 --recursive

# Performance without PSR formatting rules
phpoptimizer analyze myproject/ --include-categories=performance.critical,performance.general --exclude-categories=psr

# Lightweight code review (exclude formatting and conventions)
phpoptimizer analyze myproject/ --min-weight=2 --exclude-categories=psr
```

**Available categories:** `security` (critical), `error` (high), `performance.critical` (high), `performance.general` (medium), `memory` (medium), `code_quality` (low), `psr` (very low)

📖 **[Complete Categories and Weights Guide](CATEGORIES_GUIDE.md)**

### Analyze a PHP file with detailed suggestions

```bash
phpoptimizer analyze examples/performance_test.php --verbose
```

### Analyze with specific PHP version targeting

```bash
# Target PHP 7.4 (avoids union types, suggests nullable types)
phpoptimizer analyze examples/type_hints_example.php --php-version=7.4 --verbose

# Target PHP 8.2 (uses latest type features: union types, mixed, etc.)
phpoptimizer analyze examples/type_hints_example.php --php-version=8.2 --verbose
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

### 🎯 Type Hints - Version-Aware Suggestions
```php
// ❌ Missing type hints detected
function calculateTotal($items, $tax) {
    $sum = 0;
    foreach ($items as $item) {
        $sum += $item['price'];
    }
    return $sum * (1 + $tax);
}

// ✅ PHP 7.4 compatible suggestions
function calculateTotal(array $items, float $tax): float {
    $sum = 0;
    foreach ($items as $item) {
        $sum += $item['price'];
    }
    return $sum * (1 + $tax);
}

// ✅ PHP 8.0+ with union types
function processValue(int|float $value): int|float {
    return $value * 2;
}

// ✅ PHP 8.0+ with mixed type for complex data
function handleRequest($data): mixed {
    // Handles arrays, objects, or scalar values
    return process($data);
}
```

### 🔐 Security - SQL Injection
```php
// ❌ Vulnerable code detected
$result = mysql_query("SELECT * FROM users WHERE id = " . $_GET['id']);

// ✅ Suggested fix
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
$stmt->execute([$_GET['id']]);
$result = $stmt->fetchAll();
```

### 🚀 Performance - Dynamic Calls Optimization
```php
// ❌ Dynamic calls detected
$method = 'calculateScore';
$result = $object->$method($value);

$function = 'strtoupper';
$output = $function($input);

// ✅ Suggested optimization (faster direct calls)
$result = $object->calculateScore($value);
$output = strtoupper($input);
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

### 🔄 Performance - Loop Fusion
```php
// ❌ Consecutive loops detected
foreach ($users as $user) {
    $user['processed'] = true;
    $stats[] = calculateUserStats($user);
}

foreach ($users as $user) {
    sendNotification($user);
    logActivity($user['id']);
}

// ✅ Suggested fusion (reduces iterations)
foreach ($users as $user) {
    // First loop operations
    $user['processed'] = true;
    $stats[] = calculateUserStats($user);
    
    // Second loop operations
    sendNotification($user);
    logActivity($user['id']);
}
```

### 📊 Performance - Repetitive Array Access
```php
// ❌ Repetitive array access detected
function processUser() {
    if ($user['profile']['settings']['theme'] == 'dark') {
        echo $user['profile']['settings']['theme'];
        $theme = $user['profile']['settings']['theme'];
        return $user['profile']['settings']['theme'];
    }
}

// ✅ Suggested optimization (faster access)
function processUser() {
    $userTheme = $user['profile']['settings']['theme'];
    if ($userTheme == 'dark') {
        echo $userTheme;
        $theme = $userTheme;
        return $userTheme;
    }
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

### General Options
- `--verbose, -v`: Detailed output with suggestions and fix examples
- `--recursive, -r`: Recursively analyze subfolders
- `--output-format`: Output format (console, json, html)
- `--output, -o`: Output file
- `--rules`: Custom rules configuration file
- `--severity`: Minimum severity level (info, warning, error)
- `--php-version`: Target PHP version for type hints suggestions (e.g. `--php-version=7.4`, `--php-version=8.2`)

### 🎯 **NEW** : Advanced Filtering Options

#### Category-based Filtering
- `--include-categories`: Include only specified categories
- `--exclude-categories`: Exclude specified categories  
- `--min-weight`: Minimum severity weight (0=very low, 1=low, 2=medium, 3=high, 4=critical)

#### Individual Rules Filtering (Legacy)
- `--exclude-rules`: Exclude specific rules from the report 
- `--include-rules`: Only include specified rules

**Examples:**
```bash
# Only security and error issues
phpoptimizer analyze . --include-categories=security,error

# Exclude PSR formatting rules
phpoptimizer analyze . --exclude-categories=psr

# Medium severity and above
phpoptimizer analyze . --min-weight=2
```

### ⚙️ Advanced Configuration

You can create a custom configuration file to fine-tune detection thresholds and rule parameters:

```bash
# Use a custom configuration file
python -m phpoptimizer analyze myfile.php --rules=my_config.json
```

**Example configuration file** (`my_config.json`):
```json
{
  "php_version": "8.0",
  "rules": {
    "performance.repetitive_array_access": {
      "enabled": true,
      "severity": "info",
      "params": {
        "min_occurrences": 2
      }
    },
    "performance.inefficient_loops": {
      "enabled": true,
      "severity": "warning"
    },
    "performance.missing_parameter_type": {
      "enabled": true,
      "severity": "info"
    },
    "performance.missing_return_type": {
      "enabled": true,
      "severity": "info"
    },
    "best_practices.missing_docstring": {
      "enabled": false
    }
  }
}
```

**Configurable parameters**:
- `php_version` (default: "8.0") - Target PHP version for type hints suggestions (affects union types, nullable types, mixed type availability)
- `performance.repetitive_array_access.min_occurrences` (default: 3) - Minimum number of identical array accesses to trigger detection
- `performance.large_arrays.max_array_size` (default: 1000) - Threshold for detecting large arrays
- `performance.inefficient_loops.max_nested_loops` (default: 3) - Maximum loop nesting level before warning

### 🎯 Filter Detected Issue Types

You can choose to exclude or target specific types of issues during analysis:

#### 🆕 Category-based Filtering (Recommended)
- **Security audit only** :
  ```bash
  phpoptimizer analyze myfile.php --include-categories=security
  ```
- **Performance optimization focus** :
  ```bash
  phpoptimizer analyze myfile.php --include-categories=performance.critical,performance.general
  ```
- **Exclude PSR formatting rules** :
  ```bash
  phpoptimizer analyze myfile.php --exclude-categories=psr
  ```
- **Important issues only (medium+ severity)** :
  ```bash
  phpoptimizer analyze myfile.php --min-weight=2
  ```

#### Legacy Rule-based Filtering
- **Exclude detection of uncommented functions** :
- **Disable type hints detection** :
  ```bash
  python -m phpoptimizer analyze myfile.php --exclude-rules=performance.missing_parameter_type,performance.missing_return_type,performance.mixed_type_opportunity,best_practices.nullable_types
  ```

### 🏷️ Rule Categories Overview

#### 🔐 Security (Weight: 4 - Critical)
- `security.sql_injection` — SQL injection vulnerabilities
- `security.xss_vulnerability` — XSS vulnerabilities (unescaped output)
- `security.weak_password_hashing` — Weak password hashing (e.g. md5)

#### ❌ Error (Weight: 3 - High)
- `error.foreach_non_iterable` — Foreach on non-iterable variables
- `dead_code.unreachable_after_return` — Unreachable code after return/exit/die
- `dead_code.always_false_condition` — Always false conditions

#### ⚡ Performance.Critical (Weight: 3 - High)
- `performance.inefficient_loops` — Inefficient loop patterns (count() in conditions, deep nesting)
- `performance.algorithmic_complexity` — O(n²) patterns and optimization opportunities

#### 🚀 Performance.General (Weight: 2 - Medium)
- `performance.repetitive_array_access` — Repetitive array/object access optimization
- `performance.repeated_calculations` — Repeated identical calculations
- `performance.dynamic_method_call` — Dynamic method calls optimization
- `performance.dynamic_function_call` — Dynamic function calls optimization
- `performance.constant_propagation` — Constant value propagation

#### 🧠 Memory (Weight: 2 - Medium)
- `performance.large_arrays` — Large array declarations needing unset()
- `performance.unused_variables` — Variables declared but never used
- `performance.unused_global_variable` — Unused global variables
- `performance.global_could_be_local` — Global variables that could be local

#### 📝 Code_Quality (Weight: 1 - Low)
- `performance.missing_parameter_type` — Missing function parameter type hints
- `performance.missing_return_type` — Missing function return type hints
- `performance.mixed_type_opportunity` — Mixed type opportunities (PHP 8.0+)
- `best_practices.function_complexity` — Function complexity analysis

#### 📏 PSR (Weight: 0 - Very Low)
- `best_practices.psr_compliance` — PSR standards compliance (line length, etc.)
- `best_practices.line_length` — Line length violations
- `best_practices.naming` — Naming convention violations

> For legacy individual rule filtering, you can still use `--include-rules` and `--exclude-rules` with the rule names above. Find the complete rule name in the `rule_name` field of each issue in the report.

## 🌐 Interactive HTML Report

The HTML report offers a modern and interactive experience :

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

## 🚀 Advanced Loop Analysis Features

### 🔄 Intelligent Loop Fusion
The PHP Optimizer includes sophisticated **loop fusion detection** that can identify consecutive loops operating on the same data structure and suggest merging them for better performance.

#### � Smart Detection Capabilities
- **Variable Compatibility Analysis**: Detects when loops use compatible variables that can be safely merged
- **Interference Detection**: Prevents unsafe fusions when variables would conflict
- **Pattern Recognition**: Handles different foreach patterns (with/without keys)
- **Code Adaptation**: Automatically adapts variable names in fusion suggestions

#### ✅ Supported Fusion Cases
```php
// ✅ Case 1: Identical variables
foreach ($users as $user) { /* operations */ }
foreach ($users as $user) { /* more operations */ }

// ✅ Case 2: Compatible patterns (same structure)
foreach ($items as $key => $value) { /* operations */ }
foreach ($items as $id => $data) { /* more operations */ }

// ✅ Case 3: Different variables without interference  
foreach ($numbers as $num) { echo $num; }
foreach ($numbers as $val) { $sum += $val; }
```

#### ❌ Smart Rejection Cases
```php
// ❌ Nested loops (not consecutive)
foreach ($users as $user) {
    foreach ($user['items'] as $item) { /* nested */ }
}

// ❌ Variable interference
foreach ($items as $item) { $value = $item * 2; }
foreach ($items as $value) { /* conflict! */ }

// ❌ Incompatible patterns
foreach ($array as $item) { /* no key */ }
foreach ($array as $key => $value) { /* with key */ }
```

#### 🎯 Performance Benefits
- **Reduced Overhead**: Single loop instead of multiple iterations
- **Better Cache Locality**: More efficient memory access patterns
- **Simplified Code**: Cleaner, more maintainable logic

## �🧪 Supported Analysis Types

## Optimization Rules

The tool currently detects **over 25 types of issues** across several categories:

### 🚀 Performance

- **Inefficient loops**: `count()` in loop conditions, deeply nested loops
- **Loop fusion opportunities**: Detects consecutive loops that can be merged for better performance
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
// ❌ Detected issue: Missing parameter type hints
function processUsers($users, $options) {
    foreach ($users as $user) {
        echo $user['name'];
    }
    return count($users);
}
// ✅ PHP 7.4 suggestion: function processUsers(array $users, array $options): int
// ✅ PHP 8.0+ suggestion: function processUsers(array $users, array $options): int

// ❌ Detected issue: Missing union type hint (PHP 8.0+)
function calculateValue($number) {
    return $number * 2.5; // Can work with int or float
}
// ✅ PHP 8.0+ suggestion: function calculateValue(int|float $number): int|float
// ✅ PHP 7.4 fallback: function calculateValue(float $number): float

// ❌ Detected issue: Missing nullable type hint
function findUser($id) {
    if ($id === null) {
        return null;
    }
    return getUserById($id);
}
// ✅ PHP 7.1+ suggestion: function findUser(?int $id): ?User
// ✅ PHP 7.0 fallback: function findUser($id) // No nullable types in PHP 7.0

// ❌ Detected issue: Missing mixed type hint (PHP 8.0+)
function handleRequest($data) {
    // Handles arrays, objects, strings, or null
    return process($data);
}
// ✅ PHP 8.0+ suggestion: function handleRequest(mixed $data): mixed
// ✅ PHP 7.4 fallback: function handleRequest($data) // Mixed not available

// ❌ Detected issue: Consecutive loops can be merged - Loop fusion opportunity
foreach ($users as $user) {
    $user['email'] = strtolower($user['name']) . '@example.com';
    echo "Email created for " . $user['name'] . "\n";
}

foreach ($users as $user) {
    echo $user['name'] . " is " . $user['age'] . " years old\n";
    $totalAge += $user['age'];
}

// ✅ Suggested fusion:
foreach ($users as $user) {
    // Code from first loop
    $user['email'] = strtolower($user['name']) . '@example.com';
    echo "Email created for " . $user['name'] . "\n";
    
    // Code from second loop  
    echo $user['name'] . " is " . $user['age'] . " years old\n";
    $totalAge += $user['age'];
}

// ❌ Detected issue: Consecutive loops with different variables (smart adaptation)
foreach ($items as $item) {
    echo "Processing: $item\n";
    $total += $item;
}

foreach ($items as $value) {
    $results[] = $value * 2;
}

// ✅ Suggested fusion (variables automatically adapted):
foreach ($items as $item) {
    // Code from first loop
    echo "Processing: $item\n";
    $total += $item;
    
    // Code from second loop (adapted variables)
    $results[] = $item * 2;
}

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
│   │   ├── dead_code_analyzer.py  # Dead code detection and elimination
│   │   ├── dynamic_calls_analyzer.py # Dynamic calls optimization
│   │   └── type_hint_analyzer.py  # Type hints analysis and suggestions (NEW!)
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
- **Dynamic calls optimization**: Detection of dynamic method/function calls that can be converted to direct calls

#### 🚀 Dynamic Calls Analyzer (`dynamic_calls_analyzer.py`) *(NEW!)*
- **Method call optimization**: `$object->$method()` → `$object->methodName()`
- **Function call optimization**: `$function()` → `functionName()`
- **Variable tracking**: Analyzes variable assignments to ensure safe optimizations
- **Reassignment detection**: Prevents suggestions when variables are modified
- **Confidence scoring**: Only suggests optimizations with high confidence (>80%)

#### 🎯 Type Hint Analyzer (`type_hint_analyzer.py`) *(NEW!)*
- **Smart Type Inference**: Analyzes variable usage patterns to suggest appropriate types
- **Version-Aware Suggestions**: Adapts suggestions based on target PHP version (7.0, 7.1, 7.4, 8.0, 8.1, 8.2+)
- **Parameter Type Detection**: Identifies array usage (`foreach`, `count`), arithmetic operations, string methods
- **Return Type Analysis**: Analyzes return statements for `bool`, `int`, `string`, `array`, `mixed` inference
- **Union Types Support**: Suggests `int|float` for PHP 8.0+, falls back to `float` for older versions
- **Nullable Types**: Suggests `?string` only for PHP 7.1+, avoids for PHP 7.0
- **Mixed Type**: Suggests `mixed` only for PHP 8.0+, provides alternatives for older versions
- **JIT Optimization**: Proper type hints can improve performance up to 15% with PHP 8+ JIT compiler

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
    DeadCodeAnalyzer(),
    DynamicCallsAnalyzer(),
    TypeHintAnalyzer()  # NEW!
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

✅ Detection of **30+ different types of issues** across 9 specialized analyzers
✅ **Type hints analysis**: Smart inference with version-aware suggestions (PHP 7.0 to 8.2+)
✅ **Union types support**: `int|float` for PHP 8.0+, fallback to `float` for older versions
✅ **Nullable types**: `?string` suggested only for PHP 7.1+, avoided for PHP 7.0
✅ **Mixed type**: Suggested only for PHP 8.0+, alternatives provided for older versions
✅ **JIT optimization**: Type hints improve performance up to 15% with PHP 8+ JIT
✅ Dynamic calls optimization: Method and function call optimization with confidence analysis
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
✅ Modular architecture with 9 specialized analyzers
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

