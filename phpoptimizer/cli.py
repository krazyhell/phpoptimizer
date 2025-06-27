#!/usr/bin/env python3
"""
Interface en ligne de commande pour PHP Optimizer
"""

import click
import sys
from pathlib import Path
from typing import List, Optional
from colorama import init, Fore, Style

from .simple_analyzer import SimpleAnalyzer
from .reporter import ReportGenerator, OutputFormat
from .config import Config

# Initialiser colorama pour Windows
init(autoreset=True)


@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--recursive', '-r', is_flag=True, 
              help='Analyser récursivement les sous-dossiers')
@click.option('--output-format', default='console', 
              type=click.Choice(['console', 'json', 'html']),
              help='Format de sortie du rapport')
@click.option('--output', '-o', type=click.Path(),
              help='Fichier de sortie (optionnel)')
@click.option('--rules', type=click.Path(exists=True),
              help='Fichier de configuration des règles personnalisées')
@click.option('--severity', default='info',
              type=click.Choice(['info', 'warning', 'error']),
              help='Niveau de sévérité minimum')
@click.option('--verbose', '-v', is_flag=True,
              help='Mode verbose')
def analyze(path: str, recursive: bool, output_format: str, output: Optional[str],
           rules: Optional[str], severity: str, verbose: bool):
    """
    Analyser un fichier ou dossier PHP pour détecter les optimisations possibles.
    
    PATH: Chemin vers le fichier ou dossier à analyser
    """
    
    if verbose:
        click.echo(f"{Fore.BLUE}🔍 PHP Optimizer v0.1.0{Style.RESET_ALL}")
        click.echo(f"📁 Analyse de: {path}")
    
    try:
        # Configuration
        config = Config()
        if rules:
            config.load_rules_file(rules)
        config.set_severity_level(severity)
        
        # Collecte des fichiers PHP
        php_files = collect_php_files(Path(path), recursive)
        
        if not php_files:
            click.echo(f"{Fore.YELLOW}⚠️  Aucun fichier PHP trouvé{Style.RESET_ALL}")
            return
        
        if verbose:
            click.echo(f"📋 {len(php_files)} fichier(s) PHP trouvé(s)")
        
        # Analyse
        analyzer = SimpleAnalyzer(config)
        results = []
        
        with click.progressbar(php_files, label='Analyse en cours') as files:
            for file_path in files:
                try:
                    result = analyzer.analyze_file(file_path)
                    results.append(result)
                except Exception as e:
                    if verbose:
                        click.echo(f"\n{Fore.RED}❌ Erreur lors de l'analyse de {file_path}: {e}{Style.RESET_ALL}")
        
        # Génération du rapport
        reporter = ReportGenerator()
        output_format_enum = OutputFormat.from_string(output_format)
        
        if output:
            reporter.generate_file_report(results, output, output_format_enum)
            click.echo(f"{Fore.GREEN}✅ Rapport généré: {output}{Style.RESET_ALL}")
        else:
            reporter.generate_console_report(results, verbose)
            
    except Exception as e:
        click.echo(f"{Fore.RED}❌ Erreur: {e}{Style.RESET_ALL}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def collect_php_files(path: Path, recursive: bool) -> List[Path]:
    """Collecte tous les fichiers PHP dans le chemin donné."""
    php_files = []
    
    if path.is_file():
        if path.suffix.lower() == '.php':
            php_files.append(path)
    elif path.is_dir():
        pattern = "**/*.php" if recursive else "*.php"
        php_files.extend(path.glob(pattern))
    
    return sorted(php_files)


@click.group()
def main():
    """PHP Code Optimizer - Analyseur et optimiseur de code PHP"""
    pass


@main.command()
def version():
    """Afficher la version du programme"""
    click.echo("PHP Optimizer v0.1.0")


@main.command()
@click.argument('output_path', type=click.Path())
def init_config(output_path: str):
    """Générer un fichier de configuration par défaut"""
    config = Config()
    config.save_default_config(Path(output_path))
    click.echo(f"{Fore.GREEN}✅ Configuration par défaut générée: {output_path}{Style.RESET_ALL}")


# Ajouter la commande analyze au groupe principal
main.add_command(analyze)


if __name__ == '__main__':
    main()
