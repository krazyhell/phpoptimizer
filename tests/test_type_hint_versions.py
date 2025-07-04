"""
Tests pour la gestion des versions PHP dans l'analyseur de type hints
"""

import unittest
from phpoptimizer.analyzers.type_hint_analyzer import TypeHintAnalyzer
from phpoptimizer.config import Config


class TestTypeHintAnalyzerVersions(unittest.TestCase):
    
    def test_php_70_no_union_types(self):
        """Test PHP 7.0 : pas de types union, convertis en types simples"""
        config = Config()
        config.php_version = "7.0"
        analyzer = TypeHintAnalyzer(config)
        
        code = """<?php
function add($a, $b) {
    return $a + $b;
}
"""
        
        issues = analyzer.analyze(code, 'test.php', code.split('\n'))
        
        # Vérifier que int|float est converti en float
        param_issues = [issue for issue in issues if issue['rule_name'] == 'performance.missing_parameter_type']
        self.assertTrue(len(param_issues) >= 1)
        
        for issue in param_issues:
            self.assertIn('float', issue['suggestion'])
            self.assertNotIn('|', issue['suggestion'])  # Pas d'union types
    
    def test_php_71_nullable_types_supported(self):
        """Test PHP 7.1 : types nullable supportés"""
        config = Config()
        config.php_version = "7.1"
        analyzer = TypeHintAnalyzer(config)
        
        code = """<?php
function findUser($id) {
    if ($id > 0) {
        return new User();
    }
    return null;
}
"""
        
        issues = analyzer.analyze(code, 'test.php', code.split('\n'))
        
        # En PHP 7.1, on ne peut pas suggérer ?mixed car mixed n'existe pas
        # Donc on ne devrait avoir aucune suggestion de type de retour
        return_issues = [issue for issue in issues if issue['rule_name'] == 'performance.missing_return_type']
        self.assertEqual(len(return_issues), 0, "PHP 7.1 ne devrait pas suggérer ?mixed")
    
    def test_php_80_union_types_supported(self):
        """Test PHP 8.0 : types union et mixed supportés"""
        config = Config()
        config.php_version = "8.0"
        analyzer = TypeHintAnalyzer(config)
        
        code = """<?php
function add($a, $b) {
    return $a + $b;
}

function findUser($id) {
    if ($id > 0) {
        return getUser($id);
    }
    return null;
}
"""
        
        issues = analyzer.analyze(code, 'test.php', code.split('\n'))
        
        # Vérifier les types union
        param_issues = [issue for issue in issues if issue['rule_name'] == 'performance.missing_parameter_type']
        union_found = False
        for issue in param_issues:
            if 'int|float' in issue['suggestion']:
                union_found = True
        self.assertTrue(union_found, "PHP 8.0 devrait supporter les types union")
        
        # Vérifier ?mixed
        return_issues = [issue for issue in issues if issue['rule_name'] == 'performance.missing_return_type']
        mixed_found = False
        for issue in return_issues:
            if '?mixed' in issue['suggestion']:
                mixed_found = True
        self.assertTrue(mixed_found, "PHP 8.0 devrait supporter ?mixed")
    
    def test_version_comparison(self):
        """Test de la comparaison de versions"""
        config = Config()
        
        # Test des méthodes de version
        config.php_version = "7.0"
        self.assertFalse(config.supports_union_types())
        self.assertFalse(config.supports_nullable_types())
        self.assertFalse(config.supports_mixed_type())
        
        config.php_version = "7.1"
        self.assertFalse(config.supports_union_types())
        self.assertTrue(config.supports_nullable_types())
        self.assertFalse(config.supports_mixed_type())
        
        config.php_version = "8.0"
        self.assertTrue(config.supports_union_types())
        self.assertTrue(config.supports_nullable_types())
        self.assertTrue(config.supports_mixed_type())
    
    def test_backward_compatibility_suggestions(self):
        """Test que les suggestions restent utilisables en PHP moderne"""
        config = Config()
        config.php_version = "8.2"  # Version très récente
        analyzer = TypeHintAnalyzer(config)
        
        code = """<?php
function processData($data) {
    if (is_array($data)) {
        return count($data);
    }
    return 0;
}
"""
        
        issues = analyzer.analyze(code, 'test.php', code.split('\n'))
        
        # Vérifier qu'on a des suggestions valides
        self.assertTrue(len(issues) > 0)
        for issue in issues:
            self.assertIn('type', issue['rule_name'])
            # Les suggestions doivent être des types PHP valides
            suggestion = issue['suggestion']
            self.assertTrue(any(valid_type in suggestion for valid_type in 
                              ['array', 'int', 'string', 'bool', 'float', 'mixed']))


if __name__ == '__main__':
    unittest.main()
