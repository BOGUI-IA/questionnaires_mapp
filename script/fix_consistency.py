"""
Script de correction de la cohérence entre sessions.json et les fiches

Ce script :
1. Vérifie la cohérence entre les références dans sessions.json et les fichiers de fiches
2. Corrige automatiquement les incohérences
3. Crée des sauvegardes avant toute modification
4. Génère un rapport détaillé des modifications
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fix_consistency.log')
    ]
)
logger = logging.getLogger(__name__)

class ConsistencyFixer:
    def __init__(self, data_dir: str = 'data'):
        """Initialise le correcteur de cohérence"""
        self.data_dir = Path(data_dir)
        self.sessions_file = self.data_dir / 'sessions.json'
        self.fiches_dir = self.data_dir / 'fiches'
        self.backup_dir = self.data_dir / 'backups_consistency'
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'fixed_files': [],
            'warnings': [],
            'errors': [],
            'summary': {}
        }
        
        # Créer le dossier de sauvegarde si nécessaire
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self) -> Path:
        """Crée une sauvegarde des fichiers avant modification"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f'backup_{timestamp}'
        
        try:
            # Copier tout le dossier data
            shutil.copytree(self.data_dir, backup_path, 
                          dirs_exist_ok=True,
                          ignore=shutil.ignore_patterns('backups_consistency*'))
            
            logger.info(f"Sauvegarde créée : {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la sauvegarde : {e}")
            raise
    
    def load_sessions(self) -> dict:
        """Charge le fichier sessions.json"""
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur lors du chargement de sessions.json : {e}")
            raise
    
    def get_fiche_files(self) -> List[Path]:
        """Récupère la liste des fichiers de fiches"""
        return list(self.fiches_dir.glob('*.json'))
    
    def check_consistency(self) -> dict:
        """
        Vérifie la cohérence entre sessions.json et les fiches
        
        Returns:
            dict: Rapport de cohérence
        """
        sessions_data = self.load_sessions()
        fiche_files = self.get_fiche_files()
        
        # Dictionnaire pour suivre les problèmes
        issues = {
            'missing_fiches': [],
            'wrong_session_refs': [],
            'invalid_ids': [],
            'valid_fiches': []
        }
        
        # Vérifier chaque session
        for session_id, session in sessions_data.get('sessions', {}).items():
            for fiche_id in session.get('fiches', []):
                fiche_path = self.fiches_dir / f"{fiche_id}.json"
                
                # Vérifier si le fichier existe
                if not fiche_path.exists():
                    issues['missing_fiches'].append({
                        'session': session_id,
                        'expected_fiche': fiche_id,
                        'message': f"Fiche {fiche_id} référencée dans {session_id} mais fichier manquant"
                    })
                    continue
                
                # Vérifier le contenu de la fiche
                try:
                    with open(fiche_path, 'r', encoding='utf-8') as f:
                        fiche_data = json.load(f)
                    
                    # Vérifier l'ID
                    if fiche_data.get('id') != fiche_id:
                        issues['invalid_ids'].append({
                            'fiche': fiche_id,
                            'current_id': fiche_data.get('id'),
                            'expected_id': fiche_id,
                            'path': str(fiche_path)
                        })
                    
                    # Vérifier la référence de session
                    fiche_session = fiche_data.get('session')
                    if fiche_session != session_id and str(fiche_session) not in session_id:
                        issues['wrong_session_refs'].append({
                            'fiche': fiche_id,
                            'current_session': fiche_session,
                            'expected_session': session_id,
                            'path': str(fiche_path)
                        })
                    
                    # Si tout est bon
                    if not any(fiche_id in issue.get('fiche', '') for issue in 
                             issues['invalid_ids'] + issues['wrong_session_refs']):
                        issues['valid_fiches'].append(fiche_id)
                        
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture de {fiche_path}: {e}")
        
        return issues
    
    def fix_consistency(self, dry_run: bool = False) -> dict:
        """
        Corrige les incohérences détectées
        
        Args:
            dry_run: Si True, n'effectue pas les modifications
            
        Returns:
            dict: Rapport des modifications
        """
        # Créer une sauvegarde avant toute modification
        if not dry_run:
            backup_path = self.create_backup()
            self.report['backup_path'] = str(backup_path)
        
        # Vérifier la cohérence
        issues = self.check_consistency()
        self.report['issues'] = issues
        
        # Corriger les incohérences
        fixed_count = 0
        
        # 1. Corriger les IDs de fiches
        for issue in issues.get('invalid_ids', []):
            fiche_id = issue['fiche']
            fiche_path = self.fiches_dir / f"{fiche_id}.json"
            
            try:
                with open(fiche_path, 'r', encoding='utf-8') as f:
                    fiche_data = json.load(f)
                
                # Sauvegarder l'ancienne valeur
                old_id = fiche_data.get('id')
                
                # Mettre à jour l'ID
                fiche_data['id'] = fiche_id
                
                if not dry_run:
                    # Sauvegarder les modifications
                    with open(fiche_path, 'w', encoding='utf-8') as f:
                        json.dump(fiche_data, f, indent=2, ensure_ascii=False)
                
                self.report['fixed_files'].append({
                    'file': str(fiche_path),
                    'field': 'id',
                    'old_value': old_id,
                    'new_value': fiche_id
                })
                fixed_count += 1
                
            except Exception as e:
                error_msg = f"Erreur lors de la correction de l'ID pour {fiche_id}: {e}"
                logger.error(error_msg)
                self.report['errors'].append(error_msg)
        
        # 2. Corriger les références de session
        for issue in issues.get('wrong_session_refs', []):
            fiche_id = issue['fiche']
            fiche_path = self.fiches_dir / f"{fiche_id}.json"
            expected_session = issue['expected_session']
            
            try:
                with open(fiche_path, 'r', encoding='utf-8') as f:
                    fiche_data = json.load(f)
                
                # Sauvegarder l'ancienne valeur
                old_session = fiche_data.get('session')
                
                # Mettre à jour la session
                fiche_data['session'] = expected_session
                
                if not dry_run:
                    # Sauvegarder les modifications
                    with open(fiche_path, 'w', encoding='utf-8') as f:
                        json.dump(fiche_data, f, indent=2, ensure_ascii=False)
                
                self.report['fixed_files'].append({
                    'file': str(fiche_path),
                    'field': 'session',
                    'old_value': old_session,
                    'new_value': expected_session
                })
                fixed_count += 1
                
            except Exception as e:
                error_msg = f"Erreur lors de la correction de la session pour {fiche_id}: {e}"
                logger.error(error_msg)
                self.report['errors'].append(error_msg)
        
        # Générer le rapport
        self.report['summary'] = {
            'total_issues': (
                len(issues.get('missing_fiches', [])) +
                len(issues.get('invalid_ids', [])) +
                len(issues.get('wrong_session_refs', []))
            ),
            'fixed_issues': fixed_count,
            'missing_fiches': len(issues.get('missing_fiches', [])),
            'invalid_ids': len(issues.get('invalid_ids', [])),
            'wrong_session_refs': len(issues.get('wrong_session_refs', [])),
            'valid_fiches': len(issues.get('valid_fiches', []))
        }
        
        return self.report
    
    def generate_report(self, report_path: str = None) -> str:
        """Génère un rapport des modifications"""
        if not report_path:
            report_path = self.data_dir / 'consistency_report.md'
        else:
            report_path = Path(report_path)
        
        # Créer le contenu du rapport
        lines = [
            "# Rapport de cohérence des fiches\n",
            f"**Date** : {self.report['timestamp']}\n",
            "## Résumé\n"
        ]
        
        # Résumé
        summary = self.report.get('summary', {})
        lines.extend([
            f"- **Total d'incohérences détectées** : {summary.get('total_issues', 0)}",
            f"- **Problèmes corrigés** : {summary.get('fixed_issues', 0)}",
            f"- **Fiches manquantes** : {summary.get('missing_fiches', 0)}",
            f"- **IDs invalides** : {summary.get('invalid_ids', 0)}",
            f"- **Références de session incorrectes** : {summary.get('wrong_session_refs', 0)}",
            f"- **Fiches valides** : {summary.get('valid_fiches', 0)}\n"
        ])
        
        # Détails des corrections
        if self.report.get('fixed_files'):
            lines.extend(["## Fichiers modifiés\n"])
            for fix in self.report['fixed_files']:
                lines.append(f"- **{Path(fix['file']).name}**")
                lines.append(f"  - Champ : `{fix['field']}`")
                lines.append(f"  - Ancienne valeur : `{fix['old_value']}`")
                lines.append(f"  - Nouvelle valeur : `{fix['new_value']}`\n")
        
        # Avertissements
        if self.report.get('warnings'):
            lines.extend(["## Avertissements\n"])
            for warning in self.report['warnings']:
                lines.append(f"- ⚠️ {warning}")
            lines.append("")
        
        # Erreurs
        if self.report.get('errors'):
            lines.extend(["## Erreurs\n"])
            for error in self.report['errors']:
                lines.append(f"- ❌ {error}")
            lines.append("")
        
        # Fiches manquantes
        issues = self.report.get('issues', {})
        if issues.get('missing_fiches'):
            lines.extend(["## Fiches manquantes\n"])
            for missing in issues['missing_fiches']:
                lines.append(f"- **Session** : {missing['session']}")
                lines.append(f"  - Fiche attendue : `{missing['expected_fiche']}.json`")
                lines.append(f"  - Message : {missing['message']}\n")
        
        # Écrire le rapport
        report_content = "\n".join(lines)
        
        if not report_path.parent.exists():
            report_path.parent.mkdir(parents=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(report_path)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Vérifie et corrige la cohérence entre sessions.json et les fiches")
    parser.add_argument('--data-dir', default='data', help="Dossier contenant les données (sessions.json et le dossier fiches)")
    parser.add_argument('--dry-run', action='store_true', help="Affiche les modifications sans les appliquer")
    parser.add_argument('--fix', action='store_true', help="Applique les corrections automatiquement")
    parser.add_argument('--report', help="Fichier de sortie pour le rapport (par défaut: data/consistency_report.md)")
    
    args = parser.parse_args()
    
    try:
        fixer = ConsistencyFixer(args.data_dir)
        
        if args.fix:
            print("🔍 Vérification et correction des incohérences...")
            report = fixer.fix_consistency(dry_run=args.dry_run)
            
            if args.dry_run:
                print("\n🔧 [MODE TEST] Les modifications suivantes seraient apportées :")
            else:
                print("\n✅ Corrections appliquées avec succès")
                
            # Générer le rapport
            report_path = fixer.generate_report(args.report)
            print(f"📊 Rapport généré : {report_path}")
            
            # Afficher un résumé
            summary = report.get('summary', {})
            print(f"\n📋 Résumé :")
            print(f"- Incohérences détectées : {summary.get('total_issues', 0)}")
            print(f"- Problèmes corrigés : {summary.get('fixed_issues', 0)}")
            print(f"- Fiches manquantes : {summary.get('missing_fiches', 0)}")
            print(f"- IDs invalides : {summary.get('invalid_ids', 0)}")
            print(f"- Références de session incorrectes : {summary.get('wrong_session_refs', 0)}")
            print(f"- Fiches valides : {summary.get('valid_fiches', 0)}")
            
            if summary.get('missing_fiches', 0) > 0:
                print("\n⚠️  Des fiches référencées dans sessions.json sont manquantes. Veuillez les créer.")
        else:
            # Mode vérification seule
            print("🔍 Vérification des incohérences...")
            issues = fixer.check_consistency()
            
            # Générer un rapport même en mode vérification
            fixer.report['issues'] = issues
            report_path = fixer.generate_report(args.report)
            
            print(f"\n📊 Rapport de vérification généré : {report_path}")
            
            # Afficher un résumé
            total_issues = (
                len(issues.get('missing_fiches', [])) +
                len(issues.get('invalid_ids', [])) +
                len(issues.get('wrong_session_refs', []))
            )
            
            print(f"\n📋 Résumé :")
            print(f"- Incohérences détectées : {total_issues}")
            print(f"- Fiches manquantes : {len(issues.get('missing_fiches', []))}")
            print(f"- IDs invalides : {len(issues.get('invalid_ids', []))}")
            print(f"- Références de session incorrectes : {len(issues.get('wrong_session_refs', []))}")
            print(f"- Fiches valides : {len(issues.get('valid_fiches', []))}")
            
            if total_issues > 0:
                print("\n⚠️  Des incohérences ont été détectées. Utilisez l'option --fix pour les corriger automatiquement.")
    
    except Exception as e:
        logger.error(f"Une erreur critique s'est produite : {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
