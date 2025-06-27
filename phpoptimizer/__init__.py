"""
PHP Code Optimizer
Un outil d'analyse et d'optimisation de code PHP
"""

__version__ = "0.1.0"
__author__ = "PHP Optimizer Team"
__email__ = "contact@phpoptimizer.dev"

from .simple_analyzer import SimpleAnalyzer
from .parser import PHPParser
from .reporter import ReportGenerator

__all__ = ['SimpleAnalyzer', 'PHPParser', 'ReportGenerator']
