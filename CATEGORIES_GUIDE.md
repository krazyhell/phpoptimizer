# Guide d'Utilisation - Catégories et Poids des Règles

PHP Optimizer propose désormais un système avancé de filtrage par catégories et poids de sévérité, rendant l'analyse plus flexible selon vos besoins.

## 📋 Catégories Disponibles

### 🔐 Security (Poids: 4 - Critique)
- `security.sql_injection` - Détection d'injections SQL
- `security.xss_vulnerability` - Vulnérabilités XSS
- `security.weak_password_hashing` - Algorithmes de hachage faibles

### ❌ Error (Poids: 3 - Élevé)
- `error.foreach_non_iterable` - Foreach sur variables non-itérables
- `dead_code.unreachable_after_return` - Code inaccessible
- `dead_code.always_false_condition` - Conditions toujours fausses

### ⚡ Performance.Critical (Poids: 3 - Élevé)
- `performance.inefficient_loops` - Boucles inefficaces
- `performance.algorithmic_complexity` - Complexité algorithmique problématique

### 🚀 Performance.General (Poids: 2 - Moyen)
- `performance.repetitive_array_access` - Accès répétitifs aux tableaux
- `performance.repeated_calculations` - Calculs répétés
- `performance.dynamic_method_call` - Appels de méthodes dynamiques
- `performance.dynamic_function_call` - Appels de fonctions dynamiques

### 🧠 Memory (Poids: 2 - Moyen)
- `performance.large_arrays` - Gros tableaux non libérés
- `performance.unused_variables` - Variables inutilisées
- `performance.unused_global_variable` - Variables globales inutilisées

### 📝 Code_Quality (Poids: 1 - Faible)
- `performance.missing_parameter_type` - Annotations de type manquantes
- `performance.missing_return_type` - Types de retour manquants
- `best_practices.function_complexity` - Complexité des fonctions
- `best_practices.missing_documentation` - Documentation manquante

### 📏 PSR (Poids: 0 - Très Faible)
- `best_practices.psr_compliance` - Conformité PSR générale
- `best_practices.line_length` - Longueur des lignes
- `best_practices.naming` - Conventions de nommage

## ⚖️ Système de Poids

- **4 (Critique)** : Problèmes de sécurité pouvant compromettre l'application
- **3 (Élevé)** : Erreurs bloquantes ou problèmes de performance majeurs  
- **2 (Moyen)** : Optimisations importantes mais non critiques
- **1 (Faible)** : Améliorations de qualité de code
- **0 (Très Faible)** : Standards de formatage et conventions

## 🎯 Exemples d'Utilisation

### Filtrage par Catégorie

```bash
# Seulement les problèmes de sécurité
php-optimizer analyze monfile.php --include-categories=security

# Sécurité et erreurs uniquement
php-optimizer analyze monfile.php --include-categories=security,error

# Exclure les règles PSR
php-optimizer analyze monfile.php --exclude-categories=psr

# Exclure les annotations de type
php-optimizer analyze monfile.php --exclude-categories=code_quality
```

### Filtrage par Poids

```bash
# Seulement les problèmes critiques et élevés (≥ 3)
php-optimizer analyze monfile.php --min-weight=3

# Problèmes moyens et plus (≥ 2)
php-optimizer analyze monfile.php --min-weight=2

# Seulement les problèmes critiques
php-optimizer analyze monfile.php --min-weight=4
```

### Combinaisons

```bash
# Performance critique avec poids élevé minimum
php-optimizer analyze monfile.php --include-categories=performance.critical --min-weight=3

# Sécurité et performance, exclusion PSR
php-optimizer analyze monfile.php --include-categories=security,performance.general --exclude-categories=psr

# Code review : problèmes importants seulement
php-optimizer analyze monfile.php --min-weight=2 --exclude-categories=psr
```

### Cas d'Usage Pratiques

#### 🚨 Audit de Sécurité
```bash
php-optimizer analyze . --recursive --include-categories=security --output-format=html --output=security-report.html
```

#### 🏃‍♂️ Optimisation Performance
```bash
php-optimizer analyze . --recursive --include-categories=performance.critical,performance.general --min-weight=2
```

#### 🧹 Code Review Léger
```bash
php-optimizer analyze . --recursive --min-weight=2 --exclude-categories=psr,code_quality
```

#### 🎯 Focus Erreurs Critiques
```bash
php-optimizer analyze . --recursive --include-categories=security,error --min-weight=3
```

#### 📝 Standards et Qualité
```bash
php-optimizer analyze . --recursive --include-categories=code_quality,psr --max-weight=1
```

## 🔄 Migration depuis l'Ancien Système

Les anciennes options `--include-rules` et `--exclude-rules` continuent de fonctionner et peuvent être combinées avec les nouvelles options de catégories et poids.

```bash
# Ancien système (toujours supporté)
php-optimizer analyze monfile.php --exclude-rules=best_practices.missing_docstring

# Nouveau système équivalent
php-optimizer analyze monfile.php --exclude-categories=code_quality

# Combinaison
php-optimizer analyze monfile.php --include-categories=security --exclude-rules=security.weak_password_hashing
```

Ce système vous permet de créer des profils d'analyse adaptés à différents contextes : développement, code review, audit de sécurité, optimisation performance, etc.
