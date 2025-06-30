#!/usr/bin/env python3
"""
Script de nettoyage pour PHP Optimizer
Supprime les fichiers temporaires et les caches
"""

import os
import shutil
import glob
from pathlib import Path


def clean_project():
    """Nettoie le projet en supprimant les fichiers temporaires"""
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🧹 Nettoyage du projet PHP Optimizer...")
    
    # Fichiers à supprimer (patterns)
    patterns_to_remove = [
        # Rapports HTML temporaires
        "rapport*.html",
        "report*.html", 
        "test_*.html",
        "analysis*.json",
        
        # Fichiers PHP de test temporaires
        "test_*.php",
        "*_test.php", 
        "*_debug.php",
        
        # Rapports de développement
        "REFACTOR_REPORT.md",
        "RAPPORT_FINAL.md", 
        "COMPLETION_REPORT.md",
        "*_REPORT.md",
        
        # Fichiers temporaires Python
        "debug_*.py",
        "temp_*.py",
        "*.py.tmp"
    ]
    
    # Dossiers à supprimer
    folders_to_remove = [
        "__pycache__",
        "*.egg-info", 
        ".pytest_cache",
        ".tox",
        ".mypy_cache",
        "htmlcov"
    ]
    
    files_removed = 0
    folders_removed = 0
    
    # Supprimer les fichiers selon les patterns
    for pattern in patterns_to_remove:
        files = glob.glob(pattern, recursive=False)
        for file_path in files:
            try:
                os.remove(file_path)
                print(f"  ✓ Supprimé: {file_path}")
                files_removed += 1
            except OSError as e:
                print(f"  ❌ Erreur lors de la suppression de {file_path}: {e}")
    
    # Supprimer les dossiers de cache récursivement
    for root, dirs, files in os.walk(".", topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            
            # Vérifier si le dossier correspond aux patterns à supprimer
            for pattern in folders_to_remove:
                if pattern.replace("*", "") in dir_name or dir_name == pattern:
                    try:
                        shutil.rmtree(dir_path)
                        print(f"  ✓ Dossier supprimé: {dir_path}")
                        folders_removed += 1
                    except OSError as e:
                        print(f"  ❌ Erreur lors de la suppression du dossier {dir_path}: {e}")
                    break
    
    # Nettoyer les dossiers vides dans examples/
    examples_dir = Path("examples")
    if examples_dir.exists():
        for item in examples_dir.iterdir():
            if item.is_dir() and not any(item.iterdir()):
                try:
                    item.rmdir()
                    print(f"  ✓ Dossier vide supprimé: {item}")
                    folders_removed += 1
                except OSError:
                    pass
    
    print(f"\n✅ Nettoyage terminé:")
    print(f"   📄 {files_removed} fichier(s) supprimé(s)")
    print(f"   📁 {folders_removed} dossier(s) supprimé(s)")
    
    if files_removed == 0 and folders_removed == 0:
        print("   🎉 Projet déjà propre !")


def list_temp_files():
    """Liste les fichiers temporaires sans les supprimer"""
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    patterns_to_check = [
        "rapport*.html", "report*.html", "test_*.html", "analysis*.json",
        "test_*.php", "*_test.php", "*_debug.php",
        "REFACTOR_REPORT.md", "RAPPORT_FINAL.md", "COMPLETION_REPORT.md",
        "debug_*.py", "temp_*.py", "*.py.tmp"
    ]
    
    temp_files = []
    for pattern in patterns_to_check:
        temp_files.extend(glob.glob(pattern, recursive=False))
    
    # Trouver les dossiers de cache
    cache_folders = []
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if any(cache_name in dir_name for cache_name in ["__pycache__", ".pytest_cache", ".egg-info"]):
                cache_folders.append(os.path.join(root, dir_name))
    
    if temp_files or cache_folders:
        print("🔍 Fichiers temporaires détectés:")
        for file in temp_files:
            print(f"  📄 {file}")
        for folder in cache_folders:
            print(f"  📁 {folder}")
        print(f"\nTotal: {len(temp_files)} fichier(s), {len(cache_folders)} dossier(s)")
    else:
        print("✅ Aucun fichier temporaire détecté")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] in ["--list", "-l"]:
        list_temp_files()
    elif len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("Script de nettoyage PHP Optimizer")
        print("\nUsage:")
        print("  python clean.py          # Nettoie le projet")
        print("  python clean.py --list   # Liste les fichiers temporaires")
        print("  python clean.py --help   # Affiche cette aide")
    else:
        clean_project()
