<?php

// Tests pour vérifier la détection des points-virgules manquants

// Ces cas DOIVENT être signalés (point-virgule manquant)
$x = 5  // Manque un point-virgule
$name = "test"  // Manque un point-virgule

// Ces cas NE DOIVENT PAS être signalés (syntaxe valide)
$array = [
    'key1' => 'value1',
    'key2' => 'value2'
];

$paths = [
    'controllers',
    'models'
];

$object = new stdClass();

$result = (
    $condition1 &&
    $condition2
);

$closure = function() {
    return true;
};

// Tests supplémentaires
$multiline = "This is a " .
    "multiline string";

$calculated = 1 + 2 +
    3 + 4;

// Ces cas doivent être correctement détectés (avec point-virgule)
$correct = 'value';
$another = 123;
