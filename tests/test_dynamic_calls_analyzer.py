"""
Tests unitaires pour l'analyseur d'appels dynamiques
"""

import unittest
from pathlib import Path
import tempfile
import os

from phpoptimizer.analyzers.dynamic_calls_analyzer import DynamicCallsAnalyzer
from phpoptimizer.config import Config


class TestDynamicCallsAnalyzer(unittest.TestCase):
    """Tests pour l'analyseur d'appels dynamiques"""
    
    def setUp(self):
        """Configuration des tests"""
        self.config = Config()
        self.analyzer = DynamicCallsAnalyzer(self.config)
    
    def test_dynamic_method_call_detection(self):
        """Test de détection d'appel de méthode dynamique"""
        php_code = """<?php
$method = 'calculateScore';
$result = $object->$method($value);
?>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
            f.write(php_code)
            f.flush()
            
            file_path = Path(f.name)
            lines = php_code.split('\n')
            issues = self.analyzer.analyze(php_code, file_path, lines)
            
            # Vérifier qu'un appel de méthode dynamique est détecté
            method_issues = [issue for issue in issues 
                           if issue['rule_name'] == 'performance.dynamic_method_call']
            self.assertEqual(len(method_issues), 1)
            self.assertIn('calculateScore', method_issues[0]['suggestion'])
        
        # Nettoyer
        os.unlink(f.name)
    
    def test_dynamic_function_call_detection(self):
        """Test de détection d'appel de fonction dynamique"""
        php_code = """<?php
$function = 'strtoupper';
$output = $function($input);
?>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
            f.write(php_code)
            f.flush()
            
            file_path = Path(f.name)
            lines = php_code.split('\n')
            issues = self.analyzer.analyze(php_code, file_path, lines)
            
            # Vérifier qu'un appel de fonction dynamique est détecté
            function_issues = [issue for issue in issues 
                             if issue['rule_name'] == 'performance.dynamic_function_call']
            self.assertEqual(len(function_issues), 1)
            self.assertIn('strtoupper', function_issues[0]['suggestion'])
        
        # Nettoyer
        os.unlink(f.name)
    
    def test_multiple_calls_same_variable(self):
        """Test de détection de plusieurs appels avec la même variable"""
        php_code = """<?php
$transform = 'ucfirst';
$name1 = $transform($firstName);
$name2 = $transform($lastName);
?>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
            f.write(php_code)
            f.flush()
            
            file_path = Path(f.name)
            lines = php_code.split('\n')
            issues = self.analyzer.analyze(php_code, file_path, lines)
            
            # Vérifier que les deux appels sont détectés
            function_issues = [issue for issue in issues 
                             if issue['rule_name'] == 'performance.dynamic_function_call']
            self.assertEqual(len(function_issues), 2)
        
        # Nettoyer
        os.unlink(f.name)
    
    def test_variable_reassignment_not_detected(self):
        """Test que les variables réassignées ne sont pas détectées"""
        php_code = """<?php
$method = 'method1';
$method = 'method2';  // Réassignation
$result = $object->$method();
?>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
            f.write(php_code)
            f.flush()
            
            file_path = Path(f.name)
            lines = php_code.split('\n')
            issues = self.analyzer.analyze(php_code, file_path, lines)
            
            # Vérifier qu'aucun appel de méthode dynamique n'est détecté
            method_issues = [issue for issue in issues 
                           if issue['rule_name'] == 'performance.dynamic_method_call']
            self.assertEqual(len(method_issues), 0)
        
        # Nettoyer
        os.unlink(f.name)
    
    def test_comments_ignored(self):
        """Test que les commentaires sont ignorés"""
        php_code = """<?php
// $method = 'calculateScore';
$function = 'strtoupper';
$output = $function($input);
?>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
            f.write(php_code)
            f.flush()
            
            file_path = Path(f.name)
            lines = php_code.split('\n')
            issues = self.analyzer.analyze(php_code, file_path, lines)
            
            # Vérifier qu'un seul appel est détecté (pas celui en commentaire)
            function_issues = [issue for issue in issues 
                             if issue['rule_name'] == 'performance.dynamic_function_call']
            self.assertEqual(len(function_issues), 1)
        
        # Nettoyer
        os.unlink(f.name)
    
    def test_no_false_positives(self):
        """Test qu'il n'y a pas de faux positifs"""
        php_code = """<?php
$result = $object->staticMethod($value);
$output = strtoupper($input);
$data = array_map('trim', $array);
?>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
            f.write(php_code)
            f.flush()
            
            file_path = Path(f.name)
            lines = php_code.split('\n')
            issues = self.analyzer.analyze(php_code, file_path, lines)
            
            # Vérifier qu'aucun appel dynamique n'est détecté
            dynamic_issues = [issue for issue in issues 
                            if issue['rule_name'] in ['performance.dynamic_method_call', 
                                                     'performance.dynamic_function_call']]
            self.assertEqual(len(dynamic_issues), 0)
        
        # Nettoyer
        os.unlink(f.name)


if __name__ == '__main__':
    unittest.main()
