"""
Tests unitaires spécifiques pour la détection des oublis de unset()
"""

import unittest
from pathlib import Path
from phpoptimizer.simple_analyzer import SimpleAnalyzer
from phpoptimizer.config import Config


class TestMemoryManagement(unittest.TestCase):
    """Tests pour la détection des problèmes de gestion mémoire"""
    
    def setUp(self):
        self.analyzer = SimpleAnalyzer(Config())
    
    def test_large_array_without_unset(self):
        """Test: gros tableau sans unset() doit être détecté"""
        code = """<?php
        $bigArray = range(1, 50000);
        foreach ($bigArray as $value) {
            echo $value;
        }
        // Pas de unset($bigArray)
        ?>"""
        
        result = self.analyzer.analyze_content(code, Path("test.php"))
        
        # Vérifier qu'un problème de gestion mémoire est détecté
        memory_issues = [issue for issue in result['issues'] 
                        if issue.get('rule_name') == 'performance.memory_management']
        self.assertGreater(len(memory_issues), 0, "Devrait détecter l'oubli de unset() sur un gros tableau")
        
        # Vérifier le message
        issue = memory_issues[0]
        self.assertIn("bigArray", issue['message'])
        self.assertIn("50000", issue['message'])
    
    def test_large_array_with_unset(self):
        """Test: gros tableau avec unset() ne doit PAS être détecté"""
        code = """<?php
        $bigArray = range(1, 50000);
        foreach ($bigArray as $value) {
            echo $value;
        }
        unset($bigArray); // Correctement libéré
        ?>"""
        
        result = self.analyzer.analyze_content(code, Path("test.php"))
        
        # Vérifier qu'AUCUN problème de gestion mémoire n'est détecté
        memory_issues = [issue for issue in result['issues'] 
                        if issue.get('rule_name') == 'performance.memory_management']
        self.assertEqual(len(memory_issues), 0, "Ne devrait PAS détecter de problème si unset() est présent")
    
    def test_array_fill_without_unset(self):
        """Test: array_fill sans unset() doit être détecté"""
        code = """<?php
        $bigArray = array_fill(0, 60000, 'data');
        processData($bigArray);
        // Pas de unset($bigArray)
        ?>"""
        
        result = self.analyzer.analyze_content(code, Path("test.php"))
        
        memory_issues = [issue for issue in result['issues'] 
                        if issue.get('rule_name') == 'performance.memory_management']
        self.assertGreater(len(memory_issues), 0, "Devrait détecter l'oubli de unset() sur array_fill")
        
        issue = memory_issues[0]
        self.assertIn("bigArray", issue['message'])
        self.assertIn("60000", issue['message'])
    
    def test_array_fill_with_unset(self):
        """Test: array_fill avec unset() ne doit PAS être détecté"""
        code = """<?php
        $bigArray = array_fill(0, 60000, 'data');
        processData($bigArray);
        unset($bigArray);
        ?>"""
        
        result = self.analyzer.analyze_content(code, Path("test.php"))
        
        memory_issues = [issue for issue in result['issues'] 
                        if issue.get('rule_name') == 'performance.memory_management']
        self.assertEqual(len(memory_issues), 0, "Ne devrait PAS détecter de problème si unset() est présent")
    
    def test_multiple_unset(self):
        """Test: plusieurs variables dans un unset() ne doivent PAS être détectées"""
        code = """<?php
        $array1 = range(1, 30000);
        $array2 = array_fill(0, 35000, 'data');
        processData($array1, $array2);
        unset($array1, $array2); // Les deux libérées ensemble
        ?>"""
        
        result = self.analyzer.analyze_content(code, Path("test.php"))
        
        memory_issues = [issue for issue in result['issues'] 
                        if issue.get('rule_name') == 'performance.memory_management']
        self.assertEqual(len(memory_issues), 0, "Ne devrait PAS détecter de problème si les variables sont dans unset()")
    
    def test_unset_in_nested_block(self):
        """Test: unset() dans un bloc imbriqué doit être reconnu"""
        code = """<?php
        function testFunction() {
            $bigArray = range(1, 45000);
            
            if ($condition) {
                processData($bigArray);
                unset($bigArray); // unset() dans un bloc if
            }
        }
        ?>"""
        
        result = self.analyzer.analyze_content(code, Path("test.php"))
        
        memory_issues = [issue for issue in result['issues'] 
                        if issue.get('rule_name') == 'performance.memory_management']
        self.assertEqual(len(memory_issues), 0, "Devrait reconnaître unset() même dans un bloc imbriqué")
    
    def test_loop_array_without_unset(self):
        """Test: tableau rempli dans boucle sans unset() doit être détecté"""
        code = """<?php
        for ($i = 0; $i < 50000; $i++) {
            $loopArray[$i] = "data_$i";
        }
        processData($loopArray);
        // Pas de unset($loopArray)
        ?>"""
        
        result = self.analyzer.analyze_content(code, Path("test.php"))
        
        memory_issues = [issue for issue in result['issues'] 
                        if issue.get('rule_name') == 'performance.memory_management']
        self.assertGreater(len(memory_issues), 0, "Devrait détecter l'oubli de unset() sur tableau de boucle")
        
        issue = memory_issues[0]
        self.assertIn("loopArray", issue['message'])
        self.assertIn("50000", issue['message'])
    
    def test_loop_array_with_unset(self):
        """Test: tableau rempli dans boucle avec unset() ne doit PAS être détecté"""
        code = """<?php
        for ($i = 0; $i < 40000; $i++) {
            $loopArray[$i] = "data_$i";
        }
        processData($loopArray);
        unset($loopArray);
        ?>"""
        
        result = self.analyzer.analyze_content(code, Path("test.php"))
        
        memory_issues = [issue for issue in result['issues'] 
                        if issue.get('rule_name') == 'performance.memory_management']
        self.assertEqual(len(memory_issues), 0, "Ne devrait PAS détecter de problème si unset() est présent")
    
    def test_str_repeat_without_unset(self):
        """Test: str_repeat sans unset() doit être détecté"""
        code = """<?php
        $bigString = str_repeat('x', 50000);
        echo strlen($bigString);
        // Pas de unset($bigString)
        ?>"""
        
        result = self.analyzer.analyze_content(code, Path("test.php"))
        
        memory_issues = [issue for issue in result['issues'] 
                        if issue.get('rule_name') == 'performance.memory_management']
        self.assertGreater(len(memory_issues), 0, "Devrait détecter l'oubli de unset() sur str_repeat")
        
        issue = memory_issues[0]
        self.assertIn("bigString", issue['message'])
        self.assertIn("50000", issue['message'])
    
    def test_small_arrays_ignored(self):
        """Test: les petits tableaux ne doivent PAS être détectés"""
        code = """<?php
        $smallArray1 = range(1, 100);    // Trop petit
        $smallArray2 = array_fill(0, 500, 'data');  // Trop petit
        $smallString = str_repeat('x', 1000);  // Trop petit
        
        // Pas de unset() - mais c'est OK car petits tableaux
        ?>"""
        
        result = self.analyzer.analyze_content(code, Path("test.php"))
        
        memory_issues = [issue for issue in result['issues'] 
                        if issue.get('rule_name') == 'performance.memory_management']
        self.assertEqual(len(memory_issues), 0, "Ne devrait PAS détecter les petits tableaux")
    
    def test_function_scope_boundary(self):
        """Test: la détection doit s'arrêter à la fin de fonction"""
        code = """<?php
        function func1() {
            $bigArray1 = range(1, 50000);
            // Pas de unset() - DOIT ÊTRE DÉTECTÉ
        }
        
        function func2() {
            $bigArray2 = range(1, 60000);
            unset($bigArray2); // OK
        }
        
        // unset($bigArray1); // Ceci ne compte pas car hors de la fonction
        ?>"""
        
        result = self.analyzer.analyze_content(code, Path("test.php"))
        
        memory_issues = [issue for issue in result['issues'] 
                        if issue.get('rule_name') == 'performance.memory_management']
        
        # Devrait détecter bigArray1 mais pas bigArray2
        bigArray1_issues = [issue for issue in memory_issues if 'bigArray1' in issue['message']]
        bigArray2_issues = [issue for issue in memory_issues if 'bigArray2' in issue['message']]
        
        self.assertGreater(len(bigArray1_issues), 0, "Devrait détecter bigArray1 sans unset()")
        self.assertEqual(len(bigArray2_issues), 0, "Ne devrait PAS détecter bigArray2 avec unset()")
    
    def test_foreach_on_non_iterable(self):
        """Test: foreach sur une variable non itérable doit être détecté"""
        code = """<?php
        $foo = 42;
        foreach ($foo as $item) {
            echo $item;
        }
        ?>"""
        result = self.analyzer.analyze_content(code, Path("test.php"))
        issues = [issue for issue in result['issues'] if issue.get('rule_name') == 'error.foreach_non_iterable']
        self.assertGreater(len(issues), 0, "Devrait détecter foreach sur un non-itérable")
        self.assertIn("foreach on non-iterable", issues[0]['message'])

    def test_heavy_functions_in_loop(self):
        """Test: fonctions lourdes dans une boucle doivent être détectées"""
        code = """<?php
        for ($i = 0; $i < 100; $i++) {
            $content = file_get_contents("file_$i.txt");
            $files = glob("*.txt");
            $exists = file_exists("test.txt");
        }
        ?>"""
        result = self.analyzer.analyze_content(code, Path("test.php"))
        heavy_issues = [issue for issue in result['issues'] if issue.get('rule_name') == 'performance.heavy_function_in_loop']
        
        self.assertGreaterEqual(len(heavy_issues), 3, "Devrait détecter au moins 3 fonctions lourdes")
        
        # Vérifier types détectés
        messages = [issue['message'] for issue in heavy_issues]
        self.assertTrue(any('Lecture de fichier' in msg for msg in messages))
        self.assertTrue(any('Recherche de fichiers' in msg for msg in messages))
        self.assertTrue(any('Vérification d\'existence' in msg for msg in messages))


if __name__ == '__main__':
    unittest.main()
