<?php
// Fichier d'exemple avec problèmes de performance avancés

class PerformanceIssues {
    
    // Problème 1: Requêtes dans une boucle (N+1)
    public function loadUsersWithPosts($userIds) {
        $users = [];
        foreach ($userIds as $id) {
            $query = "SELECT * FROM users WHERE id = $id";  // SELECT * + injection
            $user = mysql_query($query);  // Fonction obsolète + requête dans boucle
            
            // Encore une requête dans la boucle
            $posts = mysql_query("SELECT * FROM posts WHERE user_id = $id");
            $users[] = ['user' => $user, 'posts' => $posts];
        }
        return $users;
    }
    
    // Problème 2: Concaténation inefficace
    public function buildLargeString($items) {
        $result = "";
        for ($i = 0; $i < count($items); $i++) {  // count() dans boucle
            $result .= $items[$i] . "\n";  // Concaténation dans boucle
        }
        return $result;
    }
    
    // Problème 3: array_key_exists vs isset
    public function checkArrayKeys($data, $keys) {
        $results = [];
        foreach ($keys as $key) {
            if (array_key_exists($key, $data)) {  // Inefficace
                $results[] = $data[$key];
            }
        }
        return $results;
    }
    
    // Problème 4: Ouvertures de fichiers multiples
    public function processFiles($filenames) {
        $content = "";
        foreach ($filenames as $filename) {
            $file = fopen($filename, 'r');  // Ouverture répétée
            while (($line = fgets($file)) !== false) {
                $content .= $line;  // Double problème: concaténation + fgets ligne par ligne
            }
            fclose($file);
        }
        return $content;
    }
    
    // Problème 5: Suppression d'erreurs
    public function riskyOperations($data) {
        $result = @file_get_contents($data['url']);  // Suppression d'erreur
        $json = @json_decode($result);  // Encore une suppression
        return $json;
    }
    
    // Problème 6: Fonctions obsolètes multiples
    public function oldStyleCode($pattern, $text) {
        if (ereg($pattern, $text)) {  // Fonction obsolète
            $parts = split(',', $text);  // Fonction obsolète
            return $parts;
        }
        return false;
    }
    
    // Problème 7: Variables non libérées + gros tableaux
    public function memoryIntensive() {
        $large_array = range(1, 1000000);  // Gros tableau
        $unused_large = array_fill(0, 500000, 'data');  // Non utilisé + gros
        
        // Traitement...
        $result = array_sum($large_array);
        
        // Oubli de unset($large_array, $unused_large)
        return $result;
    }
}

// Problèmes globaux
$global_unused = "Cette variable n'est jamais utilisée";

// Calculs répétés complexes
$calc1 = $a * $b + $c * $d - $e;
$calc2 = $a * $b + $c * $d - $e;  // Répété
$calc3 = $a * $b + $c * $d - $e;  // Encore répété

// Ligne très très très très très très très très très très très très très très très très très très très très très très très très très très très très très longue
?>
