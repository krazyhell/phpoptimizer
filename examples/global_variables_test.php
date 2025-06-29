<?php

// Test 1: Variable globale jamais utilisée
function test_unused_global() {
    global $unused_var; // ❌ Déclarée mais jamais utilisée
    echo "Function without using global variable";
}

// Test 2: Variable globale qui pourrait être locale
function test_could_be_local() {
    global $local_candidate; // ❌ Pourrait être locale
    $local_candidate = "only used here"; // Assignée dans cette fonction
    echo $local_candidate; // Utilisée seulement ici
}

// Test 3: Variable globale correctement utilisée (ne doit pas être détectée)
$global_config = "shared data";

function test_proper_global_usage() {
    global $global_config; // ✅ OK - utilisée globalement
    echo $global_config;
}

function another_function_using_global() {
    global $global_config; // ✅ OK - utilisée dans plusieurs fonctions
    return $global_config . " modified";
}

// Test 4: Plusieurs variables globales dans une déclaration
function test_multiple_globals() {
    global $used_var, $unused_var2; // ❌ $unused_var2 jamais utilisée
    echo $used_var; // $used_var est utilisée
}

// Test 5: Variable globale avec assignation externe (ne doit pas être locale)
$external_var = "set outside";

function test_external_assignment() {
    global $external_var; // ✅ OK - assignée à l'extérieur
    echo $external_var;
}

// Test 6: Variables superglobales (ne doivent pas être détectées)
function test_superglobals() {
    echo $_GET['param']; // ✅ OK - superglobale
    echo $_SESSION['data']; // ✅ OK - superglobale
}

?>
