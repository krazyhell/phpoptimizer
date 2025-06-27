#!/usr/bin/env python3

import sys
sys.path.append('.')

from phpoptimizer.simple_analyzer import SimpleAnalyzer
from phpoptimizer.config import Config
from pathlib import Path

# Créer l'analyseur
config = Config()
analyzer = SimpleAnalyzer(config)

# Analyser le fichier
result = analyzer.analyze_file(Path('examples/performance_test.php'))

# Afficher les problèmes de gestion mémoire
print(f"Total des problèmes détectés: {len(result['issues'])}")
print()

memory_issues = [issue for issue in result['issues'] if issue['rule_name'] == 'performance.memory_management']

if memory_issues:
    print(f"Problèmes de gestion mémoire détectés: {len(memory_issues)}")
    print("=" * 50)
    for issue in memory_issues:
        print(f"Ligne {issue['line']}: {issue['message']}")
        print(f"Suggestion: {issue['suggestion']}")
        print(f"Code: {issue['code_snippet']}")
        print("-" * 30)
else:
    print("Aucun problème de gestion mémoire détecté.")

# Afficher tous les types de problèmes
print("\nRépartition par type de règle:")
rule_count = {}
for issue in result['issues']:
    rule_name = issue['rule_name']
    rule_count[rule_name] = rule_count.get(rule_name, 0) + 1

for rule, count in sorted(rule_count.items(), key=lambda x: x[1], reverse=True):
    print(f"  {rule}: {count}")
