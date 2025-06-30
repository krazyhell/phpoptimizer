# Guide d'utilisation VS Code pour PHP Optimizer

## Résolution de l'erreur `${file}`

### Problème
L'erreur "Variable ${file} can not be resolved. Please open an editor." apparaît quand :
- Aucun fichier n'est ouvert dans l'éditeur VS Code
- La tâche est exécutée sans contexte de fichier actif

### Solutions

#### **Solution 1 : Ouvrir un fichier avant d'exécuter la tâche**
1. **Ouvrez un fichier PHP** dans l'éditeur (double-clic sur le fichier)
2. **Assurez-vous que l'onglet est actif** (sélectionné)
3. **Exécutez la tâche** via `Ctrl+Shift+P` → "Tasks: Run Task" → "Analyser fichier PHP"

#### **Solution 2 : Utiliser les tâches alternatives**
Les nouvelles tâches disponibles :

- **"Analyser fichier PHP"** : Analyse le fichier actuellement ouvert (nécessite `${file}`)
- **"Analyser fichier sélectionné (saisie manuelle)"** : Permet de saisir le chemin du fichier
- **"Analyser projet PHP"** : Analyse tout le dossier `examples/`
- **"Générer rapport HTML"** : Génère un rapport HTML complet
- **"Analyser fichier demo"** : Analyse directement `examples/demo_complet.php`

## Utilisation recommandée

### Pour analyser un fichier spécifique :
1. **Ouvrez le fichier** dans VS Code
2. **Ctrl+Shift+P** → "Tasks: Run Task" → "Analyser fichier PHP"

### Pour analyser sans ouvrir de fichier :
1. **Ctrl+Shift+P** → "Tasks: Run Task" → "Analyser fichier sélectionné"
2. **Saisissez le chemin** (ex: `examples/demo_complet.php`)

### Pour une analyse complète :
1. **Ctrl+Shift+P** → "Tasks: Run Task" → "Analyser projet PHP"

## Variables VS Code disponibles

- `${workspaceFolder}` : Chemin vers le dossier de travail
- `${file}` : Chemin vers le fichier actuellement ouvert ⚠️
- `${fileBasename}` : Nom du fichier (avec extension)
- `${fileDirname}` : Dossier contenant le fichier
- `${input:variableName}` : Demande une saisie utilisateur

## Raccourcis utiles

- **Ctrl+Shift+P** : Palette de commandes
- **Ctrl+Shift+`** : Ouvrir un nouveau terminal
- **Ctrl+`** : Basculer le terminal

## Test rapide

Pour tester le système immédiatement :
```bash
python -m phpoptimizer analyze examples/demo_complet.php --verbose
```
