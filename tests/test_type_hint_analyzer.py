"""
Tests pour l'analyseur de type hints
"""

import unittest
from phpoptimizer.analyzers.type_hint_analyzer import TypeHintAnalyzer


class TestTypeHintAnalyzer(unittest.TestCase):
    
    def setUp(self):
        """Initialiser l'analyseur pour chaque test"""
        self.analyzer = TypeHintAnalyzer()
    
    def test_missing_parameter_types(self):
        """Test de détection des types de paramètres manquants"""
        
        code = """<?php
function calculateTotal($items, $tax) {
    $sum = 0;
    foreach ($items as $item) {
        $sum += $item;
    }
    return $sum * (1 + $tax);
}
"""
        
        issues = self.analyzer.analyze(code, 'test.php', code.split('\n'))
        
        # Vérifier qu'on détecte les types manquants
        parameter_issues = [issue for issue in issues if issue['rule_name'] == 'performance.missing_parameter_type']
        self.assertTrue(len(parameter_issues) >= 1, "Devrait détecter au moins un paramètre sans type")
        
        # Vérifier les détails
        if parameter_issues:
            issue = parameter_issues[0]
            self.assertEqual(issue['severity'], 'info')
            self.assertIn('$items', issue['message'])
    
    def test_missing_return_type(self):
        """Test de détection des types de retour manquants"""
        
        code = """<?php
function getUserById($id) {
    if ($id > 0) {
        return findUser($id);
    }
    return null;
}
"""
        
        issues = self.analyzer.analyze(code, 'test.php', code.split('\n'))
        
        # Vérifier qu'on détecte le type de retour manquant
        return_issues = [issue for issue in issues if issue['rule_name'] == 'performance.missing_return_type']
        self.assertTrue(len(return_issues) >= 1, "Devrait détecter au moins un type de retour manquant")
        
        if return_issues:
            issue = return_issues[0]
            self.assertEqual(issue['severity'], 'info')
            self.assertIn('getUserById', issue['message'])
    
    def test_array_parameter_inference(self):
        """Test d'inférence de type array pour les paramètres"""
        
        code = """<?php
function processArray($data) {
    if (is_array($data)) {
        return count($data);
    }
    return 0;
}
"""
        
        issues = self.analyzer.analyze(code, 'test.php', code.split('\n'))
        
        # Chercher les suggestions de type array
        parameter_issues = [issue for issue in issues if issue['rule_name'] == 'performance.missing_parameter_type']
        
        # Vérifier qu'on suggère le type array
        array_suggestion = False
        for issue in parameter_issues:
            if 'array' in issue['suggestion']:
                array_suggestion = True
                break
        
        self.assertTrue(array_suggestion, "Devrait suggérer le type 'array' pour le paramètre $data")
    
    def test_string_parameter_inference(self):
        """Test d'inférence de type string pour les paramètres"""
        
        code = """<?php
function formatName($firstName, $lastName) {
    return trim($firstName) . ' ' . trim($lastName);
}
"""
        
        issues = self.analyzer.analyze(code, 'test.php', code.split('\n'))
        
        # Chercher les suggestions de type string
        parameter_issues = [issue for issue in issues if issue['rule_name'] == 'performance.missing_parameter_type']
        
        # Vérifier qu'on suggère le type string
        string_suggestion = False
        for issue in parameter_issues:
            if 'string' in issue['suggestion']:
                string_suggestion = True
                break
        
        self.assertTrue(string_suggestion, "Devrait suggérer le type 'string' pour les paramètres de nom")
    
    def test_int_return_type_inference(self):
        """Test d'inférence de type de retour int"""
        
        code = """<?php
function getCount() {
    return count($this->items);
}
"""
        
        issues = self.analyzer.analyze(code, 'test.php', code.split('\n'))
        
        # Chercher les suggestions de type de retour
        return_issues = [issue for issue in issues if issue['rule_name'] == 'performance.missing_return_type']
        
        # Vérifier qu'on suggère le type int
        int_suggestion = False
        for issue in return_issues:
            if 'int' in issue['suggestion']:
                int_suggestion = True
                break
        
        self.assertTrue(int_suggestion, "Devrait suggérer le type 'int' pour le retour de count()")
    
    def test_boolean_return_type_inference(self):
        """Test d'inférence de type de retour bool"""
        
        code = """<?php
function isValidEmail($email) {
    return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
}
"""
        
        issues = self.analyzer.analyze(code, 'test.php', code.split('\n'))
        
        # Chercher les suggestions de type de retour
        return_issues = [issue for issue in issues if issue['rule_name'] == 'performance.missing_return_type']
        
        # Vérifier qu'on suggère le type bool
        bool_suggestion = False
        for issue in return_issues:
            if 'bool' in issue['suggestion']:
                bool_suggestion = True
                break
        
        self.assertTrue(bool_suggestion, "Devrait suggérer le type 'bool' pour une fonction de validation")
    
    def test_already_typed_function_ignored(self):
        """Test que les fonctions déjà typées sont ignorées"""
        
        code = """<?php
function calculateTotal(array $items, float $tax): float {
    $sum = 0.0;
    foreach ($items as $item) {
        $sum += $item;
    }
    return $sum * (1 + $tax);
}
"""
        
        issues = self.analyzer.analyze(code, 'test.php', code.split('\n'))
        
        # Vérifier qu'aucune suggestion n'est faite pour une fonction déjà typée
        type_issues = [issue for issue in issues if issue['rule_name'] in [
            'performance.missing_parameter_type',
            'performance.missing_return_type'
        ]]
        
        self.assertEqual(len(type_issues), 0, "Ne devrait pas suggérer de types pour une fonction déjà typée")
    
    def test_complex_example_detection(self):
        """Test de détection sur un exemple complexe"""
        
        code = """<?php
class Calculator {
    public function add($a, $b) {
        return $a + $b;
    }
    
    public function sumArray($numbers) {
        return array_sum($numbers);
    }
    
    public function isPositive($number) {
        return $number > 0;
    }
}
"""
        
        issues = self.analyzer.analyze(code, 'test.php', code.split('\n'))
        
        # Vérifier qu'on détecte plusieurs problèmes
        parameter_issues = [issue for issue in issues if issue['rule_name'] == 'performance.missing_parameter_type']
        return_issues = [issue for issue in issues if issue['rule_name'] == 'performance.missing_return_type']
        
        self.assertTrue(len(parameter_issues) >= 2, "Devrait détecter plusieurs paramètres sans type")
        self.assertTrue(len(return_issues) >= 2, "Devrait détecter plusieurs types de retour manquants")
    
    def test_get_rules(self):
        """Test de la méthode get_rules"""
        
        rules = self.analyzer.get_rules()
        
        expected_rules = [
            'performance.missing_parameter_type',
            'performance.missing_return_type',
            'performance.mixed_type_opportunity',
            'best_practices.nullable_types'
        ]
        
        for rule in expected_rules:
            self.assertIn(rule, rules, f"La règle {rule} devrait être dans la liste")


if __name__ == '__main__':
    unittest.main()
