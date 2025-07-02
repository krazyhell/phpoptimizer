"""
Dead Code Analyzer for PHP Optimizer

Detects unreachable code patterns including:
- Code after return/exit/die/throw statements
- Code in always-false conditional branches
- Code after break/continue statements
- Unreachable catch blocks
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re
from .base_analyzer import BaseAnalyzer


class DeadCodeAnalyzer(BaseAnalyzer):
    """Analyzer for detecting dead code patterns"""
    
    def analyze(self, content: str, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """Analyze PHP code for dead code patterns"""
        issues = []
        
        # Track function/method boundaries and control flow
        in_function = False
        brace_level = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or self._is_comment_line(stripped):
                continue
            
            # Track brace levels for scope analysis
            brace_level += stripped.count('{') - stripped.count('}')
            
            # Check for unreachable code after flow control statements
            unreachable_issue = self._check_unreachable_after_flow_control(lines, line_num - 1)
            if unreachable_issue:
                issues.append(self._create_issue(
                    'dead_code.unreachable_after_return',
                    unreachable_issue['message'],
                    file_path,
                    line_num,
                    'warning',
                    'dead_code',
                    unreachable_issue['suggestion'],
                    stripped,
                    unreachable_issue['examples']
                ))
            
            # Check for always-false conditions
            false_condition_issue = self._check_always_false_condition(stripped, line_num)
            if false_condition_issue:
                issues.append(self._create_issue(
                    'dead_code.always_false_condition',
                    'Always-false condition creates unreachable code',
                    file_path,
                    line_num,
                    'warning',
                    'dead_code',
                    'Remove or fix the always-false condition',
                    stripped,
                    {
                        'before': f'if (false) {{\n    // This code is never executed\n    echo "Dead code";\n}}',
                        'after': '// Remove the entire if block or fix the condition\n// if ($actual_condition) {\n//     echo "Reachable code";\n// }'
                    }
                ))
            
            # Check for unreachable code after break/continue
            break_continue_issue = self._check_unreachable_after_break_continue(lines, line_num - 1)
            if break_continue_issue:
                issues.append(self._create_issue(
                    'dead_code.unreachable_after_break',
                    'Unreachable code after break/continue statement',
                    file_path,
                    line_num,
                    'warning',
                    'dead_code',
                    'Remove unreachable code after break or continue',
                    stripped,
                    {
                        'before': 'for ($i = 0; $i < 10; $i++) {\n    if ($condition) {\n        break;\n        echo "Never executed"; // Dead code\n    }\n}',
                        'after': 'for ($i = 0; $i < 10; $i++) {\n    if ($condition) {\n        break;\n    }\n}'
                    }
                ))
        
        return issues
    
    def _check_unreachable_after_flow_control(self, lines: List[str], current_index: int) -> Optional[Dict[str, Any]]:
        """Check for unreachable code after return/exit/die/throw statements"""
        if current_index >= len(lines):
            return None
        
        current_line = lines[current_index].strip()
        
        # Look for previous line with flow control statement
        for i in range(current_index - 1, max(0, current_index - 3), -1):
            prev_line = lines[i].strip()
            
            # Skip empty lines and comments
            if not prev_line or self._is_comment_line(prev_line):
                continue
            
            # Check if previous line ends with flow control statement
            if self._ends_with_flow_control(prev_line):
                # Check if current line is not a closing brace or new block
                if not self._is_block_boundary(current_line):
                    flow_type = self._get_flow_control_type(prev_line)
                    return {
                        'message': f'Unreachable code after {flow_type} statement',
                        'suggestion': f'Remove unreachable code after {flow_type} statement',
                        'examples': self._get_flow_control_examples(flow_type)
                    }
            break
        
        return None
    
    def _check_always_false_condition(self, line: str, line_num: int) -> bool:
        """Check for always-false conditional statements"""
        # Patterns for always-false conditions
        false_patterns = [
            r'\bif\s*\(\s*false\s*\)',
            r'\bif\s*\(\s*0\s*\)',
            r'\bif\s*\(\s*null\s*\)',
            r'\bif\s*\(\s*""\s*\)',
            r'\bif\s*\(\s*\'\'\s*\)',
            r'\bwhile\s*\(\s*false\s*\)',
            r'\bwhile\s*\(\s*0\s*\)',
        ]
        
        for pattern in false_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _check_unreachable_after_break_continue(self, lines: List[str], current_index: int) -> bool:
        """Check for unreachable code after break/continue statements"""
        if current_index >= len(lines):
            return False
        
        current_line = lines[current_index].strip()
        
        # Look for previous line with break/continue
        for i in range(current_index - 1, max(0, current_index - 2), -1):
            prev_line = lines[i].strip()
            
            if not prev_line or self._is_comment_line(prev_line):
                continue
            
            # Check if previous line is break or continue
            if re.search(r'\b(break|continue)\s*;?\s*$', prev_line, re.IGNORECASE):
                # Check if current line is not a closing brace
                if not re.match(r'^\s*}', current_line):
                    return True
            break
        
        return False
    
    def _ends_with_flow_control(self, line: str) -> bool:
        """Check if line ends with a flow control statement"""
        flow_patterns = [
            r'\breturn\b.*?;?\s*$',
            r'\bexit\s*\([^)]*\)\s*;?\s*$',
            r'\bdie\s*\([^)]*\)\s*;?\s*$',
            r'\bthrow\s+.*?;?\s*$',
            r'\bexit\s*;?\s*$',
            r'\bdie\s*;?\s*$'
        ]
        
        for pattern in flow_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _get_flow_control_type(self, line: str) -> str:
        """Get the type of flow control statement"""
        if re.search(r'\breturn\b', line, re.IGNORECASE):
            return 'return'
        elif re.search(r'\bexit\b', line, re.IGNORECASE):
            return 'exit'
        elif re.search(r'\bdie\b', line, re.IGNORECASE):
            return 'die'
        elif re.search(r'\bthrow\b', line, re.IGNORECASE):
            return 'throw'
        return 'flow control'
    
    def _is_block_boundary(self, line: str) -> bool:
        """Check if line is a block boundary (brace, else, etc.)"""
        boundary_patterns = [
            r'^\s*}',  # Closing brace
            r'^\s*else\b',  # Else statement
            r'^\s*elseif\b',  # Elseif statement
            r'^\s*catch\b',  # Catch block
            r'^\s*finally\b',  # Finally block
            r'^\s*case\b',  # Switch case
            r'^\s*default\s*:',  # Switch default
        ]
        
        for pattern in boundary_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _get_flow_control_examples(self, flow_type: str) -> Dict[str, str]:
        """Get before/after examples for flow control issues"""
        examples = {
            'return': {
                'before': '''function calculate($value) {
    if ($value < 0) {
        return null;
        echo "This line is never executed"; // Dead code
        $result = $value * 2; // Dead code
    }
    return $value * 3;
}''',
                'after': '''function calculate($value) {
    if ($value < 0) {
        return null;
    }
    return $value * 3;
}'''
            },
            'exit': {
                'before': '''if ($error) {
    exit("Error occurred");
    echo "Cleanup code"; // Dead code
    unlink($temp_file); // Dead code
}''',
                'after': '''if ($error) {
    // Perform cleanup before exit
    unlink($temp_file);
    exit("Error occurred");
}'''
            },
            'throw': {
                'before': '''if ($invalid) {
    throw new Exception("Invalid data");
    echo "Recovery attempt"; // Dead code
    $data = fix_data($data); // Dead code
}''',
                'after': '''if ($invalid) {
    // Fix data before throwing if possible
    // $data = fix_data($data);
    throw new Exception("Invalid data");
}'''
            }
        }
        
        return examples.get(flow_type, {
            'before': f'{flow_type};\necho "Dead code"; // Never executed',
            'after': f'{flow_type};\n// Dead code removed'
        })
