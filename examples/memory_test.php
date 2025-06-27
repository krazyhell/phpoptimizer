<?php
/**
 * Fichier de test pour la détection des oublis de unset()
 * Contient différents scénarios de gestion mémoire
 */

class MemoryTestClass {
    
    public function testLargeArraysWithUnset() {
        // CAS 1: Gros tableau avec unset() - PAS DE PROBLÈME
        $bigArray1 = range(1, 50000);
        // ... utilisation du tableau
        foreach ($bigArray1 as $value) {
            echo $value;
        }
        unset($bigArray1); // Correctement libéré
        
        // CAS 2: array_fill avec unset() - PAS DE PROBLÈME
        $bigArray2 = array_fill(0, 100000, 'data');
        processData($bigArray2);
        unset($bigArray2); // Correctement libéré
    }
    
    public function testLargeArraysWithoutUnset() {
        // CAS 3: Gros tableau SANS unset() - PROBLÈME
        $bigArray3 = range(1, 75000);
        foreach ($bigArray3 as $value) {
            echo $value;
        }
        // Oubli de unset($bigArray3) - DOIT ÊTRE DÉTECTÉ
        
        // CAS 4: array_fill SANS unset() - PROBLÈME  
        $bigArray4 = array_fill(0, 60000, 'test');
        processData($bigArray4);
        // Oubli de unset($bigArray4) - DOIT ÊTRE DÉTECTÉ
        
        // CAS 5: str_repeat SANS unset() - PROBLÈME
        $bigString = str_repeat('x', 50000);
        echo strlen($bigString);
        // Oubli de unset($bigString) - DOIT ÊTRE DÉTECTÉ
    }
    
    public function testConditionalUnset() {
        // CAS 6: unset() conditionnel - COMPLEXE
        $bigArray5 = range(1, 80000);
        
        if ($someCondition) {
            unset($bigArray5); // unset() conditionnel
        }
        // Ce cas est complexe à détecter parfaitement
    }
    
    public function testNestedBlocks() {
        // CAS 7: Blocs imbriqués avec unset()
        $bigArray6 = array_fill(0, 45000, 'nested');
        
        if ($condition1) {
            if ($condition2) {
                // Code imbriqué
                processData($bigArray6);
            }
            unset($bigArray6); // unset() dans bloc imbriqué - OK
        }
    }
    
    public function testLoopArrays() {
        // CAS 8: Tableau rempli dans boucle SANS unset() - PROBLÈME
        for ($i = 0; $i < 50000; $i++) {
            $loopArray[$i] = "data_$i";
        }
        processData($loopArray);
        // Oubli de unset($loopArray) - DOIT ÊTRE DÉTECTÉ
    }
    
    public function testLoopArraysWithUnset() {
        // CAS 9: Tableau rempli dans boucle AVEC unset() - OK
        for ($i = 0; $i < 40000; $i++) {
            $loopArray2[$i] = "data_$i";
        }
        processData($loopArray2);
        unset($loopArray2); // Correctement libéré
    }
    
    public function testMultipleUnset() {
        // CAS 10: Plusieurs variables dans un seul unset()
        $array1 = range(1, 30000);
        $array2 = array_fill(0, 35000, 'multi');
        $array3 = range(100, 45000);
        
        processData($array1, $array2, $array3);
        unset($array1, $array2, $array3); // Toutes libérées ensemble - OK
    }
}

// CAS 11: Variables globales (difficiles à tracker)
$globalBigArray = range(1, 100000);
processGlobalData($globalBigArray);
// Pas de unset() global - PEUT ÊTRE DÉTECTÉ

function testInFunction() {
    // CAS 12: Dans une fonction simple
    $funcArray = array_fill(0, 55000, 'function');
    return processData($funcArray);
    // Oubli de unset($funcArray) - DOIT ÊTRE DÉTECTÉ
}

function testInFunctionWithUnset() {
    // CAS 13: Dans une fonction avec unset()
    $funcArray2 = range(1, 65000);
    $result = processData($funcArray2);
    unset($funcArray2); // Correctement libéré
    return $result;
}

// Fonctions utilitaires
function processData($data) {
    return count($data);
}

function processGlobalData($data) {
    return array_sum($data);
}
?>
