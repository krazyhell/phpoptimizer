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
@click.option('--exclude-rules', default='', help='Liste de règles à exclure (séparées par des virgules)')
@click.option('--include-rules', default='', help='Liste de règles à inclure uniquement (séparées par des virgules)')
@click.option('--include-categories', default='', help='Catégories à inclure (security,error,performance.critical,performance.general,memory,code_quality,psr)')
@click.option('--exclude-categories', default='', help='Catégories à exclure')
@click.option('--min-weight', type=click.Choice(['0', '1', '2', '3', '4']), help='Poids minimum (0=très faible, 1=faible, 2=moyen, 3=élevé, 4=critique)')
@click.option('--php-version', default='8.0', help='Version PHP cible (ex: 7.0, 7.1, 7.4, 8.0, 8.1, 8.2)')
@click.option('--verbose', '-v', is_flag=True,
              help='Mode verbose')
def analyze(path: str, recursive: bool, output_format: str, output: Optional[str],
           rules: Optional[str], severity: str, exclude_rules: str, include_rules: str, 
           include_categories: str, exclude_categories: str, min_weight: Optional[str],
           php_version: str, verbose: bool):
    """
    Analyse un fichier ou dossier PHP et permet de filtrer les types d'erreurs détectées.

    PATH: Chemin vers le fichier ou dossier à analyser

    Options de filtrage par règles individuelles :
      --exclude-rules : Exclut certaines règles du rapport
      --include-rules : N'inclut que les règles spécifiées
      
    Options de filtrage par catégorie :
      --include-categories : N'inclut que les catégories spécifiées (security,error,performance.critical,etc.)
      --exclude-categories : Exclut les catégories spécifiées
      --min-weight : Poids minimum (0=très faible à 4=critique)

    Exemples :
      N'afficher que les problèmes de sécurité et erreurs :
        python -m phpoptimizer analyze monfichier.php --include-categories=security,error
      Exclure les règles PSR :
        python -m phpoptimizer analyze monfichier.php --exclude-categories=psr
      Afficher seulement les problèmes importants :
        python -m phpoptimizer analyze monfichier.php --min-weight=2
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
        config.php_version = php_version  # Définir la version PHP cible

        # Préparer les filtres de règles individuelles
        exclude_rules_list = [r.strip() for r in exclude_rules.split(',') if r.strip()]
        include_rules_list = [r.strip() for r in include_rules.split(',') if r.strip()]
        
        # Préparer les filtres par catégorie
        include_categories_list = [c.strip() for c in include_categories.split(',') if c.strip()]
        exclude_categories_list = [c.strip() for c in exclude_categories.split(',') if c.strip()]
        
        # Appliquer les filtres par catégorie et poids
        if include_categories_list or exclude_categories_list:
            config.set_category_filters(include_categories_list, exclude_categories_list)
        
        if min_weight:
            config.set_min_severity_weight(min_weight)

        # Collecte des fichiers PHP
        php_files = collect_php_files(Path(path), recursive)

        if not php_files:
            click.echo(f"{Fore.YELLOW}⚠️  Aucun fichier PHP trouvé{Style.RESET_ALL}")
            return

        if verbose:
            click.echo(f"📋 {len(php_files)} fichier(s) PHP trouvé(s)")
            if include_categories_list:
                click.echo(f"🎯 Catégories incluses: {', '.join(include_categories_list)}")
            if exclude_categories_list:
                click.echo(f"🚫 Catégories exclues: {', '.join(exclude_categories_list)}")
            if min_weight:
                click.echo(f"⚖️  Poids minimum: {min_weight}")

        # Analyse
        analyzer = SimpleAnalyzer(config, exclude_rules=exclude_rules_list, include_rules=include_rules_list)
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
            click.echo(f"{Fore.GREEN}Rapport généré: {output}{Style.RESET_ALL}")
        else:
            try:
                reporter.generate_console_report(results, verbose=True)  # Activer les descriptions par défaut
            except UnicodeEncodeError:
                # Fallback sans emojis pour les terminaux qui ne supportent pas Unicode
                click.echo("Rapport généré (mode compatibilité)")
                for result in results:
                    if result.get('success', False):
                        issues = result.get('issues', [])
                        if issues:
                            click.echo(f"Fichier: {result.get('file_path', 'Unknown')}")
                            click.echo(f"Issues: {len(issues)}")
                            for issue in issues[:5]:  # Limiter à 5 issues pour la lisibilité
                                click.echo(f"  - {issue.get('rule_name', 'unknown')}: {issue.get('message', 'no message')}")

    except Exception as e:
        try:
            click.echo(f"{Fore.RED}Erreur: {e}{Style.RESET_ALL}")
        except UnicodeEncodeError:
            click.echo(f"Erreur: {e}")
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
