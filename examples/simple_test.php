<?php
// Exemple simple pour tester l'affichage enrichi

// Injection SQL
$user_id = $_GET['id'];
$query = "SELECT * FROM users WHERE id = $user_id";
$result = mysql_query($query);

// Gros tableau sans unset
$large_data = range(1, 50000);
$sum = array_sum($large_data);

// Fonction obsolète
if (ereg('^[a-zA-Z]+$', $name)) {
    echo "Nom valide";
}

// Suppression d'erreur
$content = @file_get_contents($url);
?>
