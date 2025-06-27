<?php
// Fichier de démonstration avec différents types de problèmes

class ProblemesSecurity {
    public function demonstrationProblemes() {
        // Problème de sécurité : injection SQL
        $user_id = $_GET['id'];
        $query = "SELECT * FROM users WHERE id = $user_id";  // Injection SQL
        
        // Problème de sécurité : XSS
        echo "Bonjour " . $_GET['nom'];  // XSS non échappé
        
        // Problème de sécurité : hachage faible
        $password_hash = md5($_POST['password']);  // Hachage faible
        
        // Problème de performance : boucle inefficace
        for ($i = 0; $i < count($this->items); $i++) {  // count() en boucle
            $result .= $this->items[$i];  // Concaténation en boucle
        }
        
        // Problème de performance : gestion mémoire
        $huge_array = range(1, 500000);  // Gros tableau
        $processed = array_sum($huge_array);
        // Oubli de unset($huge_array)
        
        // Problème de performance : suppression d'erreur
        $content = @file_get_contents('http://example.com/api');  // @ suppression
        
        // Problème de performance : fonction obsolète
        if (ereg('[0-9]+', $input)) {  // Fonction obsolète
            $parts = split(',', $input);  // Fonction obsolète
        }
        
        return $processed;
    }
}

// Cette ligne est vraiment très très très très très très très très très très très très très très très très très très longue
?>
