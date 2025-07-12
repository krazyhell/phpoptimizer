"""
Système de règles d'optimisation PHP
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Type
from pathlib import Path
import importlib
import inspect


class BaseRule(ABC):
    """Classe de base pour toutes les règles d'optimisation"""
    
    def __init__(self, config):
        self.config = config
        self.rule_config = config.get_rule_config(self.get_rule_name())
    
    @abstractmethod
    def get_rule_name(self) -> str:
        """Retourner le nom unique de la règle"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Retourner la description de la règle"""
        pass
    
    @abstractmethod
    def get_issue_type(self) -> str:
        """Retourner le type de problème détecté par cette règle"""
        pass
    
    @abstractmethod
    def analyze(self, parse_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyser le code et retourner les problèmes détectés
        
        Args:
            parse_result: Résultat du parsing (AST + métadonnées)
            
        Returns:
            Liste des problèmes détectés
        """
        pass
    
    def is_enabled(self) -> bool:
        """Vérifier si la règle est activée"""
        return self.rule_config.enabled
    
    def get_severity(self) -> str:
        """Obtenir le niveau de sévérité de la règle"""
        return self.rule_config.severity.value
    
    def get_category(self) -> str:
        """Obtenir la catégorie de la règle"""
        return self.rule_config.category.value
    
    def get_weight(self) -> int:
        """Obtenir le poids de sévérité de la règle"""
        return self.rule_config.weight.value
    
    def get_param(self, param_name: str, default_value: Any = None) -> Any:
        """Obtenir un paramètre de configuration de la règle"""
        return self.rule_config.params.get(param_name, default_value)
    
    def create_issue(self, message: str, line: int, column: int, 
                    suggestion: str, code_snippet: str = "") -> Dict[str, Any]:
        """Créer un problème détecté"""
        return {
            'rule_name': self.get_rule_name(),
            'message': message,
            'file_path': "",  # Sera rempli par le gestionnaire de règles
            'line': line,
            'column': column,
            'severity': self.get_severity(),
            'category': self.get_category(),
            'weight': self.get_weight(),
            'issue_type': self.get_issue_type(),
            'suggestion': suggestion,
            'code_snippet': code_snippet
        }


class RuleManager:
    """Gestionnaire des règles d'optimisation"""
    
    def __init__(self, config):
        self.config = config
        self.rules: List[BaseRule] = []
        self._load_rules()
    
    def _load_rules(self):
        """Charger toutes les règles disponibles"""
        # Charger les règles intégrées
        self._load_builtin_rules()
        
        # Charger les règles personnalisées (si définies)
        # TODO: Implémenter le chargement de règles personnalisées
    
    def _load_builtin_rules(self):
        """Charger les règles intégrées"""
        from . import rules
        
        # Importer tous les modules de règles
        rule_modules = [
            'rules.performance',
            'rules.security', 
            'rules.best_practices'
        ]
        
        for module_name in rule_modules:
            try:
                module = importlib.import_module(f'phpoptimizer.{module_name}')
                self._register_rules_from_module(module)
            except ImportError:
                # Le module n'existe pas encore, on continue
                pass
    
    def _register_rules_from_module(self, module):
        """Enregistrer toutes les règles d'un module"""
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseRule) and 
                obj != BaseRule):
                
                # Créer une instance de la règle
                rule = obj(self.config)
                if rule.is_enabled():
                    self.rules.append(rule)
    
    def analyze(self, parse_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyser le code avec toutes les règles activées
        
        Args:
            parse_result: Résultat du parsing
            
        Returns:
            Liste de tous les problèmes détectés
        """
        all_issues = []
        
        for rule in self.rules:
            try:
                issues = rule.analyze(parse_result)
                
                # Ajouter le nom du fichier aux problèmes
                for issue in issues:
                    issue['file_path'] = parse_result.get('filename', '')
                
                all_issues.extend(issues)
                
            except Exception as e:
                # Log l'erreur mais continue avec les autres règles
                print(f"Erreur dans la règle {rule.get_rule_name()}: {e}")
        
        return all_issues
    
    def get_rule_count(self) -> int:
        """Obtenir le nombre de règles chargées"""
        return len(self.rules)
    
    def get_rules_by_type(self, issue_type: str) -> List[BaseRule]:
        """Obtenir toutes les règles d'un type donné"""
        return [rule for rule in self.rules if rule.get_issue_type() == issue_type]
