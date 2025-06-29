<?php
// Test création d'objets répétée dans boucles
for ($i = 0; $i < 1000; $i++) {
    $date = new DateTime('2023-01-01');
    $dom = new DOMDocument();
    $parser = json_decode('{"test": "value"}');
    $xml = simplexml_load_string('<root></root>');
    $logger = Logger::getInstance();
    $factory = MyFactory::create('default');
    
    // Usage avec variables (OK)
    $user = new User($i, "name_$i");
}

// Test normal (pas de problème)
$date = new DateTime('2023-01-01');
for ($i = 0; $i < 10; $i++) {
    echo $date->format('Y-m-d');
}
?>
