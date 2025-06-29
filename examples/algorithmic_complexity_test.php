<?php

// Test de création d'objets répétée dans boucle
for ($i = 0; $i < 100; $i++) {
    $date = new DateTime('2023-01-01'); // ❌ Création répétée avec arguments constants
    $logger = Logger::getInstance(); // ❌ Singleton appelé dans boucle
    echo $date->format('Y-m-d');
}

// Test de complexité algorithmique - tri dans boucle
$data = range(1, 1000);
foreach ($users as $user) {
    sort($data); // ❌ Tri dans boucle - O(n²log n)
    usort($user_data, 'compare_func'); // ❌ Tri personnalisé dans boucle
}

// Test de recherche linéaire dans boucle
$large_array = range(1, 10000);
foreach ($items as $item) {
    if (in_array($item->id, $large_array)) { // ❌ Recherche linéaire O(n²)
        echo "Found!";
    }
    $key = array_search($item->name, $names); // ❌ Recherche linéaire
}

// Test de boucles imbriquées sur même tableau
foreach ($users as $user1) {
    foreach ($users as $user2) { // ❌ Même tableau - O(n²)
        if ($user1->id !== $user2->id) {
            echo "Different users";
        }
    }
}

// Test de création d'objets avec variables (OK - ne doit pas être détecté)
foreach ($configs as $config) {
    $pdo = new PDO($config->dsn, $config->user, $config->pass); // ✅ Arguments variables
    $result = $pdo->query($config->sql);
}

// Test de fonctions lourdes dans boucle (déjà testé)
for ($i = 0; $i < 100; $i++) {
    $content = file_get_contents("file_$i.txt"); // ❌ I/O lourde
    $files = glob("*.txt"); // ❌ Scan filesystem
}

?>
