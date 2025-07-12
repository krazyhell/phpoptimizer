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


class RuleCategory(Enum):
    """Catégories de règles d'optimisation"""
    SECURITY = "security"
    ERROR = "error" 
    PERFORMANCE_CRITICAL = "performance.critical"
    PERFORMANCE_GENERAL = "performance.general"
    MEMORY = "memory"
    CODE_QUALITY = "code_quality"
    PSR = "psr"


class SeverityWeight(Enum):
    """Poids de sévérité pour le filtrage"""
    CRITICAL = 4  # Problèmes de sécurité
    HIGH = 3      # Erreurs bloquantes ou performance majeure
    MEDIUM = 2    # Optimisations importantes
    LOW = 1       # Qualité de code
    VERY_LOW = 0  # Standards de formatage


@dataclass
class RuleConfig:
    """Configuration d'une règle d'optimisation"""
    enabled: bool = True
    severity: SeverityLevel = SeverityLevel.WARNING
    category: RuleCategory = RuleCategory.CODE_QUALITY
    weight: SeverityWeight = SeverityWeight.LOW
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
        self.php_version: str = "8.0"  # Version PHP cible par défaut
        
        # Nouveaux filtres par catégorie et poids
        self.included_categories: List[RuleCategory] = []
        self.excluded_categories: List[RuleCategory] = []
        self.min_severity_weight: SeverityWeight = SeverityWeight.VERY_LOW
        
        # Initialiser les règles par défaut
        self._init_default_rules()
    
    def _init_default_rules(self):
        """Initialiser les règles par défaut"""
        default_rules = {
            # Règles de sécurité - Poids CRITICAL
            'security.sql_injection': RuleConfig(
                enabled=True,
                severity=SeverityLevel.ERROR,
                category=RuleCategory.SECURITY,
                weight=SeverityWeight.CRITICAL
            ),
            'security.xss_vulnerability': RuleConfig(
                enabled=True,
                severity=SeverityLevel.ERROR,
                category=RuleCategory.SECURITY,
                weight=SeverityWeight.CRITICAL
            ),
            'security.weak_password_hashing': RuleConfig(
                enabled=True,
                severity=SeverityLevel.ERROR,
                category=RuleCategory.SECURITY,
                weight=SeverityWeight.CRITICAL
            ),
            
            # Règles d'erreur - Poids HIGH
            'error.foreach_non_iterable': RuleConfig(
                enabled=True,
                severity=SeverityLevel.ERROR,
                category=RuleCategory.ERROR,
                weight=SeverityWeight.HIGH
            ),
            'dead_code.unreachable_after_return': RuleConfig(
                enabled=True,
                severity=SeverityLevel.WARNING,
                category=RuleCategory.ERROR,
                weight=SeverityWeight.HIGH
            ),
            'dead_code.always_false_condition': RuleConfig(
                enabled=True,
                severity=SeverityLevel.WARNING,
                category=RuleCategory.ERROR,
                weight=SeverityWeight.HIGH
            ),
            
            # Règles de performance critique - Poids HIGH
            'performance.inefficient_loops': RuleConfig(
                enabled=True,
                severity=SeverityLevel.WARNING,
                category=RuleCategory.PERFORMANCE_CRITICAL,
                weight=SeverityWeight.HIGH,
                params={'max_nested_loops': 3}
            ),
            'performance.algorithmic_complexity': RuleConfig(
                enabled=True,
                severity=SeverityLevel.WARNING,
                category=RuleCategory.PERFORMANCE_CRITICAL,
                weight=SeverityWeight.HIGH
            ),
            
            # Règles de performance générale - Poids MEDIUM
            'performance.constant_propagation': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO,
                category=RuleCategory.PERFORMANCE_GENERAL,
                weight=SeverityWeight.MEDIUM
            ),
            'performance.repeated_calculations': RuleConfig(
                enabled=True,
                severity=SeverityLevel.WARNING,
                category=RuleCategory.PERFORMANCE_GENERAL,
                weight=SeverityWeight.MEDIUM
            ),
            'performance.repetitive_array_access': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO,
                category=RuleCategory.PERFORMANCE_GENERAL,
                weight=SeverityWeight.MEDIUM,
                params={'min_occurrences': 3}
            ),
            'performance.dynamic_method_call': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO,
                category=RuleCategory.PERFORMANCE_GENERAL,
                weight=SeverityWeight.MEDIUM
            ),
            'performance.dynamic_function_call': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO,
                category=RuleCategory.PERFORMANCE_GENERAL,
                weight=SeverityWeight.MEDIUM
            ),
            
            # Règles de mémoire - Poids MEDIUM
            'performance.large_arrays': RuleConfig(
                enabled=True,
                severity=SeverityLevel.WARNING,
                category=RuleCategory.MEMORY,
                weight=SeverityWeight.MEDIUM,
                params={'max_array_size': 1000}
            ),
            'performance.unused_variables': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO,
                category=RuleCategory.MEMORY,
                weight=SeverityWeight.MEDIUM
            ),
            'performance.unused_global_variable': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO,
                category=RuleCategory.MEMORY,
                weight=SeverityWeight.MEDIUM
            ),
            'performance.global_could_be_local': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO,
                category=RuleCategory.MEMORY,
                weight=SeverityWeight.MEDIUM
            ),
            
            # Règles de qualité de code - Poids LOW
            'performance.missing_parameter_type': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO,
                category=RuleCategory.CODE_QUALITY,
                weight=SeverityWeight.LOW
            ),
            'performance.missing_return_type': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO,
                category=RuleCategory.CODE_QUALITY,
                weight=SeverityWeight.LOW
            ),
            'performance.mixed_type_opportunity': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO,
                category=RuleCategory.CODE_QUALITY,
                weight=SeverityWeight.LOW
            ),
            'best_practices.function_complexity': RuleConfig(
                enabled=True,
                severity=SeverityLevel.WARNING,
                category=RuleCategory.CODE_QUALITY,
                weight=SeverityWeight.LOW,
                params={'max_complexity': 10}
            ),
            'best_practices.missing_documentation': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO,
                category=RuleCategory.CODE_QUALITY,
                weight=SeverityWeight.LOW
            ),
            
            # Règles PSR - Poids VERY_LOW
            'best_practices.psr_compliance': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO,
                category=RuleCategory.PSR,
                weight=SeverityWeight.VERY_LOW
            ),
            'best_practices.line_length': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO,
                category=RuleCategory.PSR,
                weight=SeverityWeight.VERY_LOW
            ),
            'best_practices.naming': RuleConfig(
                enabled=True,
                severity=SeverityLevel.INFO,
                category=RuleCategory.PSR,
                weight=SeverityWeight.VERY_LOW
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

    def supports_union_types(self) -> bool:
        """Vérifier si la version PHP supporte les types union (PHP 8.0+)"""
        return self._version_compare(self.php_version, "8.0") >= 0
    
    def supports_nullable_types(self) -> bool:
        """Vérifier si la version PHP supporte les types nullable (PHP 7.1+)"""
        return self._version_compare(self.php_version, "7.1") >= 0
    
    def supports_mixed_type(self) -> bool:
        """Vérifier si la version PHP supporte le type mixed (PHP 8.0+)"""
        return self._version_compare(self.php_version, "8.0") >= 0
    
    def supports_never_type(self) -> bool:
        """Vérifier si la version PHP supporte le type never (PHP 8.1+)"""
        return self._version_compare(self.php_version, "8.1") >= 0
    
    def _version_compare(self, version1: str, version2: str) -> int:
        """
        Comparer deux versions PHP
        Retourne: -1 si version1 < version2, 0 si égales, 1 si version1 > version2
        """
        def version_to_tuple(v: str) -> tuple:
            return tuple(map(int, v.split('.')))
        
        v1_tuple = version_to_tuple(version1)
        v2_tuple = version_to_tuple(version2)
        
        if v1_tuple < v2_tuple:
            return -1
        elif v1_tuple > v2_tuple:
            return 1
        else:
            return 0

    def set_category_filters(self, included_categories: List[str] = None, excluded_categories: List[str] = None):
        """Définir les filtres par catégorie"""
        if included_categories:
            self.included_categories = [RuleCategory(cat) for cat in included_categories]
        if excluded_categories:
            self.excluded_categories = [RuleCategory(cat) for cat in excluded_categories]

    def set_min_severity_weight(self, weight: str):
        """Définir le poids minimum de sévérité"""
        self.min_severity_weight = SeverityWeight(int(weight))

    def should_apply_rule(self, rule_name: str) -> bool:
        """
        Vérifier si une règle doit être appliquée selon les filtres de catégorie et poids
        """
        if rule_name not in self.rules:
            return False
            
        rule_config = self.rules[rule_name]
        
        # Vérifier si la règle est activée
        if not rule_config.enabled:
            return False
            
        # Vérifier les catégories incluses
        if self.included_categories and rule_config.category not in self.included_categories:
            return False
            
        # Vérifier les catégories exclues
        if self.excluded_categories and rule_config.category in self.excluded_categories:
            return False
            
        # Vérifier le poids minimum
        if rule_config.weight.value < self.min_severity_weight.value:
            return False
            
        return True

    def get_rules_by_category(self, category: RuleCategory) -> Dict[str, RuleConfig]:
        """Obtenir toutes les règles d'une catégorie"""
        return {
            name: config for name, config in self.rules.items()
            if config.category == category
        }

    def get_rules_by_weight(self, min_weight: SeverityWeight) -> Dict[str, RuleConfig]:
        """Obtenir toutes les règles ayant au moins un certain poids"""
        return {
            name: config for name, config in self.rules.items()
            if config.weight.value >= min_weight.value
        }
