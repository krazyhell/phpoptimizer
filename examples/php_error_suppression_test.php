<?php
// Test des vraies suppressions d'erreurs PHP (DOIVENT être détectées)

function testErrorSuppression() {
    // Ces @ DOIVENT déclencher des alertes
    $result = @file_get_contents($url);
    $data = @unserialize($input);
    $connection = @mysql_connect($host, $user, $pass);
    $content = @fopen($file, 'r');
    $json = @json_decode($string);
    
    // Mais pas ceux-ci qui sont dans des commentaires
    // $test = @some_function(); // commentaire avec @
    /* 
       $another = @another_function();
    */
    
    return $result;
}
?>
