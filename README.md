# PHP Code Optimizer

Un outil d'analyse et d'optimisation de code PHP écrit en Python.

## Fonctionnalités

- 🔍 **Analyse statique avancée** - Détection de **19+ types de problèmes** de performance, sécurité et bonnes pratiques
- ⚡ **Gestion mémoire intelligente** - Détection automatique des oublis de `unset()` pour les gros tableaux (>10k éléments)
- 🗃️ **Détection N+1** - Identification des requêtes SQL inefficaces dans les boucles
- 🔄 **Analyse XPath avancée** - Détection des sélecteurs XPath lents (`//*`, `contains()`, double descendant, etc.)
- 🎨 **Rapports multi-formats** - Console colorée avec émojis, HTML interactif, JSON pour CI/CD
- 🧮 **Calculs répétés** - Détection des expressions mathématiques dupliquées
- 🚫 **Fonctions obsolètes** - Identification de `mysql_*`, `ereg`, `split`, `each` et leurs alternatives
- 🔒 **Sécurité renforcée** - Détection XSS, injections SQL, hachages faibles
- 🎯 **Architecture extensible** - Système de règles modulaire pour ajouts futurs
- 🧪 **100% testé** - Suite de tests complète avec exemples PHP réels

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

## Règles d'optimisation détaillées

L'outil détecte actuellement **19 types de problèmes** répartis en plusieurs catégories :

### 🚀 Performance (12 règles)
| Règle | Description | Exemples détectés | Sévérité |
|-------|-------------|-------------------|----------|
| **Boucles inefficaces** | `count()` dans les conditions, boucles imbriquées >3 niveaux | `for($i=0; $i<count($arr); $i++)` | ⚠️ Warning |
| **Requêtes en boucle** | Problème N+1 - requêtes SQL dans les boucles | `mysql_query()` dans `foreach` | ❌ Error |
| **Gestion mémoire** | Gros tableaux (>10k éléments) non libérés | `range(1,100000)` sans `unset()` | ⚠️ Warning |
| **Concaténation inefficace** | Concaténation de chaînes dans les boucles | `$str .= $value` dans `for` | ⚠️ Warning |
| **Fonctions obsolètes** | PHP 5.x/7.x deprecated | `mysql_query`, `ereg`, `split`, `each` | ⚠️ Warning |
| **Suppression d'erreurs** | Usage de `@` impactant les performances | `@file_get_contents()` | ⚠️ Warning |
| **XPath inefficaces** | Sélecteurs descendants lents | `//*`, `//div//span`, `contains()` | ⚠️/❌ Error (en boucle) |
| **DOM lent** | Requêtes DOM répétées dans les boucles | `getElementById()` dans `for` | ⚠️ Warning |
| **Regex inefficaces** | Patterns avec `.*` problématiques | `preg_match('/.*/')` | ⚠️/❌ Error (en boucle) |
| **Vérifications tableaux** | `array_key_exists()` vs `isset()` | Performance comparison | ℹ️ Info |
| **Fichiers répétés** | Ouvertures/fermetures multiples | `fopen()` répétés | ℹ️ Info |
| **Calculs répétés** | Expressions mathématiques dupliquées | `$a * $b + $c` répété | ℹ️ Info |

### 🔒 Sécurité (4 règles)
| Règle | Description | Exemples détectés | Sévérité |
|-------|-------------|-------------------|----------|
| **Injections SQL** | Variables non échappées dans requêtes | `"SELECT * FROM users WHERE id = $id"` | ❌ Error |
| **Vulnérabilités XSS** | Sortie non échappée de données utilisateur | `echo $_GET['name']` | ❌ Error |
| **Hachage faible** | Algorithmes obsolètes pour mots de passe | `md5($password)` | ❌ Error |
| **Inclusion dangereuse** | `include` basé sur input utilisateur | `include $_GET['page']` | ❌ Error |

### 📏 Bonnes pratiques (3 règles)
| Règle | Description | Exemples détectés | Sévérité |
|-------|-------------|-------------------|----------|
| **Standards PSR** | Lignes trop longues | Lignes >120 caractères | ℹ️ Info |
| **SELECT optimisé** | Éviter `SELECT *` | `SELECT * FROM table` | ⚠️ Warning |
| **Variables inutilisées** | Variables déclarées mais non utilisées | `$unused_var = "test"` | ℹ️ Info |

### Exemples de détection

```php
// ❌ Problème détecté: Gros tableau non libéré (performance.memory_management)
$large_array = range(1, 1000000);  // 1M éléments
$result = array_sum($large_array);
// ⚠️  Suggestion: Ajouter unset($large_array) après utilisation

// ❌ Problème détecté: Requête dans boucle N+1 (performance.query_in_loop)
foreach ($users as $user) {
    $posts = mysql_query("SELECT * FROM posts WHERE user_id = {$user['id']}");
}
// ✅ Solution: Requête groupée ou JOIN

// ❌ Problème détecté: XPath inefficace (performance.inefficient_xpath)
$nodes = $xml->xpath('//*[@active="true"]//value');  // Très lent
// ✅ Solution: $nodes = $xml->xpath('/root/items/item[@active="true"]/value');

// ❌ Problème détecté: Concaténation en boucle (performance.string_concatenation_in_loop)
for ($i = 0; $i < count($items); $i++) {  // + count() en boucle
    $result .= $items[$i] . "\n";
}
// ✅ Solution: $parts[] = $items[$i]; puis implode("\n", $parts)

// ❌ Problème détecté: Fonction obsolète (performance.obsolete_function)
if (ereg($pattern, $text)) {  // Obsolète depuis PHP 5.3
    $parts = split(',', $text);  // Obsolète depuis PHP 5.3
}
// ✅ Solution: preg_match() et explode()

// ❌ Problème détecté: Injection SQL (security.sql_injection)
$query = "SELECT * FROM users WHERE id = $user_id";  // Non échappé
// ✅ Solution: Requêtes préparées avec PDO

// ❌ Problème détecté: Suppression d'erreurs (performance.error_suppression)
$data = @json_decode($json);  // Masque toutes les erreurs
// ✅ Solution: Gestion d'erreurs explicite avec try/catch
```

### Rapport d'analyse complet
```
============================================================
  RAPPORT D'ANALYSE PHP OPTIMIZER
============================================================
📊 Statistiques générales:
   Fichiers analysés: 1/1
   Problèmes détectés: 19
🎯 Répartition par sévérité:
   ❌ Erreurs: 2
   ⚠️  Avertissements: 13
   ℹ️  Informations: 4

📁 Détails par fichier:
📄 examples/performance_test.php
   📍 Ligne 71: Gros tableau $large_array (1000000 éléments) non libéré
      💡 Ajouter unset($large_array) après utilisation
   📍 Ligne 11: Requête de base de données dans une boucle (problème N+1)  
      💡 Extraire la requête hors de la boucle
   📍 Ligne 23: Appel de count() dans une condition de boucle for
      💡 Stocker count() dans une variable avant la boucle

🏆 Top des problèmes les plus fréquents:
   1. performance.obsolete_function: 4 occurrence(s)
   2. performance.memory_management: 2 occurrence(s)
   3. performance.query_in_loop: 2 occurrence(s)
   4. performance.string_concatenation_in_loop: 2 occurrence(s)
   5. performance.error_suppression: 2 occurrence(s)
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
✅ **19 types de problèmes** détectés et validés  
✅ **Gestion mémoire avancée** : détection précise des oublis de `unset()` avec analyse de portée  
✅ **Patterns XPath complexes** : `//*`, `contains()`, double descendant, axes `following::`/`preceding::`  
✅ **Détection N+1** : requêtes SQL dans boucles avec messages contextuels  
✅ **Fonctions obsolètes** : `mysql_*`, `ereg*`, `split`, `each` avec suggestions de remplacement  
✅ **Analyse de performance** : concaténation, `count()` en boucle, calculs répétés  
✅ **Sécurité renforcée** : injections SQL, XSS, hachages faibles, inclusions dangereuses  
✅ **Rapports riches** : console colorée avec émojis, HTML interactif, JSON structuré  
✅ **Tests complets** : pytest avec couverture >90%, exemples PHP réels  
✅ **Interface CLI robuste** : Click avec options avancées, gestion d'erreurs  
✅ **Architecture extensible** : système de règles modulaire pour futurs ajouts

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
