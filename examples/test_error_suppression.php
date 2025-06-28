<?php

/**
 * Classe de test pour les suppressions d'erreurs
 * 
 * @var array<class-string, class-string> Ceci ne doit PAS être détecté
 */
class TestErrorSuppression 
{
    /**
     * Configuration des politiques  
     *
     * @var array<string, string> Ceci non plus ne doit PAS être détecté
     */
    protected $policies = [];

    public function testValidErrorSuppression()
    {
        // Ceci DOIT être détecté comme problématique
        $result = @file_get_contents('nonexistent_file.txt');
        
        // * @param string $file - ceci ne doit PAS être détecté (commentaire)
        
        // Ceci aussi DOIT être détecté
        @mysqli_connect('localhost', 'user', 'password');
        
        /* @deprecated Cette fonction est obsolète - ne doit PAS être détecté */
        
        // Ceci DOIT être détecté
        $data = @json_decode($json_string);
    }
    
    /**
     * Documentation avec @ mais pas de suppression d'erreurs
     * @return array<string, mixed> - ne doit PAS être détecté
     * @throws Exception - ne doit PAS être détecté  
     */
    public function getConfig(): array
    {
        return $this->policies;
    }
}
