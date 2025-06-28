# Guide de contribution - PHP Optimizer

Merci de votre intérêt pour contribuer à PHP Optimizer ! Ce guide vous aidera à démarrer.

## Types de contributions

### 🐛 Signaler des bugs
- Utilisez le template d'issue GitHub
- Incluez un exemple de code PHP minimal qui reproduit le problème
- Précisez la version de Python et l'OS utilisé
- Décrivez le comportement attendu vs observé

### 💡 Proposer des fonctionnalités
- Ouvrez une issue pour discuter l'idée avant de coder
- Décrivez le pattern PHP que vous voulez détecter
- Expliquez pourquoi c'est un problème de performance/sécurité
- Proposez des suggestions d'amélioration

### 🔧 Contribuer au code
- Fork le repository
- Créez une branch pour votre fonctionnalité : `git checkout -b feature/nouvelle-regle`
- Suivez les conventions de code (voir ci-dessous)
- Ajoutez des tests pour votre contribution
- Soumettez une pull request

## Setup de développement

```bash
# 1. Fork et cloner
git clone https://github.com/votre-username/phpoptimizer.git
cd phpoptimizer

# 2. Environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou .\venv\Scripts\Activate  # Windows

# 3. Installation en mode développement
pip install -r requirements.txt
pip install -e .

# 4. Vérifier que tout fonctionne
python -m pytest tests/
python -m phpoptimizer.cli analyze examples/performance_test.php
```

## Structure du code

```
phpoptimizer/
├── phpoptimizer/
│   ├── simple_analyzer.py    # ⭐ Analyseur principal - ajoutez vos règles ici
│   ├── cli.py               # Interface ligne de commande
│   ├── reporter.py          # Génération des rapports
│   ├── config.py            # Gestion de la configuration
│   └── rules/               # 🚧 Futur système de règles modulaires
├── tests/
│   ├── test_analyzer.py     # ⭐ Tests principaux - ajoutez vos tests ici
│   └── test_*.py           # Tests spécialisés
└── examples/
    ├── *.php               # ⭐ Exemples de code - ajoutez vos cas de test
```

## Ajouter une nouvelle règle de détection

### 1. Identifier le pattern problématique

Exemple : détection de `array_push()` dans une boucle

```php
// ❌ Inefficace
for ($i = 0; $i < 1000; $i++) {
    array_push($array, $value);  // Réallocation à chaque itération
}

// ✅ Efficace
$array[] = $value;  // Ou collecte puis array_merge
```

### 2. Ajouter la détection dans `simple_analyzer.py`

```python
# Dans la boucle d'analyse des lignes
if (in_loop and loop_stack and 
    re.search(r'\barray_push\s*\(', line_stripped)):
    issues.append({
        'rule_name': 'performance.array_push_in_loop',
        'message': 'array_push() dans une boucle est inefficace',
        'file_path': str(file_path),
        'line': line_num,
        'column': 0,
        'severity': 'warning',
        'issue_type': 'performance',
        'suggestion': 'Utiliser $array[] = $value ou array_merge() après la boucle',
        'code_snippet': line.strip()
    })
```

### 3. Ajouter un test

```python
# Dans tests/test_analyzer.py
def test_array_push_in_loop():
    php_code = '''<?php
    for ($i = 0; $i < 100; $i++) {
        array_push($data, $i);  // Devrait être détecté
    }
    ?>'''
    
    issues = analyze_php_code(php_code)
    array_push_issues = [i for i in issues if i['rule_name'] == 'performance.array_push_in_loop']
    
    assert len(array_push_issues) == 1
    assert array_push_issues[0]['line'] == 3
    assert array_push_issues[0]['severity'] == 'warning'
```

### 4. Ajouter un exemple de fichier PHP

```php
<?php
// examples/array_push_test.php
// Test de détection d'array_push en boucle

for ($i = 0; $i < 1000; $i++) {
    array_push($large_array, $value);  // ❌ Devrait être détecté
}

$small_array[] = $value;  // ✅ Ne devrait pas être détecté
?>
```

### 5. Tester votre contribution

```bash
# Tests unitaires
python -m pytest tests/test_analyzer.py::test_array_push_in_loop -v

# Test sur l'exemple
python -m phpoptimizer.cli analyze examples/array_push_test.php -v

# Tests complets
python -m pytest tests/
```

## Conventions de code

### Style Python
- **PEP 8** : Utilisez `black` pour le formatage : `pip install black && black .`
- **Type hints** : Ajoutez des annotations de type
- **Docstrings** : Documentez les fonctions publiques
- **Noms descriptifs** : `detect_inefficient_loops()` plutôt que `check_loops()`

### Messages d'erreur
- **Clairs et actionables** : "Utilisez isset() au lieu de array_key_exists()"
- **Contextuels** : Mentionnez pourquoi c'est problématique
- **Suggérez des solutions** : Proposez une alternative

### Tests
- **Un test par règle** : Testez chaque pattern individuellement
- **Cas négatifs** : Vérifiez que les bons patterns ne sont pas détectés
- **Cas limites** : Testez les edge cases (syntaxe complexe, imbrication, etc.)

### Exemples PHP
- **Commentaires explicites** : Marquez ce qui devrait être détecté
- **Variété** : Incluez différents niveaux de complexité
- **Réalistes** : Basez-vous sur du code PHP réel

## Processus de review

### Avant de soumettre
1. ✅ Tests passent : `python -m pytest tests/`
2. ✅ Formatage correct : `black phpoptimizer/ tests/`
3. ✅ Exemple fonctionne : Test sur un fichier PHP réel
4. ✅ Documentation mise à jour : README si nécessaire

### Pull Request
- **Titre descriptif** : "Ajouter détection array_push() en boucle"
- **Description détaillée** : Expliquez le problème détecté et la solution
- **Captures d'écran** : Montrez l'output avant/après si pertinent
- **Tests inclus** : Mentionnez les tests ajoutés

### Critères d'acceptation
- ✅ **Fonctionnel** : La règle détecte correctement les problèmes
- ✅ **Pas de faux positifs** : Ne signale pas de code correct
- ✅ **Performance** : N'impact pas significativement le temps d'analyse
- ✅ **Testé** : Couverture de test appropriée
- ✅ **Documenté** : Messages clairs et README mis à jour

## Règles prioritaires recherchées

### Performance
- [ ] `array_push()` dans les boucles
- [ ] `array_merge()` répété vs accumulation
- [ ] `in_array()` sur de gros tableaux (suggérer `isset()` avec flip)
- [ ] Allocation de strings avec `str_repeat()` vs concaténation
- [ ] `file_get_contents()` vs `fread()` pour gros fichiers

### Sécurité
- [ ] `eval()` avec input utilisateur
- [ ] `serialize()`/`unserialize()` sans validation
- [ ] `extract()` avec données externes
- [ ] Headers HTTP non échappés
- [ ] Cookies sans flags sécurisés

### Bonnes pratiques PHP 8+
- [ ] `array_key_exists()` vs `isset()` avec null coalescing
- [ ] Fonctions arrow vs anonymous classiques
- [ ] `match` vs `switch` pour de meilleures performances
- [ ] Attributes vs annotations docblock

## Questions ?

- 💬 **Discussions GitHub** : Pour les questions générales
- 🐛 **Issues** : Pour les bugs et propositions de fonctionnalités

Merci de contribuer à améliorer PHP Optimizer ! 🚀
