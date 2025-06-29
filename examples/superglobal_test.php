<?php

// Test d'accès répétés aux superglobales dans des boucles
foreach ($users as $user) {
    $sessionData = $_SESSION['user_data']; // ❌ Accès répété à $_SESSION
    $cookieValue = $_COOKIE['preferences']; // ❌ Accès répété à $_COOKIE
    $userId = $_GET['id']; // ❌ Accès répété à $_GET
    echo "Processing user: " . $user->name;
}

// Test avec $_POST dans une boucle for
for ($i = 0; $i < 10; $i++) {
    $postData = $_POST['data'][$i]; // ❌ Accès répété à $_POST
    $serverInfo = $_SERVER['HTTP_HOST']; // ❌ Accès répété à $_SERVER
    echo "Processing: " . $postData;
}

// Test avec $_REQUEST et $_ENV
while ($row = fetchRow()) {
    $requestValue = $_REQUEST['action']; // ❌ Accès répété à $_REQUEST
    $envVar = $_ENV['PATH']; // ❌ Accès répété à $_ENV
    $globalVar = $GLOBALS['config']; // ❌ Accès répété à $GLOBALS
    processRow($row);
}

// Code correct - variables stockées avant la boucle (ne doit pas être détecté)
$sessionData = $_SESSION['user_data']; // ✅ OK - hors boucle
$cookieValue = $_COOKIE['preferences']; // ✅ OK - hors boucle
foreach ($items as $item) {
    echo "Using stored data: " . $sessionData . " - " . $cookieValue;
}

?>
