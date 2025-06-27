"""
Analyseur principal pour détecter les optimisations PHP
"""

from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import time

from .parser import PHPParser
from .config import Config, SeverityLevel
from .rules import RuleManager


class IssueType(Enum):
    PERFORMANCE = "performance"
    SECURITY = "security"
    BEST_PRACTICES = "best_practices"
    MAINTAINABILITY = "maintainability"


@dataclass
class Issue:
    """Représente un problème détecté dans le code"""
    rule_name: str
    message: str
    file_path: str
    line: int
    column: int
    severity: SeverityLevel
    issue_type: IssueType
    suggestion: str
    code_snippet: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            'rule_name': self.rule_name,
            'message': self.message,
            'file_path': self.file_path,
            'line': self.line,
            'column': self.column,
            'severity': self.severity.value,
            'issue_type': self.issue_type.value,
            'suggestion': self.suggestion,
            'code_snippet': self.code_snippet
        }


@dataclass
class AnalysisResult:
    """Résultat de l'analyse d'un fichier"""
    file_path: str
    issues: List[Issue]
    metrics: Dict[str, Any]
    analysis_time: float
    success: bool
    error_message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            'file_path': self.file_path,
            'issues': [issue.to_dict() for issue in self.issues],
            'metrics': self.metrics,
            'analysis_time': self.analysis_time,
            'success': self.success,
            'error_message': self.error_message
        }


class PHPAnalyzer:
    """Analyseur principal pour le code PHP"""
    
    def __init__(self, config: Config):
        self.config = config
        self.parser = PHPParser()
        self.rule_manager = RuleManager(config)
    
    def analyze_file(self, file_path: Path) -> AnalysisResult:
        """
        Analyser un fichier PHP
        
        Args:
            file_path: Chemin vers le fichier à analyser
            
        Returns:
            Résultat de l'analyse
        """
        start_time = time.time()
        
        try:
            # Vérifier si le fichier doit être traité
            if not self.config.should_process_file(file_path):
                return AnalysisResult(
                    file_path=str(file_path),
                    issues=[],
                    metrics={},
                    analysis_time=0,
                    success=False,
                    error_message="Fichier ignoré par la configuration"
                )
            
            # Parser le fichier
            parse_result = self.parser.parse_file(file_path)
            
            # Analyser avec les règles
            issues = self.rule_manager.analyze(parse_result)
            
            # Filtrer par niveau de sévérité
            filtered_issues = [
                issue for issue in issues
                if self._should_include_issue(issue)
            ]
            
            analysis_time = time.time() - start_time
            
            return AnalysisResult(
                file_path=str(file_path),
                issues=filtered_issues,
                metrics=parse_result['metadata'],
                analysis_time=analysis_time,
                success=True
            )
            
        except Exception as e:
            analysis_time = time.time() - start_time
            return AnalysisResult(
                file_path=str(file_path),
                issues=[],
                metrics={},
                analysis_time=analysis_time,
                success=False,
                error_message=str(e)
            )
    
    def analyze_directory(self, directory_path: Path, recursive: bool = True) -> List[AnalysisResult]:
        """
        Analyser tous les fichiers PHP d'un répertoire
        
        Args:
            directory_path: Chemin vers le répertoire
            recursive: Analyser récursivement les sous-répertoires
            
        Returns:
            Liste des résultats d'analyse
        """
        results = []
        
        # Collecter les fichiers PHP
        pattern = "**/*.php" if recursive else "*.php"
        php_files = list(directory_path.glob(pattern))
        
        # Analyser chaque fichier
        for file_path in php_files:
            result = self.analyze_file(file_path)
            results.append(result)
        
        return results
    
    def _should_include_issue(self, issue: Issue) -> bool:
        """Vérifier si un problème doit être inclus selon la configuration"""
        severity_levels = {
            SeverityLevel.INFO: 0,
            SeverityLevel.WARNING: 1,
            SeverityLevel.ERROR: 2
        }
        
        min_level = severity_levels.get(self.config.severity_level, 0)
        issue_level = severity_levels.get(issue.severity, 0)
        
        return issue_level >= min_level
    
    def get_summary_statistics(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """
        Générer des statistiques résumées pour plusieurs résultats d'analyse
        
        Args:
            results: Liste des résultats d'analyse
            
        Returns:
            Dictionnaire avec les statistiques
        """
        total_files = len(results)
        successful_analyses = sum(1 for r in results if r.success)
        total_issues = sum(len(r.issues) for r in results)
        total_time = sum(r.analysis_time for r in results)
        
        # Compter par type de problème
        issue_type_counts = {}
        severity_counts = {}
        
        for result in results:
            for issue in result.issues:
                # Compter par type
                issue_type = issue.issue_type.value
                issue_type_counts[issue_type] = issue_type_counts.get(issue_type, 0) + 1
                
                # Compter par sévérité
                severity = issue.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Fichiers les plus problématiques
        files_by_issues = sorted(
            [(r.file_path, len(r.issues)) for r in results if r.success],
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'total_files': total_files,
            'successful_analyses': successful_analyses,
            'failed_analyses': total_files - successful_analyses,
            'total_issues': total_issues,
            'total_analysis_time': total_time,
            'average_issues_per_file': total_issues / max(successful_analyses, 1),
            'issue_type_counts': issue_type_counts,
            'severity_counts': severity_counts,
            'most_problematic_files': files_by_issues[:10]  # Top 10
        }
