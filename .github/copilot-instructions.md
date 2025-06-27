<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Instructions Copilot pour PHP Optimizer

Ce projet est un analyseur et optimiseur de code PHP écrit en Python.

## Architecture du projet

- **phpoptimizer/**: Package principal
  - **cli.py**: Interface en ligne de commande
  - **simple_analyzer.py**: Analyseur simplifié principal
  - **parser.py**: Parseur PHP utilisant phply
  - **config.py**: Gestion de la configuration
  - **reporter.py**: Générateur de rapports (console, JSON, HTML)
  - **rules/**: Système de règles d'optimisation
    - **performance.py**: Règles de performance
    - **security.py**: Règles de sécurité  
    - **best_practices.py**: Règles de bonnes pratiques

## Conventions de développement

- Utiliser des docstrings pour toutes les fonctions publiques
- Respecter les types hints Python
- Privilégier la lisibilité du code
- Utiliser des noms de variables descriptifs
- Écrire des tests unitaires pour les nouvelles fonctionnalités

## Objectifs du projet

- Détecter les vulnérabilités de sécurité communes (SQL injection, XSS, etc.)
- Identifier les problèmes de performance (boucles inefficaces, variables inutilisées)
- Vérifier la conformité aux bonnes pratiques PHP et PSR
- Générer des rapports détaillés avec suggestions d'amélioration

## Technologie utilisée

- Python 3.8+
- Click pour l'interface CLI
- phply pour l'analyse syntaxique PHP
- Colorama pour la sortie colorée
- Génération HTML pour les rapports
