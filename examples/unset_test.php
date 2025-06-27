<?php
// Test simple pour la détection des oublis de unset()

function test_memory_issues() {
    // Cas 1: Gros tableau avec range() - DEVRAIT être détecté
    $large_array = range(1, 100000);
    $result = array_sum($large_array);
    // Oubli de unset($large_array)
    
    // Cas 2: Gros tableau avec array_fill() - DEVRAIT être détecté  
    $big_data = array_fill(0, 50000, 'test');
    $count = count($big_data);
    // Oubli de unset($big_data)
    
    // Cas 3: Petit tableau - NE DEVRAIT PAS être détecté
    $small_array = range(1, 100);
    unset($small_array); // Correctement libéré
    
    // Cas 4: Gros tableau correctement libéré - NE DEVRAIT PAS être détecté
    $correct_array = range(1, 200000);
    $sum = array_sum($correct_array);
    unset($correct_array); // Correctement libéré
    
    return $result + $count + $sum;
}

// Test global
$global_large = array_fill(0, 75000, 'data');
// Oubli de unset($global_large)
?>
