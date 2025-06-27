<?php
// Exemple de fichier PHP avec divers problèmes à détecter

class ExampleClass {
    private $data;
    
    // Fonction sans documentation
    public function inefficientLoop() {
        $results = array();
        $large_array = array();
        
        // Boucle inefficace avec fonction count() à l'intérieur
        for ($i = 0; $i < count($large_array); $i++) {
            for ($j = 0; $j < count($large_array); $j++) {
                for ($k = 0; $k < count($large_array); $k++) {
                    $results[] = $large_array[$i] + $large_array[$j] + $large_array[$k];
                }
            }
        }
        
        return $results;
    }
    
    // Vulnérabilité SQL Injection
    public function dangerousQuery($userId) {
        $query = "SELECT * FROM users WHERE id = " . $userId;
        mysql_query($query);
    }
    
    // Sortie non échappée (XSS)
    public function displayUserInput() {
        echo $_GET['message'];
        print $_POST['comment'];
    }
    
    // Variables non utilisées
    public function unusedVariables() {
        $unused_var = "This variable is never used";
        $another_unused = 42;
        $used_var = "This one is used";
        
        return $used_var;
    }
    
    // Fonction trop complexe
    public function complexFunction($param1, $param2, $param3) {
        if ($param1 > 0) {
            if ($param2 > 0) {
                if ($param3 > 0) {
                    for ($i = 0; $i < 10; $i++) {
                        if ($i % 2 == 0) {
                            if ($param1 > $param2) {
                                while ($param3 > 0) {
                                    switch ($param1) {
                                        case 1:
                                            return "case1";
                                        case 2:
                                            return "case2";
                                        default:
                                            $param3--;
                                    }
                                }
                            } else {
                                return "else branch";
                            }
                        } else {
                            continue;
                        }
                    }
                } else {
                    return "param3 negative";
                }
            } else {
                return "param2 negative";
            }
        } else {
            return "param1 negative";
        }
    }
    
    // Hachage faible pour mot de passe
    public function weakPasswordHash($password) {
        return md5($password);
    }
}

// Inclusion dangereuse
include($_GET['page'] . '.php');

// Calculs répétés
$result1 = $a * $b + $c;
$result2 = $a * $b + $c; // Même calcul répété
$result3 = $a * $b + $c; // Encore répété

// Ligne très longue qui dépasse 120 caractères et devrait déclencher un avertissement PSR-2 pour la longueur de ligne
?>
