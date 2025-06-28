<?php

/**
 * Autre fichier de test pour le rapport HTML
 */
class TestMultipleFiles 
{
    public function performanceIssue()
    {
        // Test de SELECT * 
        $sql = "SELECT * FROM users WHERE id = 1";
        
        // Test de count() dans une boucle
        for ($i = 0; $i < count($array); $i++) {
            echo $array[$i];
        }
    }
    
    public function securityIssue()
    {
        // Test d'injection SQL
        mysql_query("SELECT * FROM users WHERE name = '$name'");
        
        // Test de XSS
        echo $_GET['message'];
    }
}
