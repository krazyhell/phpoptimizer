# PHP Code Optimizer

Un outil d'analyse et d'optimisation de code PHP écrit en Python.

## Fonctionnalités

- 🔍 **Analyse statique avancée** - Détection de **19 types de problèmes** de performance, sécurité et bonnes pratiques
- ⚡ **Optimisation mémoire** - Détection des oublis de `unset()` pour les gros tableaux (>10k éléments)
- 🗃️ **Détection N+1** - Requêtes SQL inefficaces dans les boucles
- 🔄 **XPath intelligent** - Analyse des sélecteurs XPath lents (`//*`, `contains()`, etc.)
- 📊 **Rapports multi-formats** - Console colorée, HTML interactif, JSON pour CI/CD
- 🎯 **Rules extensibles** - Architecture modulaire pour ajouter de nouvelles règles
- 🧪 **Testé et validé** - Suite de tests complète avec exemples réels

## Installation

```bash
# Cloner le repository
git clone <votre-repo>
cd phpoptimizer

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt

# Installer en mode développement
pip install -e .
```

## Utilisation

### Analyser un fichier PHP
```bash
phpoptimizer analyze examples/performance_test.php --output-format console
```

### Analyser un dossier
```bash
phpoptimizer analyze src/ --recursive --output-format html --output rapport.html
```

### Exemple de sortie
```
============================================================
  RAPPORT D'ANALYSE PHP OPTIMIZER
============================================================
📊 Statistiques: 1 fichier, 19 problèmes détectés
🎯 Sévérité: 2 erreurs, 13 avertissements, 4 infos

📄 examples/performance_test.php
   📍 Ligne 71: Gros tableau $large_array (1000000 éléments) non libéré
   📍 Ligne 11: Requête SQL dans boucle (problème N+1)
   📍 Ligne 23: count() dans condition de boucle for (inefficace)

🏆 Top problèmes: performance.obsolete_function (4x), performance.memory_management (2x)
```

### Options disponibles
- `--recursive, -r` : Analyser récursivement les sous-dossiers
- `--output-format` : Format de sortie (console, json, html)
- `--output, -o` : Fichier de sortie
- `--rules` : Fichier de configuration des règles personnalisées
- `--severity` : Niveau de sévérité minimum (info, warning, error)

## Règles d'optimisation

L'outil détecte actuellement **plus de 15 types de problèmes** répartis en plusieurs catégories :

### 🚀 Performance
- **Boucles inefficaces** : `count()` dans les conditions de boucle, boucles imbriquées trop profondes
- **Requêtes en boucle** : Détection du problème N+1 (requêtes SQL dans les boucles)
- **Gestion mémoire** : Gros tableaux non libérés avec `unset()` (>10 000 éléments)
- **Concaténation inefficace** : Concaténation de chaînes dans les boucles
- **Fonctions obsolètes** : `mysql_query()`, `ereg()`, `split()`, `each()`
- **Suppression d'erreurs** : Usage de `@` qui impact les performances
- **XPath inefficaces** : Sélecteurs descendants (`//*`), `contains()`, double descendant
- **DOM lent** : `getElementById()`, `getElementsByTagName()` dans les boucles
- **Regex inefficaces** : Patterns avec `.*` problématiques
- **Optimisations diverses** : `array_key_exists()` vs `isset()`, ouvertures de fichiers répétées

### 🔒 Sécurité
- **Injections SQL** : Variables non échappées dans les requêtes
- **Vulnérabilités XSS** : Sortie de `$_GET`/`$_POST` non échappée
- **Hachage faible** : `md5()` pour les mots de passe
- **Inclusion dangereuse** : `include` basé sur données utilisateur

### 📏 Bonnes pratiques
- **Standards PSR** : Lignes trop longues (>120 caractères)
- **SELECT optimisé** : Détection de `SELECT *` inefficace
- **Variables inutilisées** : Variables déclarées mais jamais utilisées
- **Calculs répétés** : Expressions mathématiques dupliquées

### Exemples de détection

```php
// ❌ Problème détecté: Gros tableau non libéré
$large_array = range(1, 1000000);
$result = array_sum($large_array);
// Suggestion: Ajouter unset($large_array)

// ❌ Problème détecté: Requête dans boucle (N+1)
foreach ($users as $user) {
    $posts = mysql_query("SELECT * FROM posts WHERE user_id = $user[id]");
}

// ❌ Problème détecté: XPath inefficace
$nodes = $xml->xpath('//*[@active="true"]'); // Très lent

// ✅ Solution recommandée
$nodes = $xml->xpath('/root/items/item[@active="true"]'); // Plus rapide
```

## Développement

### Structure du projet
```
phpoptimizer/
├── phpoptimizer/           # Code source principal
│   ├── __init__.py
│   ├── cli.py             # Interface ligne de commande
│   ├── simple_analyzer.py # Analyseur principal (détection des patterns)
│   ├── config.py          # Configuration
│   ├── reporter.py        # Générateurs de rapports (console, HTML, JSON)
│   └── rules/             # Règles d'optimisation (extensibilité future)
├── tests/                 # Tests unitaires
├── examples/              # Exemples PHP avec problèmes à détecter
│   ├── performance_test.php  # Problèmes de performance avancés
│   ├── xpath_test.php       # Problèmes XPath/XML
│   └── unset_test.php       # Tests gestion mémoire
└── .vscode/               # Configuration VS Code avec tasks.json
```

### Fonctionnalités testées et validées
✅ Détection de **19 types de problèmes** différents  
✅ Gestion mémoire : détection des oublis de `unset()`  
✅ Patterns XPath inefficaces dans les boucles  
✅ Requêtes SQL en boucle (problème N+1)  
✅ Fonctions PHP obsolètes (mysql_*, ereg, etc.)  
✅ Rapports multi-formats (console, HTML, JSON)  
✅ Tests unitaires avec pytest  
✅ Interface CLI avec Click

### Lancer les tests
```bash
python -m pytest tests/
```

### Debugging dans VS Code
Utilisez F5 pour lancer le debugger avec la configuration prédéfinie.

## Contribution

Les contributions sont les bienvenues ! Consultez le fichier CONTRIBUTING.md pour plus de détails.

## Licence

MIT License - voir le fichier LICENSE pour plus de détails.
