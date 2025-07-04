<?php
/**
 * Exemple de fichier PHP pour tester la détection des type hints manquants
 * Ce fichier contient volontairement des fonctions sans type hints pour démonstration
 */

// ❌ Fonction sans types de paramètres ni de retour
function calculateTotal($items, $tax) {
    $sum = 0;
    foreach ($items as $item) {
        $sum += $item;
    }
    return $sum * (1 + $tax);
}

// ❌ Fonction avec utilisation claire de types mais pas déclarés
function getUserById($id) {
    // Usage suggère que $id est un int
    if ($id > 0) {
        return findUserInDatabase($id);
    }
    return null;
}

// ❌ Fonction avec manipulation de chaînes
function formatName($firstName, $lastName) {
    return trim($firstName) . ' ' . trim($lastName);
}

// ❌ Fonction avec vérifications de type explicites
function processArray($data) {
    if (is_array($data)) {
        return count($data);
    }
    return 0;
}

// ❌ Fonction avec opérations arithmétiques
function calculatePrice($quantity, $unitPrice, $discount) {
    return ($quantity * $unitPrice) * (1 - $discount);
}

// ❌ Fonction avec retour booléen évident
function isValidEmail($email) {
    return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
}

// ❌ Fonction avec manipulation d'array
function getActiveUsers($users) {
    $active = [];
    foreach ($users as $user) {
        if ($user['active']) {
            $active[] = $user;
        }
    }
    return $active;
}

// ❌ Fonction avec retour de chaîne
function generateSlug($title) {
    return strtolower(str_replace(' ', '-', $title));
}

// ✅ Exemple de fonction bien typée (pour comparaison)
function calculateTotalTyped(array $items, float $tax): float {
    $sum = 0.0;
    foreach ($items as $item) {
        $sum += $item;
    }
    return $sum * (1 + $tax);
}

// ❌ Fonction avec nullable qui pourrait être typé
function findUserByEmail($email) {
    $users = getUsersFromDb();
    foreach ($users as $user) {
        if ($user['email'] === $email) {
            return $user;
        }
    }
    return null;
}

// ❌ Classe avec méthodes non typées
class Calculator {
    
    // ❌ Méthode sans types
    public function add($a, $b) {
        return $a + $b;
    }
    
    // ❌ Méthode avec usage évident d'array
    public function sumArray($numbers) {
        return array_sum($numbers);
    }
    
    // ❌ Méthode avec retour booléen
    public function isPositive($number) {
        return $number > 0;
    }
}

// ❌ Fonction avec gestion d'erreur suggérant un type nullable
function getConfigValue($key) {
    global $config;
    if (isset($config[$key])) {
        return $config[$key];
    }
    return null;
}

// ❌ Fonction avec usage de strlen (suggère string)
function validatePassword($password) {
    return strlen($password) >= 8;
}
