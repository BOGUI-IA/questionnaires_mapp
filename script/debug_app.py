import os
import json
import streamlit as st
import logging
from typing import Dict, List, Any, Optional
import hashlib
import sys
from pathlib import Path
import datetime  # ← Ajouter cette ligne

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app_debug.log')
    ]
)
logger = logging.getLogger(__name__)

class AppDebugger:
    def __init__(self, app_dir: str = '.'):
        self.app_dir = Path(app_dir)
        self.issues = []
        self.fiches_dir = self.app_dir / 'data' / 'fiches'
        self.results = {
            'fiches': [],
            'sessions': [],
            'structure': {},
            'performance': {},
            'errors': []
        }

    def check_directory_structure(self) -> Dict:
        """Vérifie la structure des dossiers de l'application"""
        logger.info("Vérification de la structure des dossiers...")
        dirs_to_check = [
            self.app_dir / 'data',
            self.fiches_dir,
            self.app_dir / 'sessions'
        ]
        
        for d in dirs_to_check:
            if not d.exists():
                self.issues.append(f"Le dossier {d} n'existe pas")
                logger.error(f"Dossier manquant: {d}")
            else:
                logger.info(f"Dossier trouvé: {d}")
        
        return {
            'exists': all(d.exists() for d in dirs_to_check),
            'missing': [str(d) for d in dirs_to_check if not d.exists()]
        }

    def validate_fiche_structure(self, fiche_path: Path) -> Dict:
        """Valide la structure d'un fichier fiche"""
        try:
            with open(fiche_path, 'r', encoding='utf-8') as f:
                fiche = json.load(f)
                
            required_fields = ['id', 'title', 'description', 'questions']  # Changed 'titre' to 'title'
            missing_fields = [f for f in required_fields if f not in fiche]
            
            if missing_fields:
                return {
                    'valid': False,
                    'file': str(fiche_path),
                    'missing_fields': missing_fields
                }
                
            # Validation des questions
            questions_issues = []
            for i, q in enumerate(fiche['questions']):
                q_required = ['id', 'texte', 'type']
                q_missing = [f for f in q_required if f not in q]
                if q_missing:
                    questions_issues.append({
                        'question_index': i,
                        'missing_fields': q_missing
                    })
            
            return {
                'valid': len(questions_issues) == 0,
                'file': str(fiche_path),
                'questions_issues': questions_issues
            }
            
        except json.JSONDecodeError as e:
            return {
                'valid': False,
                'file': str(fiche_path),
                'error': f"Erreur de décodage JSON: {str(e)}"
            }
        except Exception as e:
            return {
                'valid': False,
                'file': str(fiche_path),
                'error': f"Erreur inattendue: {str(e)}"
            }

    def check_all_fiches(self) -> List[Dict]:
        """Vérifie toutes les fiches dans le dossier des fiches"""
        logger.info("Vérification des fichiers de fiches...")
        issues = []
        
        if not self.fiches_dir.exists():
            self.issues.append(f"Le dossier des fiches n'existe pas: {self.fiches_dir}")
            return []
            
        fiche_files = list(self.fiches_dir.glob('*.json'))
        if not fiche_files:
            self.issues.append("Aucun fichier de fiche trouvé")
            return []
            
        results = []
        for fiche_file in fiche_files:
            result = self.validate_fiche_structure(fiche_file)
            results.append(result)
            if not result['valid']:
                issues.append(f"Problème avec la fiche {fiche_file.name}")
                logger.error(f"Fiche invalide: {fiche_file.name} - {result.get('error', '')}")
        
        self.results['fiches'] = results
        return issues

    def check_session_state(self) -> List[str]:
        """Vérifie l'état de la session Streamlit"""
        logger.info("Vérification de l'état de la session...")
        issues = []
        
        try:
            if not hasattr(st, 'session_state'):
                issues.append("L'état de session Streamlit n'est pas disponible")
                return issues
                
            # Vérifier les clés essentielles
            essential_keys = ['current_fiche_id', 'responses']
            for key in essential_keys:
                if key not in st.session_state:
                    issues.append(f"Clé de session manquante: {key}")
            
            return issues
            
        except Exception as e:
            error_msg = f"Erreur lors de la vérification de la session: {str(e)}"
            logger.error(error_msg)
            issues.append(error_msg)
            return issues

    def check_widget_keys(self) -> List[str]:
        """Vérifie les clés des widgets pour les doublons potentiels"""
        logger.info("Vérification des clés de widgets...")
        issues = []
        
        try:
            # Analyser le fichier app.py pour trouver les clés de widgets
            app_file = self.app_dir / 'app.py'
            if not app_file.exists():
                return ["Fichier app.py introuvable"]
                
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Recherche des clés de widgets
            import re
            key_patterns = {
                'st.checkbox': r'st\.checkbox\([^)]*key=[\'"]([^\'"]+)[\'"]',
                'st.radio': r'st\.radio\([^)]*key=[\'"]([^\'"]+)[\'"]',
                'st.text_input': r'st\.text_input\([^)]*key=[\'"]([^\'"]+)[\'"]',
                'st.text_area': r'st\.text_area\([^)]*key=[\'"]([^\'"]+)[\'"]',
                'st.slider': r'st\.slider\([^)]*key=[\'"]([^\'"]+)[\'"]'
            }
            
            key_counts = {}
            for widget_type, pattern in key_patterns.items():
                keys = re.findall(pattern, content)
                for key in keys:
                    if key in key_counts:
                        key_counts[key].append(widget_type)
                    else:
                        key_counts[key] = [widget_type]
            
            # Vérifier les doublons
            for key, widgets in key_counts.items():
                if len(widgets) > 1:
                    issues.append(f"Clé de widget en double: '{key}' utilisée dans {', '.join(widgets)}")
            
            self.results['widget_keys'] = {
                'total_unique_keys': len(key_counts),
                'duplicate_keys': [k for k, v in key_counts.items() if len(v) > 1]
            }
            
            return issues
            
        except Exception as e:
            error_msg = f"Erreur lors de la vérification des clés de widgets: {str(e)}"
            logger.error(error_msg)
            return [error_msg]

    def check_performance(self) -> Dict:
        """Vérifie les problèmes de performance potentiels"""
        logger.info("Vérification des performances...")
        issues = []
        
        try:
            app_file = self.app_dir / 'app.py'
            if not app_file.exists():
                return {"error": "Fichier app.py introuvable"}
                
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            # Vérifier les imports inutiles
            if 'import os' in content and 'os.' not in content:
                issues.append("Import inutile: 'os' n'est pas utilisé")
                
            # Vérifier les boucles potentiellement coûteuses
            if 'for ' in content and 'range(' in content and 'tqdm' not in content:
                issues.append("Considérez d'utiliser tqdm pour les boucles longues")
            
            # Vérifier les appels API synchrones
            if 'requests.get(' in content or 'requests.post(' in content:
                issues.append("Utilisation d'appels API synchrones détectée - utilisez des appels asynchrones")
            
            self.results['performance']['issues'] = issues
            return {'issues': issues}
            
        except Exception as e:
            error_msg = f"Erreur lors de la vérification des performances: {str(e)}"
            logger.error(error_msg)
            return {'error': error_msg}

    def run_checks(self) -> Dict:
        """Exécute toutes les vérifications"""
        logger.info("Démarrage du débogage de l'application...")
        
        # Vérification de la structure des dossiers
        self.results['structure'] = self.check_directory_structure()
        
        # Vérification des fiches
        fiche_issues = self.check_all_fiches()
        
        # Vérification de l'état de la session
        session_issues = self.check_session_state()
        
        # Vérification des clés de widgets
        widget_issues = self.check_widget_keys()
        
        # Vérification des performances
        perf_results = self.check_performance()
        
        # Compilation des résultats
        all_issues = (
            self.issues + 
            fiche_issues + 
            session_issues + 
            widget_issues + 
            perf_results.get('issues', [])
        )
        
        self.results['summary'] = {
            'total_issues': len(all_issues),
            'issues': all_issues,
            'has_errors': len(all_issues) > 0
        }
        
        logger.info(f"Vérification terminée. {len(all_issues)} problèmes détectés.")
        return self.results

    def generate_report(self, output_file: str = 'debug_report.md') -> str:
        """Génère un rapport de débogage au format Markdown"""
        try:
            report = [
                "# Rapport de débogage de l'application",
                f"Généré le: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "\n## Résumé",
                f"**Total des problèmes détectés:** {self.results['summary']['total_issues']}",
                "\n## Détails"
            ]
            
            # Problèmes de structure
            if 'structure' in self.results and not self.results['structure']['exists']:
                report.append("\n### ❌ Problèmes de structure")
                report.append("Dossiers manquants:")
                for d in self.results['structure'].get('missing', []):
                    report.append(f"- {d}")
            
            # Problèmes de fiches
            if 'fiches' in self.results:
                invalid_fiches = [f for f in self.results['fiches'] if not f.get('valid', True)]
                if invalid_fiches:
                    report.append("\n### ❌ Problèmes dans les fiches")
                    for fiche in invalid_fiches:
                        report.append(f"- **{fiche.get('file', 'Fiche inconnue')}**")
                        if 'missing_fields' in fiche:
                            report.append(f"  - Champs manquants: {', '.join(fiche['missing_fields'])}")
                        if 'questions_issues' in fiche:
                            for issue in fiche['questions_issues']:
                                report.append(f"  - Question {issue['question_index']}: Champs manquants: {', '.join(issue['missing_fields'])}")
                        if 'error' in fiche:
                            report.append(f"  - Erreur: {fiche['error']}")
            
            # Problèmes de clés de widgets
            if 'widget_keys' in self.results and self.results['widget_keys'].get('duplicate_keys'):
                report.append("\n### ⚠️ Clés de widgets en double")
                for key in self.results['widget_keys']['duplicate_keys']:
                    report.append(f"- `{key}`")
            
            # Problèmes de performance
            if 'performance' in self.results and self.results['performance'].get('issues'):
                report.append("\n### ⚡ Problèmes de performance")
                for issue in self.results['performance'].get('issues', []):
                    report.append(f"- {issue}")
            
            # Problèmes généraux
            if self.issues:
                report.append("\n### ❗ Autres problèmes détectés")
                for issue in self.issues:
                    report.append(f"- {issue}")
            
            # Ajouter des conseils de débogage
            report.extend([
                "\n## Conseils de débogage",
                "1. **Pour les problèmes de structure**: Vérifiez que tous les dossiers nécessaires existent.",
                "2. **Pour les problèmes de fiches**: Vérifiez que chaque fiche a tous les champs requis et que le JSON est valide.",
                "3. **Pour les problèmes de session**: Assurez-vous que l'état de session est correctement initialisé au démarrage de l'application.",
                "4. **Pour les problèmes de widgets**: Vérifiez que toutes les clés de widgets sont uniques.",
                "5. **Pour les problèmes de performance**: Considérez d'optimiser les boucles et les appels réseau."
            ])
            
            # Écrire le rapport dans un fichier
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report))
            
            logger.info(f"Rapport de débogage généré: {output_file}")
            return output_file
            
        except Exception as e:
            error_msg = f"Erreur lors de la génération du rapport: {str(e)}"
            logger.error(error_msg)
            return error_msg

def debug_app():
    """Fonction principale pour le débogage de l'application"""
    st.set_page_config(
        page_title="Débogage de l'application",
        layout="wide"
    )
    
    st.title("🔍 Outil de débogage de l'application")
    st.write("Cet outil permet de détecter les problèmes potentiels dans l'application.")
    
    if st.button("Lancer la vérification", type="primary"):
        with st.spinner("Analyse en cours..."):
            debugger = AppDebugger()
            results = debugger.run_checks()
            
            # Afficher un résumé
            st.subheader("Résumé de la vérification")
            if results['summary']['total_issues'] == 0:
                st.success("✅ Aucun problème détecté !")
            else:
                st.error(f"❌ {results['summary']['total_issues']} problèmes détectés")
                
                # Afficher les problèmes par catégorie
                tabs = st.tabs(["Tous les problèmes", "Structure", "Fiches", "Session", "Widgets", "Performance"])
                
                with tabs[0]:  # Tous les problèmes
                    for issue in results['summary']['issues']:
                        st.error(issue)
                
                # Onglet Structure
                with tabs[1]:
                    if 'structure' in results and not results['structure']['exists']:
                        st.error("### Problèmes de structure")
                        for d in results['structure'].get('missing', []):
                            st.error(f"- Dossier manquant: {d}")
                    else:
                        st.success("✅ Aucun problème de structure détecté")
                
                # Onglet Fiches
                with tabs[2]:
                    invalid_fiches = [f for f in results.get('fiches', []) if not f.get('valid', True)]
                    if invalid_fiches:
                        st.error("### Problèmes dans les fiches")
                        for fiche in invalid_fiches:
                            with st.expander(f"Fiche: {os.path.basename(fiche.get('file', 'inconnue'))}", expanded=False):
                                if 'missing_fields' in fiche:
                                    st.error(f"Champs manquants: {', '.join(fiche['missing_fields'])}")
                                if 'questions_issues' in fiche:
                                    for issue in fiche['questions_issues']:
                                        st.error(f"Question {issue['question_index']}: Champs manquants: {', '.join(issue['missing_fields'])}")
                                if 'error' in fiche:
                                    st.error(f"Erreur: {fiche['error']}")
                    else:
                        st.success("✅ Aucun problème détecté dans les fiches")
                
                # Onglet Session
                with tabs[3]:
                    session_issues = [i for i in results['summary']['issues'] if 'session' in i.lower()]
                    if session_issues:
                        st.error("### Problèmes de session")
                        for issue in session_issues:
                            st.error(f"- {issue}")
                    else:
                        st.success("✅ Aucun problème de session détecté")
                
                # Onglet Widgets
                with tabs[4]:
                    if 'widget_keys' in results and results['widget_keys'].get('duplicate_keys'):
                        st.error("### Clés de widgets en double")
                        for key in results['widget_keys']['duplicate_keys']:
                            st.error(f"- `{key}`")
                    else:
                        st.success("✅ Aucune clé de widget en double détectée")
                
                # Onglet Performance
                with tabs[5]:
                    if 'performance' in results and results['performance'].get('issues'):
                        st.warning("### Problèmes de performance potentiels")
                        for issue in results['performance'].get('issues', []):
                            st.warning(f"- {issue}")
                    else:
                        st.success("✅ Aucun problème de performance détecté")
            
            # Générer un rapport
            report_path = debugger.generate_report()
            if os.path.exists(report_path):
                with open(report_path, "r", encoding='utf-8') as f:
                    st.download_button(
                        label="📥 Télécharger le rapport complet",
                        data=f,
                        file_name=os.path.basename(report_path),
                        mime="text/markdown"
                    )

if __name__ == "__main__":
    debug_app()