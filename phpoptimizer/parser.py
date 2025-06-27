"""
Parseur PHP utilisant phply pour l'analyse syntaxique
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import phply
from phply import phplex
from phply.phpparse import make_parser
from phply.phpast import *


class PHPParser:
    """Parseur pour les fichiers PHP"""
    
    def __init__(self):
        self.lexer = phplex.lexer.clone()
        self.parser = make_parser()
    
    def parse_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parser un fichier PHP et retourner l'AST
        
        Args:
            file_path: Chemin vers le fichier PHP
            
        Returns:
            Dictionnaire contenant l'AST et les métadonnées
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.parse_content(content, str(file_path))
            
        except Exception as e:
            raise ValueError(f"Erreur lors du parsing de {file_path}: {e}")
    
    def parse_content(self, content: str, filename: str = "<string>") -> Dict[str, Any]:
        """
        Parser le contenu PHP
        
        Args:
            content: Contenu PHP à parser
            filename: Nom du fichier (pour les erreurs)
            
        Returns:
            Dictionnaire contenant l'AST et les métadonnées
        """
        try:
            # Parser le contenu
            ast = self.parser.parse(content, lexer=self.lexer)
            
            # Extraire les métadonnées
            metadata = self._extract_metadata(content, ast)
            
            return {
                'ast': ast,
                'content': content,
                'filename': filename,
                'metadata': metadata
            }
            
        except Exception as e:
            raise ValueError(f"Erreur lors du parsing de {filename}: {e}")
    
    def _extract_metadata(self, content: str, ast: Any) -> Dict[str, Any]:
        """Extraire les métadonnées du code PHP"""
        lines = content.split('\n')
        
        metadata = {
            'line_count': len(lines),
            'file_size': len(content),
            'functions': [],
            'classes': [],
            'variables': [],
            'includes': [],
            'complexity_metrics': {
                'cyclomatic_complexity': 0,
                'nesting_depth': 0
            }
        }
        
        # Analyser l'AST pour extraire les informations
        if ast:
            self._analyze_ast_node(ast, metadata)
        
        return metadata
    
    def _analyze_ast_node(self, node: Any, metadata: Dict[str, Any], depth: int = 0):
        """Analyser récursivement les nœuds de l'AST"""
        if not hasattr(node, '__class__'):
            return
        
        node_type = node.__class__.__name__
        
        # Mettre à jour la profondeur maximale
        metadata['complexity_metrics']['nesting_depth'] = max(
            metadata['complexity_metrics']['nesting_depth'], depth
        )
        
        # Analyser selon le type de nœud
        if node_type == 'Function':
            self._analyze_function(node, metadata)
        elif node_type == 'Class':
            self._analyze_class(node, metadata)
        elif node_type == 'Assignment':
            self._analyze_assignment(node, metadata)
        elif node_type == 'Include':
            self._analyze_include(node, metadata)
        elif node_type in ['If', 'While', 'For', 'Foreach']:
            metadata['complexity_metrics']['cyclomatic_complexity'] += 1
        
        # Analyser récursivement les enfants
        if hasattr(node, 'nodes') and node.nodes:
            for child in node.nodes:
                self._analyze_ast_node(child, metadata, depth + 1)
        
        # Analyser d'autres attributs qui peuvent contenir des nœuds
        for attr_name in dir(node):
            if not attr_name.startswith('_'):
                attr_value = getattr(node, attr_name)
                if hasattr(attr_value, '__class__') and hasattr(attr_value, 'nodes'):
                    self._analyze_ast_node(attr_value, metadata, depth + 1)
                elif isinstance(attr_value, list):
                    for item in attr_value:
                        if hasattr(item, '__class__') and hasattr(item, 'nodes'):
                            self._analyze_ast_node(item, metadata, depth + 1)
    
    def _analyze_function(self, node: Any, metadata: Dict[str, Any]):
        """Analyser une fonction"""
        function_info = {
            'name': getattr(node, 'name', 'anonymous'),
            'line': getattr(node, 'lineno', 0),
            'params': [],
            'complexity': 1  # Complexité de base
        }
        
        # Analyser les paramètres
        if hasattr(node, 'params') and node.params:
            for param in node.params:
                param_info = {
                    'name': getattr(param, 'name', ''),
                    'default': getattr(param, 'default', None),
                    'type': getattr(param, 'type', None)
                }
                function_info['params'].append(param_info)
        
        metadata['functions'].append(function_info)
    
    def _analyze_class(self, node: Any, metadata: Dict[str, Any]):
        """Analyser une classe"""
        class_info = {
            'name': getattr(node, 'name', 'anonymous'),
            'line': getattr(node, 'lineno', 0),
            'extends': getattr(node, 'extends', None),
            'implements': getattr(node, 'implements', []),
            'methods': [],
            'properties': []
        }
        
        metadata['classes'].append(class_info)
    
    def _analyze_assignment(self, node: Any, metadata: Dict[str, Any]):
        """Analyser une assignation de variable"""
        if hasattr(node, 'node') and hasattr(node.node, 'name'):
            var_name = node.node.name
            if var_name not in [v['name'] for v in metadata['variables']]:
                metadata['variables'].append({
                    'name': var_name,
                    'line': getattr(node, 'lineno', 0),
                    'type': 'unknown'
                })
    
    def _analyze_include(self, node: Any, metadata: Dict[str, Any]):
        """Analyser une instruction include/require"""
        if hasattr(node, 'expr'):
            metadata['includes'].append({
                'type': getattr(node, 'type', 'include'),
                'file': str(node.expr),
                'line': getattr(node, 'lineno', 0)
            })


class ASTVisitor:
    """Visiteur pour parcourir l'AST de manière structurée"""
    
    def visit(self, node: Any) -> Any:
        """Visiter un nœud et dispatcher vers la méthode appropriée"""
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: Any) -> Any:
        """Visite générique pour les nœuds non spécifiques"""
        if hasattr(node, 'nodes') and node.nodes:
            for child in node.nodes:
                self.visit(child)
        return node
