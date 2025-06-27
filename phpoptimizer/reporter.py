"""
Générateur de rapports pour PHP Optimizer
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from enum import Enum
from datetime import datetime
from colorama import Fore, Style, Back

from .analyzer import AnalysisResult, Issue


class OutputFormat(Enum):
    CONSOLE = "console"
    JSON = "json"
    HTML = "html"
    
    @classmethod
    def from_string(cls, value: str):
        """Créer enum depuis string"""
        for format_type in cls:
            if format_type.value == value:
                return format_type
        raise ValueError(f"Format non supporté: {value}")


class ReportGenerator:
    """Générateur de rapports d'analyse"""
    
    def generate_console_report(self, results: List[Dict[str, Any]], verbose: bool = False):
        """Générer un rapport console coloré"""
        if not results:
            print(f"{Fore.YELLOW}Aucun résultat à afficher{Style.RESET_ALL}")
            return
        
        # Statistiques générales
        total_files = len(results)
        successful_files = sum(1 for r in results if r.get('success', False))
        total_issues = sum(len(r.get('issues', [])) for r in results)
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  RAPPORT D'ANALYSE PHP OPTIMIZER{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        print(f"\n📊 {Fore.BLUE}Statistiques générales:{Style.RESET_ALL}")
        print(f"   Fichiers analysés: {successful_files}/{total_files}")
        print(f"   Problèmes détectés: {total_issues}")
        
        if total_issues == 0:
            print(f"\n{Fore.GREEN}✅ Aucun problème détecté ! Excellent travail !{Style.RESET_ALL}")
            return
        
        # Résumé par sévérité
        severity_counts = {'error': 0, 'warning': 0, 'info': 0}
        for result in results:
            for issue in result.get('issues', []):
                severity = issue.get('severity', 'info')
                if severity in severity_counts:
                    severity_counts[severity] += 1
        
        print(f"\n🎯 {Fore.BLUE}Répartition par sévérité:{Style.RESET_ALL}")
        if severity_counts['error'] > 0:
            print(f"   {Fore.RED}❌ Erreurs: {severity_counts['error']}{Style.RESET_ALL}")
        if severity_counts['warning'] > 0:
            print(f"   {Fore.YELLOW}⚠️  Avertissements: {severity_counts['warning']}{Style.RESET_ALL}")
        if severity_counts['info'] > 0:
            print(f"   {Fore.BLUE}ℹ️  Informations: {severity_counts['info']}{Style.RESET_ALL}")
        
        # Détails par fichier
        print(f"\n📁 {Fore.BLUE}Détails par fichier:{Style.RESET_ALL}")
        
        for result in results:
            if not result.get('success', False):
                print(f"\n{Fore.RED}❌ {result.get('file_path', 'Unknown')}{Style.RESET_ALL}")
                print(f"   Erreur: {result.get('error_message', 'Erreur inconnue')}")
                continue
            
            issues = result.get('issues', [])
            if not issues:
                if verbose:
                    print(f"\n{Fore.GREEN}✅ {result.get('file_path', 'Unknown')}{Style.RESET_ALL}")
                    print(f"   Aucun problème détecté")
                continue
            
            print(f"\n{Fore.YELLOW}📄 {result.get('file_path', 'Unknown')}{Style.RESET_ALL}")
            print(f"   {len(issues)} problème(s) détecté(s)")
            
            if verbose:
                # Grouper par ligne pour un affichage plus lisible
                issues_by_line = {}
                for issue in issues:
                    line = issue.get('line', 0)
                    if line not in issues_by_line:
                        issues_by_line[line] = []
                    issues_by_line[line].append(issue)
                
                for line_num in sorted(issues_by_line.keys()):
                    line_issues = issues_by_line[line_num]
                    print(f"\n   📍 {Fore.CYAN}Ligne {line_num}:{Style.RESET_ALL}")
                    
                    for issue in line_issues:
                        severity = issue.get('severity', 'info')
                        severity_color = self._get_severity_color(severity)
                        severity_icon = self._get_severity_icon(severity)
                        
                        print(f"      {severity_color}{severity_icon} {issue.get('message', '')}{Style.RESET_ALL}")
                        print(f"        💡 {issue.get('suggestion', '')}")
                        
                        code_snippet = issue.get('code_snippet', '')
                        if code_snippet:
                            print(f"        📝 {Fore.LIGHTBLACK_EX}{code_snippet}{Style.RESET_ALL}")
        
        # Top des règles les plus déclenchées
        rule_counts = {}
        for result in results:
            for issue in result.get('issues', []):
                rule_name = issue.get('rule_name', 'unknown')
                rule_counts[rule_name] = rule_counts.get(rule_name, 0) + 1
        
        if rule_counts:
            print(f"\n🏆 {Fore.BLUE}Top des problèmes les plus fréquents:{Style.RESET_ALL}")
            sorted_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)
            
            for i, (rule_name, count) in enumerate(sorted_rules[:5], 1):
                print(f"   {i}. {rule_name}: {count} occurrence(s)")
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    def generate_file_report(self, results: List[Dict[str, Any]], 
                           output_path: str, format_type: OutputFormat):
        """Générer un rapport dans un fichier"""
        output_file = Path(output_path)
        
        if format_type == OutputFormat.JSON:
            self._generate_json_report(results, output_file)
        elif format_type == OutputFormat.HTML:
            self._generate_html_report(results, output_file)
        else:
            raise ValueError(f"Format de fichier non supporté: {format_type}")
    
    def _generate_json_report(self, results: List[Dict[str, Any]], output_file: Path):
        """Générer un rapport JSON"""
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_files': len(results),
                'successful_analyses': sum(1 for r in results if r.get('success', False)),
                'total_issues': sum(len(r.get('issues', [])) for r in results),
                'total_analysis_time': sum(r.get('analysis_time', 0) for r in results)
            },
            'results': results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    def _generate_html_report(self, results: List[Dict[str, Any]], output_file: Path):
        """Générer un rapport HTML"""
        # Calculer les statistiques
        total_files = len(results)
        successful_files = sum(1 for r in results if r.get('success', False))
        total_issues = sum(len(r.get('issues', [])) for r in results)
        
        severity_counts = {'error': 0, 'warning': 0, 'info': 0}
        rule_counts = {}
        
        for result in results:
            for issue in result.get('issues', []):
                severity = issue.get('severity', 'info')
                if severity in severity_counts:
                    severity_counts[severity] += 1
                rule_name = issue.get('rule_name', 'unknown')
                rule_counts[rule_name] = rule_counts.get(rule_name, 0) + 1
        
        # Générer le HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport PHP Optimizer</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 30px; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #333; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .severity-error {{ color: #dc3545; }}
        .severity-warning {{ color: #ffc107; }}
        .severity-info {{ color: #17a2b8; }}
        .content {{ padding: 0 30px 30px 30px; }}
        .file-result {{ margin-bottom: 30px; border: 1px solid #e9ecef; border-radius: 8px; overflow: hidden; }}
        .file-header {{ background: #f8f9fa; padding: 15px 20px; border-bottom: 1px solid #e9ecef; }}
        .file-path {{ font-weight: bold; color: #333; }}
        .issue-count {{ color: #666; font-size: 0.9em; }}
        .issues {{ padding: 20px; }}
        .issue {{ margin-bottom: 20px; padding: 15px; border-left: 4px solid #ddd; background: #f8f9fa; }}
        .issue.error {{ border-left-color: #dc3545; }}
        .issue.warning {{ border-left-color: #ffc107; }}
        .issue.info {{ border-left-color: #17a2b8; }}
        .issue-header {{ display: flex; justify-content: between; align-items: center; margin-bottom: 10px; }}
        .issue-message {{ font-weight: bold; color: #333; }}
        .issue-line {{ color: #666; font-size: 0.9em; }}
        .issue-suggestion {{ color: #666; font-style: italic; margin-bottom: 10px; }}
        .code-snippet {{ background: #2d3748; color: #e2e8f0; padding: 10px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 0.9em; overflow-x: auto; }}
        .no-issues {{ text-align: center; padding: 40px; color: #28a745; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Rapport PHP Optimizer</h1>
            <p>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{successful_files}/{total_files}</div>
                <div class="stat-label">Fichiers analysés</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_issues}</div>
                <div class="stat-label">Problèmes détectés</div>
            </div>
            <div class="stat-card">
                <div class="stat-number severity-error">{severity_counts['error']}</div>
                <div class="stat-label">Erreurs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number severity-warning">{severity_counts['warning']}</div>
                <div class="stat-label">Avertissements</div>
            </div>
            <div class="stat-card">
                <div class="stat-number severity-info">{severity_counts['info']}</div>
                <div class="stat-label">Informations</div>
            </div>
        </div>
        
        <div class="content">
"""
        
        if total_issues == 0:
            html_content += """
            <div class="no-issues">
                <h2>🎉 Aucun problème détecté !</h2>
                <p>Votre code respecte toutes les règles d'optimisation configurées.</p>
            </div>
"""
        else:
            for result in results:
                if not result.get('success', False):
                    html_content += f"""
            <div class="file-result">
                <div class="file-header">
                    <div class="file-path">❌ {result.get('file_path', 'Unknown')}</div>
                    <div class="issue-count">Erreur d'analyse: {result.get('error_message', 'Erreur inconnue')}</div>
                </div>
            </div>
"""
                    continue
                
                issues = result.get('issues', [])
                if not issues:
                    continue
                
                html_content += f"""
            <div class="file-result">
                <div class="file-header">
                    <div class="file-path">📄 {result.get('file_path', 'Unknown')}</div>
                    <div class="issue-count">{len(issues)} problème(s) détecté(s)</div>
                </div>
                <div class="issues">
"""
                
                for issue in issues:
                    severity = issue.get('severity', 'info')
                    html_content += f"""
                    <div class="issue {severity}">
                        <div class="issue-header">
                            <div class="issue-message">{issue.get('message', '')}</div>
                            <div class="issue-line">Ligne {issue.get('line', 0)}</div>
                        </div>
                        <div class="issue-suggestion">💡 {issue.get('suggestion', '')}</div>
"""
                    
                    code_snippet = issue.get('code_snippet', '')
                    if code_snippet:
                        html_content += f"""
                        <div class="code-snippet">{code_snippet}</div>
"""
                    
                    html_content += "                    </div>\n"
                
                html_content += """
                </div>
            </div>
"""
        
        html_content += """
        </div>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _get_severity_color(self, severity: str) -> str:
        """Obtenir la couleur pour une sévérité"""
        colors = {
            'error': Fore.RED,
            'warning': Fore.YELLOW,
            'info': Fore.BLUE
        }
        return colors.get(severity, Fore.WHITE)
    
    def _get_severity_icon(self, severity: str) -> str:
        """Obtenir l'icône pour une sévérité"""
        icons = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        return icons.get(severity, '•')
