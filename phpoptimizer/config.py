"""
Configuration du système PHP Optimizer
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum


class SeverityLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class RuleConfig:
    """Configuration d'une règle d'optimisation"""
    enabled: bool = True
    severity: SeverityLevel = SeverityLevel.WARNING
    params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}


class Config:
    """Gestionnaire de configuration pour PHP Optimizer"""
    
    def __init__(self):
        self.severity_level = SeverityLevel.INFO
        self.rules: Dict[str, RuleConfig] = {}
        self.excluded_paths: List[str] = []
        self.included_extensions: List[str] = ['.php']
        self.max_file_size: int = 10 * 1024 * 1024  # 10MB
        
        # Initialiser les règles par défaut
        self._init_default_rules()
    
    def _init_default_rules(self):
        """Initialiser les règles par défaut"""
        default_rules = {
            # Règles de performance
            'performance.inefficient_loops': RuleConfig(
                enabled=True,
                severity=SeverityLevel.WARNING,
                params={'max_nested_loops': 3}
            ),
            'performance.unused_variables': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO
            ),
            'performance.repeated_calculations': RuleConfig(
                enabled=True,
                severity=SeverityLevel.WARNING
            ),
            'performance.large_arrays': RuleConfig(
                enabled=True,
                severity=SeverityLevel.WARNING,
                params={'max_array_size': 1000}
            ),
            
            # Règles de sécurité
            'security.sql_injection': RuleConfig(
                enabled=True,
                severity=SeverityLevel.ERROR
            ),
            'security.xss_vulnerability': RuleConfig(
                enabled=True,
                severity=SeverityLevel.ERROR
            ),
            'security.weak_password_hashing': RuleConfig(
                enabled=True,
                severity=SeverityLevel.ERROR
            ),
            
            # Règles de bonnes pratiques
            'best_practices.psr_compliance': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO
            ),
            'best_practices.function_complexity': RuleConfig(
                enabled=True,
                severity=SeverityLevel.WARNING,
                params={'max_complexity': 10}
            ),
            'best_practices.missing_documentation': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO
            ),
        }
        
        self.rules.update(default_rules)
    
    def load_rules_file(self, file_path: Path):
        """Charger les règles depuis un fichier JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Mettre à jour la configuration
            if 'severity_level' in data:
                self.severity_level = SeverityLevel(data['severity_level'])
            
            if 'excluded_paths' in data:
                self.excluded_paths = data['excluded_paths']
            
            if 'rules' in data:
                for rule_name, rule_data in data['rules'].items():
                    if rule_name in self.rules:
                        # Mettre à jour la règle existante
                        self.rules[rule_name].enabled = rule_data.get('enabled', True)
                        self.rules[rule_name].severity = SeverityLevel(
                            rule_data.get('severity', 'warning')
                        )
                        self.rules[rule_name].params.update(
                            rule_data.get('params', {})
                        )
                        
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement du fichier de règles: {e}")
    
    def save_default_config(self, file_path: Path):
        """Sauvegarder la configuration par défaut dans un fichier"""
        config_data = {
            'severity_level': self.severity_level.value,
            'excluded_paths': self.excluded_paths,
            'included_extensions': self.included_extensions,
            'max_file_size': self.max_file_size,
            'rules': {}
        }
        
        # Convertir les règles en dictionnaire
        for rule_name, rule_config in self.rules.items():
            config_data['rules'][rule_name] = {
                'enabled': rule_config.enabled,
                'severity': rule_config.severity.value,
                'params': rule_config.params
            }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def set_severity_level(self, level: str):
        """Définir le niveau de sévérité minimum"""
        self.severity_level = SeverityLevel(level)
    
    def is_rule_enabled(self, rule_name: str) -> bool:
        """Vérifier si une règle est activée"""
        return rule_name in self.rules and self.rules[rule_name].enabled
    
    def get_rule_config(self, rule_name: str) -> RuleConfig:
        """Obtenir la configuration d'une règle"""
        return self.rules.get(rule_name, RuleConfig())
    
    def should_process_file(self, file_path: Path) -> bool:
        """Vérifier si un fichier doit être traité"""
        # Vérifier l'extension
        if file_path.suffix not in self.included_extensions:
            return False
        
        # Vérifier les chemins exclus
        file_str = str(file_path)
        for excluded in self.excluded_paths:
            if excluded in file_str:
                return False
        
        # Vérifier la taille du fichier
        try:
            if file_path.stat().st_size > self.max_file_size:
                return False
        except OSError:
            return False
        
        return True
