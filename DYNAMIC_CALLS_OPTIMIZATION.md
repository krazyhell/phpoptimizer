# Optimisation des Appels Dynamiques

## Présentation

L'analyseur d'appels dynamiques de PHP Optimizer détecte les cas où des appels de méthodes ou fonctions dynamiques peuvent être remplacés par des appels directs pour améliorer les performances.

## Types d'optimisations détectées

### 1. Appels de méthodes dynamiques

**Avant optimisation :**
```php
$method = 'calculateScore';
$result = $object->$method($value);
```

**Après optimisation :**
```php
$result = $object->calculateScore($value);
```

### 2. Appels de fonctions dynamiques

**Avant optimisation :**
```php
$function = 'strtoupper';
$output = $function($input);
```

**Après optimisation :**
```php
$output = strtoupper($input);
```

## Avantages de l'optimisation

1. **Performance améliorée** : Les appels directs sont plus rapides que les appels dynamiques
2. **Meilleure lisibilité** : Le code est plus explicite et facile à comprendre
3. **Analyse statique** : Les IDE et outils d'analyse peuvent mieux comprendre le code
4. **Optimisation du cache d'opcodes** : PHP peut mieux optimiser les appels directs

## Niveau de confiance

L'analyseur calcule un niveau de confiance pour chaque suggestion :

- **Confiance élevée (0.9)** : Variable assignée une seule fois avec une valeur constante
- **Confiance faible (0.1)** : Variable réassignée (ne sera pas suggérée)

## Cas d'usage réels

### Validation de données
```php
// Avant
$validationMethod = 'validateEmail';
if (!$this->$validationMethod($email)) {
    return false;
}

// Après
if (!$this->validateEmail($email)) {
    return false;
}
```

### Transformation de données
```php
// Avant
$sanitizer = 'htmlspecialchars';
$data['name'] = $sanitizer($data['name']);
$data['bio'] = $sanitizer($data['bio']);

// Après
$data['name'] = htmlspecialchars($data['name']);
$data['bio'] = htmlspecialchars($data['bio']);
```

### Hachage de mots de passe
```php
// Avant
$hashFunction = 'password_hash';
$hashedPassword = $hashFunction($password, PASSWORD_DEFAULT);

// Après
$hashedPassword = password_hash($password, PASSWORD_DEFAULT);
```

## Cas non détectés (par conception)

L'analyseur ne suggère pas d'optimisation dans les cas suivants :

### Variables modifiées
```php
$method = 'get';
if ($usePost) {
    $method = 'post';  // Réassignation détectée
}
$response = $client->$method($url);  // Pas d'optimisation suggérée
```

### Variables de boucle
```php
$functions = ['strlen', 'trim', 'strtolower'];
foreach ($functions as $func) {
    $result = $func($input);  // Variable de boucle, pas d'optimisation
}
```

## Configuration

Cette optimisation est activée par défaut et fait partie de l'analyseur de performance. Elle peut être désactivée en excluant la règle :

```bash
python -m phpoptimizer analyze file.php --exclude-rules performance.dynamic_method_call,performance.dynamic_function_call
```

## Impact sur les performances

Les tests de performance montrent une amélioration de 5-15% sur les opérations répétitives utilisant des appels dynamiques, particulièrement visible dans :

- Les boucles avec appels de fonctions
- Les validations en chaîne
- Les transformations de données

## Intégration

Cette fonctionnalité est intégrée dans :
- L'analyseur principal (`SimpleAnalyzer`)
- Les rapports console, JSON et HTML
- L'interface en ligne de commande VS Code

## Exemples de rapports

Voir `rapport_dynamic_calls.html` pour un exemple complet d'analyse avec cette optimisation.
