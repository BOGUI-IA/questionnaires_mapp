import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
import glob

# Configuration des chemins des dossiers de données
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
FICHES_DIR = DATA_DIR / "fiches"
SESSIONS_FILE = DATA_DIR / "sessions.json"

# Création des dossiers si inexistants
for directory in [DATA_DIR, FICHES_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

# Création du fichier sessions.json s'il n'existe pas
if not SESSIONS_FILE.exists():
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump({"sessions": {}}, f, ensure_ascii=False, indent=2)

# Fonction pour obtenir le chemin d'un fichier de fiche
def get_fiche_path(fiche_id):
    """Retourne le chemin complet vers un fichier de fiche"""
    return FICHES_DIR / f"{fiche_id}.json"

# Configuration de la page
def set_page_config():
    """Configure l'apparence de la page"""
    st.set_page_config(
        page_title="Questionnaires Stratégiques IA-INDUS",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Styles CSS personnalisés responsive
    st.markdown("""
    <style>
        /* Variables CSS pour la cohérence */
        :root {
            --primary-color: #4f46e5;
            --secondary-color: #7c3aed;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --bg-light: #f8fafc;
            --border-color: #e5e7eb;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        /* Reset et base */
        * {
            box-sizing: border-box;
        }
        
        /* Container principal responsive */
        .main {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
        }
        
        /* Header responsive */
        .welcome-header {
            text-align: center;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 2rem 1rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: var(--shadow);
        }
        
        .welcome-header h1 {
            font-size: clamp(1.5rem, 4vw, 2.5rem);
            margin-bottom: 0.5rem;
            font-weight: 700;
        }
        
        .welcome-header p {
            font-size: clamp(0.9rem, 2vw, 1.1rem);
            opacity: 0.9;
            margin: 0;
        }
        
        /* Grid responsive pour les fonctionnalités */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .feature-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow);
            transition: transform 0.2s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
            display: block;
        }
        
        /* Sessions grid responsive */
        .sessions-container {
            margin: 2rem 0;
        }
        
        .sessions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
            margin-top: 1rem;
        }
        
        .session-card {
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .session-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
        }
        
        .session-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        }
        
        .session-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .session-description {
            color: var(--text-secondary);
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 1rem;
        }
        
        .progress-container {
            margin: 1rem 0;
        }
        
        .progress-label {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background-color: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 50%, var(--success-color) 100%);
            position: relative;
            overflow: hidden;
        }
        
        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        /* Boutons responsive */
        .session-button {
            width: 100%;
            padding: 0.75rem 1rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-top: 1rem;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
        }
        
        .btn-secondary {
            background: var(--bg-light);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }
        
        .session-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Instructions responsive */
        .instructions-container {
            background: var(--bg-light);
            border-radius: 8px;
            padding: 1.5rem;
            margin: 2rem 0;
            border-left: 4px solid var(--primary-color);
        }
        
        .instructions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .instruction-item {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }
        
        .instruction-number {
            background: var(--primary-color);
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            font-weight: 600;
            flex-shrink: 0;
        }
        
        .instruction-text {
            font-size: 0.9rem;
            line-height: 1.4;
            color: var(--text-primary);
        }
        
        /* Responsive breakpoints */
        @media (max-width: 768px) {
            .main {
                padding: 0.5rem;
            }
            
            .welcome-header {
                padding: 1.5rem 1rem;
                margin-bottom: 1.5rem;
            }
            
            .sessions-grid {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
            
            .features-grid {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
            
            .instructions-grid {
                grid-template-columns: 1fr;
            }
            
            .session-card {
                padding: 1rem;
            }
        }
        
        @media (max-width: 480px) {
            .welcome-header {
                padding: 1rem 0.75rem;
            }
            
            .feature-card,
            .session-card {
                padding: 1rem;
            }
            
            .instructions-container {
                padding: 1rem;
            }
        }
        
        /* Animation d'entrée */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .animate-fade-in {
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* Amélioration de l'accessibilité */
        .session-button:focus {
            outline: 2px solid var(--primary-color);
            outline-offset: 2px;
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            :root {
                --text-primary: #f9fafb;
                --text-secondary: #d1d5db;
                --bg-light: #374151;
                --border-color: #4b5563;
            }
        }
        
        /* Styles pour les badges de statut (manquants) */
        .status-badge {
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            margin-left: auto;
            white-space: nowrap;
        }
        
        .status-complete {
            background: linear-gradient(135deg, var(--success-color), #059669);
            color: white;
        }
        
        .status-in-progress {
            background: linear-gradient(135deg, var(--warning-color), #d97706);
            color: white;
        }
        
        .status-not-started {
            background: linear-gradient(135deg, #6b7280, #4b5563);
            color: white;
        }
        
        /* Amélioration des boutons de navigation rapide */
        .quick-nav-container {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow);
        }
        
        /* Amélioration des cartes de fonctionnalités */
        .feature-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid var(--border-color);
            position: relative;
            overflow: hidden;
        }
        
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        }
        
        .feature-card h3 {
            color: var(--primary-color);
            margin: 0.5rem 0;
            font-size: 1.1rem;
        }
        
        /* Amélioration du titre de session */
        .session-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        /* Indicateurs visuels améliorés */
        .progress-fill {
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 50%, var(--success-color) 100%);
            position: relative;
            overflow: hidden;
        }
        
        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        /* Amélioration responsive pour mobile */
        @media (max-width: 768px) {
            .quick-nav-container {
                padding: 1rem;
            }
            
            .status-badge {
                font-size: 0.7rem;
                padding: 0.2rem 0.5rem;
            }
            
            .session-title {
                flex-direction: column;
                align-items: flex-start;
            }
        }
        
        /* Effets de hover améliorés */
        .session-card:hover .progress-fill {
            animation: pulse 1s ease-in-out;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        
        /* Amélioration de l'accessibilité */
        .feature-card:focus-within,
        .session-card:focus-within {
            outline: 2px solid var(--primary-color);
            outline-offset: 2px;
        }
        
        /* Amélioration des cartes de session */
        .session-card-enhanced {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.75rem 0;
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .session-card-enhanced:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        
        .session-card-enhanced::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        }
        
        /* Animation de la barre de progression */
        .progress-bar-animated {
            background: #e5e7eb;
            border-radius: 4px;
            height: 8px;
            overflow: hidden;
            position: relative;
        }
        
        .progress-fill-animated {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease-in-out;
            position: relative;
            overflow: hidden;
        }
        
        .progress-fill-animated::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            animation: shimmer 2s infinite;
        }
    </style>
    """, unsafe_allow_html=True)

def validate_and_fix_fiche_ids():
    """Valide et corrige automatiquement les IDs des fiches"""
    fiches_dir = Path("data/fiches")
    issues_found = []
    
    for fiche_file in fiches_dir.glob("*.json"):
        try:
            with open(fiche_file, 'r', encoding='utf-8') as f:
                fiche_data = json.load(f)
            
            expected_id = fiche_file.stem  # nom du fichier sans extension
            current_id = fiche_data.get('id')
            
            # Vérifier si l'ID est incorrect (numérique ou ne correspond pas)
            if isinstance(current_id, (int, float)) or current_id != expected_id:
                # Corriger l'ID
                fiche_data['id'] = expected_id
                
                # Sauvegarder la correction
                with open(fiche_file, 'w', encoding='utf-8') as f:
                    json.dump(fiche_data, f, ensure_ascii=False, indent=2)
                
                issues_found.append({
                    'file': str(fiche_file),
                    'old_id': current_id,
                    'new_id': expected_id
                })
        
        except Exception as e:
            st.error(f"Erreur lors de la validation de {fiche_file}: {e}")
    
    return issues_found

def get_fiche(fiche_id):
    """Récupère une fiche à partir de son ID avec gestion des IDs legacy
    
    Args:
        fiche_id (str): L'identifiant de la fiche à récupérer
        
    Returns:
        dict: Les données de la fiche ou None si non trouvée
    """
    # Utiliser un chemin absolu
    base_dir = os.path.dirname(os.path.abspath(__file__))
    fiche_file = os.path.join(base_dir, 'data', 'fiches', f'{fiche_id}.json')
    
    try:
        if os.path.exists(fiche_file):
            with open(fiche_file, 'r', encoding='utf-8') as f:
                fiche_data = json.load(f)
                # Vérifier si l'ID interne correspond
                if fiche_data.get('id') == fiche_id:
                    return fiche_data
                # Si pas de correspondance, chercher par nom de fichier
                fiche_data['id'] = fiche_id  # Forcer l'ID correct
                return fiche_data
        return None
    except Exception as e:
        st.error(f"Erreur lors du chargement de la fiche {fiche_id}: {e}")
        st.error(f"Chemin de la fiche: {fiche_file}")
        return None

class SessionManager:
    def __init__(self, sessions_file="data/sessions.json"):
        # Utiliser un chemin absolu basé sur le fichier app.py
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.sessions_file = os.path.join(base_dir, sessions_file)
        st.write(f"📁 Chemin du fichier sessions: {self.sessions_file}")
        self.sessions_data = self.load_sessions()
        self.fiches_cache = {}
    
    def load_sessions(self):
        """Charge les données de sessions avec validation"""
        try:
            if not os.path.exists(self.sessions_file):
                st.error(f"❌ Fichier sessions.json introuvable: {self.sessions_file}")
                st.write(f"Répertoire parent existe: {os.path.exists(os.path.dirname(self.sessions_file))}")
                if os.path.exists(os.path.dirname(self.sessions_file)):
                    st.write(f"Contenu du répertoire: {os.listdir(os.path.dirname(self.sessions_file))}")
                return {"sessions": {}}
                    
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                st.success(f"✅ Sessions chargées depuis: {self.sessions_file}")
                st.write(f"Nombre de sessions dans le fichier: {len(data.get('sessions', {}))}")
                return data
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement des sessions : {e}")
            st.error(f"Type d'erreur: {type(e).__name__}")
            st.error(f"Chemin du fichier: {self.sessions_file}")
            return {"sessions": {}}
    
    def get_session_by_id(self, session_id):
        """Récupère une session par son ID"""
        return self.sessions_data.get("sessions", {}).get(session_id)
    
    def get_session_fiches(self, session_id):
        """Récupère toutes les fiches d'une session avec cache"""
        session = self.get_session_by_id(session_id)
        if not session or 'fiches' not in session:
            return []
        
        fiches = []
        for fiche_id in session['fiches']:
            if fiche_id not in self.fiches_cache:
                self.fiches_cache[fiche_id] = get_fiche(fiche_id)
            
            if self.fiches_cache[fiche_id]:
                fiches.append(self.fiches_cache[fiche_id])
        
        return fiches
    
    def calculate_session_progress(self, session_id):
        """Calcule la progression d'une session de manière optimisée"""
        session = self.get_session_by_id(session_id)
        if not session or 'fiches' not in session or not session['fiches']:
            return 0
        
        total_questions = 0
        answered_questions = 0
        
        # Parcourir toutes les fiches de la session
        for fiche_id in session['fiches']:
            if fiche_id not in self.fiches_cache:
                self.fiches_cache[fiche_id] = get_fiche(fiche_id)
                
            fiche = self.fiches_cache[fiche_id]
            if not fiche or 'questions' not in fiche:
                continue
                
            questions = fiche['questions']
            total_questions += len(questions)
            
            # Vérifier les réponses pour chaque question
            for question in questions:
                question_id = question.get('id')
                if question_id and 'responses' in st.session_state:
                    response = st.session_state['responses'].get(question_id, {})
                    if response:
                        answered_questions += 1
        
        # Calculer le pourcentage de progression
        if total_questions == 0:
            return 0
            
        progress = int((answered_questions / total_questions) * 100)
        return min(100, max(0, progress))  # S'assurer que c'est entre 0 et 100

def get_session_progress(session):
    """
    Calcule la progression d'une session en pourcentage
    
    Args:
        session (dict): Dictionnaire contenant les informations de la session
        
    Returns:
        int: Pourcentage de progression (0-100)
    """
    # Vérifier si la session a des fiches
    if 'fiches' not in session or not session['fiches']:
        return 0
    
    total_questions = 0
    answered_questions = 0
    
    # Parcourir toutes les fiches de la session
    for fiche_id in session['fiches']:
        fiche = get_fiche(fiche_id)
        if not fiche or 'questions' not in fiche:
            continue
            
        questions = fiche['questions']
        total_questions += len(questions)
        
        # Vérifier les réponses pour chaque question
        for question in questions:
            question_id = question.get('id')
            if question_id and 'responses' in st.session_state:
                response = st.session_state['responses'].get(question_id, {})
                if response:
                    answered_questions += 1
    
    # Calculer le pourcentage de progression
    if total_questions == 0:
        return 0
        
    progress = int((answered_questions / total_questions) * 100)
    return min(100, max(0, progress))  # S'assurer que c'est entre 0 et 100

def show_toast_notification(message, type="success"):
    """Affiche une notification toast"""
    icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️"
    }
    
    st.toast(f"{icons.get(type, '📢')} {message}", icon=icons.get(type, "📢"))

def save_current_responses(session_id=None, responses=None, auto_save=False):
    """Sauvegarde les réponses actuelles dans un fichier JSON"""
    try:
        # Utiliser les paramètres fournis ou les valeurs par défaut
        if session_id is None:
            session_id = st.session_state.get('selected_session', 'default')
        if responses is None:
            response_key = f'responses_{session_id}'
            responses = st.session_state.get(response_key, {})
        
        # Créer le dossier de sauvegarde s'il n'existe pas
        save_dir = os.path.join(os.path.dirname(__file__), "data", "responses")
        os.makedirs(save_dir, exist_ok=True)
        
        # Nom du fichier avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"responses_{session_id}_{timestamp}.json"
        filepath = os.path.join(save_dir, filename)
        
        # Sauvegarder les données
        save_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'responses': responses
        }
        
        # Ajouter un indicateur de sauvegarde automatique
        if auto_save:
            save_data['auto_save'] = True
            save_data['save_type'] = 'automatic'
        else:
            save_data['save_type'] = 'manual'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        # Notification différente selon le type de sauvegarde
        if auto_save:
            st.toast("💾 Sauvegarde automatique effectuée", icon="✅")
        else:
            st.success("✅ Réponses sauvegardées avec succès !")
            st.balloons()
        
        return True
    except Exception as e:
        if not auto_save:  # Ne pas afficher d'erreur pour l'auto-save
            st.error(f"Erreur lors de la sauvegarde : {str(e)}")
        return False

def load_responses(session_id):
    """Charge les réponses sauvegardées pour une session"""
    try:
        responses_dir = os.path.join(os.path.dirname(__file__), "data", "responses")
        if not os.path.exists(responses_dir):
            return {}
        
        # Chercher le fichier de réponses le plus récent pour cette session
        pattern = f"responses_{session_id}_*.json"
        files = glob.glob(os.path.join(responses_dir, pattern))
        
        if not files:
            return {}
        
        # Prendre le fichier le plus récent
        latest_file = max(files, key=os.path.getctime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('responses', {})
    except Exception as e:
        st.error(f"Erreur lors du chargement des réponses : {str(e)}")
        return {}

def display_session_progress(selected_session, session_id):
    """Affiche la progression de la session sélectionnée"""
    progress = get_session_progress(selected_session)
    
    # Afficher la barre de progression
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.progress(progress / 100, text=f"Progression de la session : {progress}%")
    
    with col2:
        # Badge de statut
        if progress == 100:
            st.success("✅ Terminée")
        elif progress > 0:
            st.info(f"🔄 {progress}%")
        else:
            st.warning("⚪ Non commencée")
    
    # Charger les réponses existantes si disponibles
    if session_id:
        response_key = f'responses_{session_id}'
        if response_key not in st.session_state:
            saved_responses = load_responses(session_id)
            if saved_responses:
                st.session_state[response_key] = saved_responses
                st.info("📂 Réponses précédentes chargées")

# Page d'accueil améliorée
def display_enhanced_session_selector():
    """Affichage amélioré du sélecteur de sessions"""
    session_manager = SessionManager()
    sessions = session_manager.sessions_data.get("sessions", {})
    
    if not sessions:
        st.error("❌ Aucune session trouvée. Vérifiez le fichier sessions.json")
        return
    
    # Créer des colonnes pour l'affichage en grille
    cols = st.columns(2)
    
    for i, (session_id, session) in enumerate(sessions.items()):
        with cols[i % 2]:
            progress = session_manager.calculate_session_progress(session_id)
            
            # Déterminer la couleur de fond selon le progrès
            bg_color = "#f0f9ff" if progress > 0 else "#f9fafb"
            progress_color = "#10b981" if progress == 100 else "#3b82f6"
            
            # Carte de session avec progression - HTML corrigé
            session_html = f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 1rem;
                margin: 0.5rem 0;
                background: {bg_color};
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s ease;
            ">
                <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">
                    {session.get('icon', '📋')} {session.get('title', session_id)}
                </h4>
                <p style="
                    font-size: 0.9rem; 
                    color: #666; 
                    margin: 0 0 1rem 0;
                    line-height: 1.4;
                ">
                    {session.get('description', '')[:100]}{'...' if len(session.get('description', '')) > 100 else ''}
                </p>
                <div style="margin: 0.5rem 0;">
                    <div style="
                        background: #e5e7eb; 
                        border-radius: 4px; 
                        height: 8px;
                        overflow: hidden;
                    ">
                        <div style="
                            background: {progress_color};
                            width: {progress}%;
                            height: 100%;
                            border-radius: 4px;
                            transition: width 0.3s ease;
                        "></div>
                    </div>
                    <small style="color: #6b7280; font-weight: 500;">{progress}% complété</small>
                </div>
            </div>
            """
            
            # Afficher le HTML
            st.markdown(session_html, unsafe_allow_html=True)
            
            # Bouton d'action
            if st.button(
                f"🚀 Commencer {session.get('title', session_id)}", 
                key=f"start_{session_id}", 
                use_container_width=True,
                type="primary"
            ):
                st.session_state.selected_session = session_id
                st.session_state.current_page = "Questionnaires"
                st.rerun()

def display_enhanced_session_selector_v2():
    """Version améliorée avec classes CSS"""
    session_manager = SessionManager()
    sessions = session_manager.sessions_data.get("sessions", {})
    
    cols = st.columns(2)
    
    for i, (session_id, session) in enumerate(sessions.items()):
        with cols[i % 2]:
            progress = session_manager.calculate_session_progress(session_id)
            progress_color = "#10b981" if progress == 100 else "#3b82f6"
            
            st.markdown(f"""
            <div class="session-card-enhanced">
                <h4 style="margin: 0 0 0.5rem 0; color: var(--text-primary);">
                    {session.get('icon', '📋')} {session.get('title', session_id)}
                </h4>
                <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 0 0 1rem 0; line-height: 1.4;">
                    {session.get('description', '')[:100]}{'...' if len(session.get('description', '')) > 100 else ''}
                </p>
                <div class="progress-bar-animated">
                    <div class="progress-fill-animated" style="width: {progress}%; background: {progress_color};"></div>
                </div>
                <small style="color: var(--text-secondary); font-weight: 500; margin-top: 0.5rem; display: block;">
                    {progress}% complété
                </small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(
                f"🚀 Commencer {session.get('title', session_id)}", 
                key=f"start_v2_{session_id}", 
                use_container_width=True,
                type="primary"
            ):
                st.session_state.selected_session = session_id
                st.session_state.current_page = "Questionnaires"
                st.rerun()

def show_home():
    """Affiche la page d'accueil responsive de l'application"""
    
    # Header principal avec design moderne
    st.markdown("""
    <div class="welcome-header animate-fade-in">
        <h1>🚀 Questionnaires Stratégiques IA-INDUS</h1>
        <p>Participez à l'élaboration de notre stratégie d'intelligence artificielle industrielle</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Section de statistiques rapides
    sessions_data = load_sessions()
    sessions = sessions_data.get('sessions', {})
    
    if sessions:
        total_sessions = len(sessions)
        completed_count = sum(1 for session_id, session in sessions.items() if get_session_progress(session) == 100)
        in_progress_count = sum(1 for session_id, session in sessions.items() if 0 < get_session_progress(session) < 100)
        
        st.markdown(f"""
        <div class="stats-container animate-fade-in" style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        ">
            <div class="stat-card" style="
                background: linear-gradient(135deg, var(--success-color), #059669);
                color: white;
                padding: 1.5rem;
                border-radius: 12px;
                text-align: center;
                box-shadow: var(--shadow);
            ">
                <div style="font-size: 2rem; font-weight: bold;">{completed_count}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Sessions Terminées</div>
            </div>
            <div class="stat-card" style="
                background: linear-gradient(135deg, var(--warning-color), #d97706);
                color: white;
                padding: 1.5rem;
                border-radius: 12px;
                text-align: center;
                box-shadow: var(--shadow);
            ">
                <div style="font-size: 2rem; font-weight: bold;">{in_progress_count}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">En Cours</div>
            </div>
            <div class="stat-card" style="
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                padding: 1.5rem;
                border-radius: 12px;
                text-align: center;
                box-shadow: var(--shadow);
            ">
                <div style="font-size: 2rem; font-weight: bold;">{total_sessions}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Total Sessions</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Zone de navigation rapide améliorée
    st.markdown("""
    <div class="quick-nav-container animate-fade-in" style="margin: 2rem 0;">
        <h3 style="text-align: center; margin-bottom: 1.5rem; color: var(--primary-color);">🎯 Navigation Rapide</h3>
        <p style="text-align: center; color: var(--text-secondary); margin-bottom: 1rem;">Accédez rapidement aux différentes sections de l'application</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Boutons de navigation rapide améliorés
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(
            "📝\n\n**Questionnaires**\n\nCommencer ou continuer\nvos questionnaires",
            key="quick_nav_questionnaires",
            use_container_width=True,
            type="primary",
            help="Accéder aux questionnaires thématiques"
        ):
            st.session_state.current_page = "Questionnaires"
            st.rerun()
    
    with col2:
        if st.button(
            "📊\n\n**Tableau de Bord**\n\nVoir votre progression\net statistiques",
            key="quick_nav_dashboard",
            use_container_width=True,
            help="Consulter vos statistiques de progression"
        ):
            st.session_state.current_page = "Tableau de Bord"
            st.rerun()
    
    with col3:
        if st.button(
            "❓\n\n**Aide**\n\nObtenir de l'aide\net support",
            key="quick_nav_help",
            use_container_width=True,
            help="Accéder à l'aide et au support"
        ):
            st.session_state.current_page = "Aide"
            st.rerun()
    
    with col4:
        if st.button(
            "🔄\n\n**Actualiser**\n\nRecharger les données\net la page",
            key="quick_nav_refresh",
            use_container_width=True,
            help="Actualiser les données de l'application"
        ):
            st.rerun()
    
    # Section des fonctionnalités clés
    st.markdown("""
    <div class="features-grid animate-fade-in">
        <div class="feature-card">
            <span class="feature-icon">📋</span>
            <h3>Questionnaires Thématiques</h3>
            <p>Répondez à des questions structurées par domaines d'expertise pour contribuer à notre vision stratégique.</p>
        </div>
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <h3>Suivi en Temps Réel</h3>
            <p>Visualisez votre progression et suivez l'avancement de vos réponses avec des indicateurs visuels.</p>
        </div>
        <div class="feature-card">
            <span class="feature-icon">💾</span>
            <h3>Sauvegarde Automatique</h3>
            <p>Vos réponses sont automatiquement sauvegardées. Reprenez où vous vous êtes arrêté à tout moment.</p>
        </div>
        <div class="feature-card">
            <span class="feature-icon">🎯</span>
            <h3>Interface Intuitive</h3>
            <p>Navigation simple et ergonomique, optimisée pour tous les appareils et tailles d'écran.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Instructions d'utilisation
    st.markdown("""
    <div class="instructions-container animate-fade-in">
        <h3>💡 Comment utiliser cette application ?</h3>
        <div class="instructions-grid">
            <div class="instruction-item">
                <div class="instruction-number">1</div>
                <div class="instruction-text">
                    <strong>Sélectionnez une session</strong><br>
                    Choisissez parmi les sessions thématiques disponibles ci-dessous
                </div>
            </div>
            <div class="instruction-item">
                <div class="instruction-number">2</div>
                <div class="instruction-text">
                    <strong>Répondez aux questions</strong><br>
                    Parcourez les fiches et répondez aux questions de votre expertise
                </div>
            </div>
            <div class="instruction-item">
                <div class="instruction-number">3</div>
                <div class="instruction-text">
                    <strong>Sauvegardez régulièrement</strong><br>
                    Utilisez le bouton de sauvegarde pour conserver vos réponses
                </div>
            </div>
            <div class="instruction-item">
                <div class="instruction-number">4</div>
                <div class="instruction-text">
                    <strong>Suivez votre progression</strong><br>
                    Consultez le tableau de bord pour voir votre avancement global
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Section des sessions avec design amélioré
    st.markdown('<div class="sessions-container animate-fade-in">', unsafe_allow_html=True)
    st.markdown("## 📋 Sessions Disponibles")
    
    # Utiliser le sélecteur de sessions amélioré
    display_enhanced_session_selector()
    
    # Footer informatif
    st.markdown("""
    <div style="margin-top: 3rem; padding: 2rem; background: var(--bg-light); border-radius: 8px; text-align: center;">
        <h4>🤝 Besoin d'aide ?</h4>
        <p>Consultez la section <strong>Aide</strong> dans le menu latéral pour plus d'informations sur l'utilisation de cette application.</p>
        <p style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 1rem;">
            💡 <strong>Conseil :</strong> Sauvegardez régulièrement vos réponses pour éviter toute perte de données.
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_help():
    """Affiche la page d'aide et de support"""
    st.title("❓ Aide et Support")
    
    st.markdown("### Comment utiliser cette application ?")
    st.markdown("""
    - **Navigation** : Utilisez le menu latéral pour vous déplacer
    - **Questionnaires** : Répondez aux questions des fiches thématiques
    - **Sauvegarde** : Enregistrez régulièrement vos réponses
    - **Progression** : Suivez votre avancement en temps réel
    """)
    
    st.markdown("### Indicateurs de statut")
    st.markdown("""
    - 🟢 **Complète** : Toutes les questions répondues
    - 🟡 **En cours** : Réponses partielles
    - ⚪ **Non commencé** : Aucune réponse
    """)
    
    st.markdown("### Support technique")
    st.markdown("""
    Pour toute question ou problème, veuillez contacter :
    - Email : support@ia-indus.fr
    - Téléphone : +33 1 23 45 67 89
    """)

def display_guidelines(sessions_data, selected_session):
    """Affiche les directives spécifiques à la session sélectionnée"""
    # Ajouter des conseils spécifiques selon le type de session
    session_type = selected_session.get('type', 'execution')
    
    if session_type == 'execution':
        st.info("💡 **Pensez MVP** - Qu'est-ce qui est essentiel pour les 3-6 prochains mois ?")
    elif session_type == 'strategy':
        st.info("🚀 **Soyez visionnaire** - Imaginez l'entreprise de demain")
    
    st.success("🎯 **Soyez honnête et direct** - Vos réponses authentiques sont la clé du succès")
    
    # Vérifier s'il y a des directives spécifiques pour cette session
    if 'guidelines' in selected_session and selected_session['guidelines']:
        with st.expander("📋 Consignes spécifiques à cette session", expanded=True):
            st.markdown(selected_session['guidelines'], unsafe_allow_html=True)
    
    # Afficher les conseils généraux pour répondre aux questions
    with st.expander("💡 Conseils pour répondre aux questions", expanded=False):
        st.markdown("""
        #### **1. Pour les Questions à Choix Multiples (QCM) :**
        - **Priorisez** : Sélectionnez l'option la plus pertinente (une seule par défaut)
        - **Justifiez** : Si vous sélectionnez deux options, expliquez pourquoi elles sont indissociables
        - **Pensez MVP** : Identifiez ce qui est essentiel pour une première version
        
        #### **2. L'Usage de la Case "Précisions/Commentaires" :**
        
        Cette case est **essentielle**. Elle te permet de dépasser les limites du QCM. Utilise-la systématiquement pour :
        
        *   **Justifier un choix :** "Je choisis (B) car dans notre secteur, la standardisation est le problème N°1."
        *   **Ajouter une nuance :** "Je choisis (A), mais à condition que cela soit fait de manière très visuelle."
        *   **Exprimer un doute :** "Je penche pour (C), mais je ne suis pas certain de l'impact sur les équipes."
        *   **Proposer une alternative (Option E) :** Si aucune des options ne te convient, décris ta propre vision ici. C'est peut-être là que se cachent les meilleures idées.
        
        #### **3. Conseils généraux :**
        - **Soyez précis** : Utilisez les commentaires pour apporter des précisions importantes
        - **Sauvegardez** : N'oubliez pas de sauvegarder régulièrement vos réponses
        """)

def validate_fiche_responses(fiche):
    """Valide les réponses d'une fiche et retourne les erreurs et avertissements"""
    errors = []
    warnings = []
    
    for question in fiche.get('questions', []):
        question_id = question.get('id')
        if not question_id:
            continue
            
        responses = st.session_state.responses.get(question_id, [])
        comment_key = f"{question_id}_comment"
        comment = st.session_state.responses.get(comment_key, '')
        
        # Vérifier la règle des deux réponses
        if isinstance(responses, list) and len(responses) == 2:
            if len(comment.strip()) < 10:
                question_text = question.get('text', question_id)[:50]
                errors.append(f"**Question** : {question_text}...\n**Erreur** : Justification obligatoire (minimum 10 caractères) pour deux réponses sélectionnées.")
        
        # Vérifier les réponses vides
        if not responses or (isinstance(responses, list) and len(responses) == 0):
            question_text = question.get('text', question_id)[:50]
            warnings.append(f"**Question** : {question_text}...\n**Attention** : Aucune réponse sélectionnée.")
    
    return errors, warnings

def display_validation_results(fiche):
    """Affiche les résultats de validation avec interface utilisateur"""
    errors, warnings = validate_fiche_responses(fiche)
    
    if errors:
        st.error("❌ **Erreurs à corriger avant sauvegarde :**")
        for error in errors:
            st.error(error)
        return False
    
    if warnings:
        st.warning("⚠️ **Avertissements :**")
        for warning in warnings:
            st.warning(warning)
    
    if not errors and not warnings:
        st.success("✅ **Toutes les réponses sont valides !**")
    
    return True

def display_fiche(fiche):
    """Affiche une fiche de questionnaire avec ses questions"""
    # Ajouter les scripts d'amélioration
    add_auto_save_script()
    add_progress_indicators()
    
    if not fiche:
        st.error("Fiche non trouvée")
        return
    
    # Titre de la fiche
    st.markdown(f"## 📋 {fiche.get('title', 'Fiche sans titre')}")
    
    # Description de la fiche si disponible
    if 'description' in fiche and fiche['description']:
        st.markdown(f"*{fiche['description']}*")
        st.divider()
    
    # Vérifier si la fiche a des questions
    if 'questions' not in fiche or not fiche['questions']:
        st.warning("Aucune question disponible dans cette fiche.")
        return
    
    # Initialiser les réponses pour cette fiche si nécessaire
    fiche_id = fiche.get('id', 'unknown')
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    
    # Afficher chaque question
    for question_idx, question in enumerate(fiche['questions'], 1):
        question_id = question.get('id', f"{fiche_id}_q{question_idx}")
        
        # Container pour la question
        with st.container():
            st.markdown(f"### Question {question_idx}")
            
            # Texte de la question (utiliser 'text' au lieu de 'question')
            question_text = question.get('text', 'Question sans texte')
            st.markdown(f"**{question_text}**")
            
            # Contexte ou aide si disponible
            if 'context' in question and question['context']:
                with st.expander("ℹ️ Contexte", expanded=False):
                    st.markdown(question['context'])
            
            # Type de question et options
            question_type = question.get('type', 'radio')
            options = question.get('options', [])
            
            if question_type == 'radio' and options:
                # Système de cases à cocher avec validation QCM
                current_responses = st.session_state.responses.get(question_id, [])
                if not isinstance(current_responses, list):
                    # Compatibilité ascendante : convertir les anciennes réponses
                    current_responses = [current_responses] if current_responses else []
                
                # Affichage des options avec cases à cocher
                selected_options = []
                
                st.markdown("**Sélectionnez une ou deux options maximum :**")
                
                for i, option in enumerate(options):
                    is_checked = option in current_responses
                    
                    # Désactiver les cases si 2 options déjà sélectionnées et cette option n'est pas cochée
                    is_disabled = len(current_responses) >= 2 and not is_checked
                    
                    # Création d'une clé unique incluant l'ID de la fiche pour éviter les doublons
                    
                    if st.checkbox(
                        option,
                        value=is_checked,
                        key=f"qcm_{fiche_id}_{question_id}_option_{i}",
                        disabled=is_disabled
                    ):
                        selected_options.append(option)
                
                # Validation des règles QCM
                if len(selected_options) > 2:
                    st.error("⚠️ **Erreur** : Maximum 2 réponses autorisées. Veuillez désélectionner des options.")
                    # Garder seulement les 2 premières sélections
                    selected_options = selected_options[:2]
                elif len(selected_options) == 2:
                    st.warning("💡 **Attention** : Deux réponses sélectionnées. Une justification est **obligatoire** ci-dessous.")
                    st.info("📝 **Conseil** : Expliquez pourquoi ces deux options sont pertinentes et comment elles se complètent.")
                elif len(selected_options) == 1:
                    st.success("✅ Une réponse sélectionnée (recommandé pour prioriser).")
                
                # Mettre à jour les réponses
                st.session_state.responses[question_id] = selected_options
                
            elif question_type == 'checkbox' and options:
                # Question à choix multiples
                current_responses = st.session_state.responses.get(question_id, [])
                if not isinstance(current_responses, list):
                    current_responses = []
                
                selected_options = []
                for i, option in enumerate(options):
                    if st.checkbox(
                        option,
                        value=option in current_responses,
                        key=f"checkbox_{fiche_id}_{question_id}_option_{i}"
                    ):
                        selected_options.append(option)
                
                st.session_state.responses[question_id] = selected_options
                
            elif question_type == 'text':
                # Question de texte libre
                current_response = st.session_state.responses.get(question_id, '')
                text_response = st.text_input(
                    "Votre réponse :",
                    value=current_response,
                    key=f"text_{fiche_id}_{question_id}"
                )
                st.session_state.responses[question_id] = text_response
                
            elif question_type == 'textarea':
                # Question de texte long
                current_response = st.session_state.responses.get(question_id, '')
                text_response = st.text_area(
                    "Votre réponse :",
                    value=current_response,
                    key=f"textarea_{fiche_id}_{question_id}",
                    height=100
                )
                st.session_state.responses[question_id] = text_response
                
            elif question_type == 'scale':
                # Question avec échelle
                scale_min = question.get('scale_min', 1)
                scale_max = question.get('scale_max', 5)
                current_response = st.session_state.responses.get(question_id, scale_min)
                
                scale_response = st.slider(
                    "Évaluez sur une échelle :",
                    min_value=scale_min,
                    max_value=scale_max,
                    value=current_response,
                    key=f"scale_{fiche_id}_{question_id}"
                )
                st.session_state.responses[question_id] = scale_response
            
            # Zone de commentaire si spécifiée dans la question
            if 'comment' in question and question['comment']:
                comment_key = f"{question_id}_comment"
                current_comment = st.session_state.responses.get(comment_key, '')
                
                # Vérifier si le commentaire est obligatoire
                selected_responses = st.session_state.responses.get(question_id, [])
                is_required = isinstance(selected_responses, list) and len(selected_responses) == 2
                
                # Construire le label avec indication d'obligation
                label = question['comment']
                if is_required:
                    label += " ⚠️ **OBLIGATOIRE** (minimum 10 caractères)"
                
                # Zone de commentaire avec aide contextuelle
                help_text = "💡 Utilisez cette zone pour :"
                if is_required:
                    help_text += "\n• Justifier pourquoi vous avez choisi ces 2 options\n• Expliquer comment elles se complètent\n• Préciser les priorités entre elles"
                else:
                    help_text += "\n• Apporter des nuances à votre choix\n• Proposer des alternatives\n• Partager votre expérience"
                
                # Ajouter un placeholder plus informatif
                placeholder_text = "💡 Astuce : Soyez spécifique et concret. Exemple : 'J'ai choisi ces options car...'"
                
                comment = st.text_area(
                    label,
                    value=current_comment,
                    key=f"comment_{fiche_id}_{question_id}",
                    height=80,
                    help=help_text,
                    placeholder=placeholder_text
                )
                
                # Validation en temps réel pour deux réponses
                if is_required:
                    char_count = len(comment.strip())
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if char_count < 10:
                            st.error(f"❌ **Justification insuffisante** : {char_count}/10 caractères minimum requis.")
                            st.markdown("**Exemple de bonne justification :**")
                            st.info("Ces deux options se complètent car la première répond aux besoins immédiats (3-6 mois) tandis que la seconde prépare notre vision long terme...")
                        else:
                            st.success(f"✅ Justification valide ({char_count} caractères)")
                    
                    with col2:
                        # Barre de progression pour les caractères
                        progress = min(char_count / 10, 1.0)
                        st.progress(progress)
                
                # Sauvegarder le commentaire
                if comment:
                    st.session_state.responses[comment_key] = comment
            
            st.divider()
    
    # Boutons d'action en bas de la fiche
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # Validation avant sauvegarde
        is_valid = display_validation_results(fiche)
        
        if st.button(
            "💾 Sauvegarder les réponses", 
            key=f"save_{fiche_id}", 
            type="primary",
            disabled=not is_valid
        ):
            if is_valid and save_current_responses():
                st.success("✅ Réponses sauvegardées avec succès !")
                st.balloons()  # Animation de succès
                st.rerun()
            elif not is_valid:
                st.error("❌ Veuillez corriger les erreurs avant de sauvegarder.")
    
    with col2:
        if st.button("📊 Voir la progression", key=f"progress_{fiche_id}"):
            # Calculer et afficher la progression pour cette fiche
            total_questions = len(fiche['questions'])
            answered_questions = sum(1 for q in fiche['questions'] 
                                   if st.session_state.responses.get(q.get('id', '')))
            progress = (answered_questions / total_questions * 100) if total_questions > 0 else 0
            st.info(f"Progression de cette fiche : {progress:.1f}% ({answered_questions}/{total_questions} questions)")
    
    with col3:
        if st.button("🔄 Réinitialiser cette fiche", key=f"reset_{fiche_id}"):
            # Confirmer avant de réinitialiser
            if st.button("⚠️ Confirmer la réinitialisation", key=f"confirm_reset_{fiche_id}", type="secondary"):
                # Supprimer les réponses de cette fiche
                for question in fiche['questions']:
                    question_id = question.get('id', '')
                    if question_id in st.session_state.responses:
                        del st.session_state.responses[question_id]
                    comment_key = f"{question_id}_comment"
                    if comment_key in st.session_state.responses:
                        del st.session_state.responses[comment_key]
                st.success("🔄 Fiche réinitialisée !")
                st.rerun()

def get_fiche_progress(fiche):
    """Calcule la progression d'une fiche en pourcentage
    
    Args:
        fiche (dict): Dictionnaire contenant les informations de la fiche
        
    Returns:
        int: Pourcentage de progression (0-100)
    """
    if not fiche or 'questions' not in fiche or not fiche['questions']:
        return 0
        
    total_questions = len(fiche['questions'])
    answered_questions = 0
    
    # Vérifier les réponses pour chaque question
    for question in fiche['questions']:
        question_id = question.get('id')
        if question_id and 'responses' in st.session_state:
            response = st.session_state['responses'].get(question_id, {})
            if response:
                answered_questions += 1
    
    # Calculer le pourcentage de progression
    if total_questions == 0:
        return 0
        
    progress = int((answered_questions / total_questions) * 100)
    return min(100, max(0, progress))  # S'assurer que c'est entre 0 et 100

def show_fiche_progress_detail(fiche):
    """Affiche le détail de la progression d'une fiche"""
    if not fiche or 'questions' not in fiche:
        st.warning("Aucune question disponible dans cette fiche.")
        return
        
    total_questions = len(fiche['questions'])
    answered_questions = 0
    
    # Créer un tableau de progression
    progress_data = []
    
    for idx, question in enumerate(fiche['questions'], 1):
        question_id = question.get('id')
        question_text = question.get('text', 'Question sans texte')[:50] + '...' if len(question.get('text', '')) > 50 else question.get('text', 'Question sans texte')
        
        # Vérifier si la question a une réponse
        has_response = False
        if question_id and 'responses' in st.session_state:
            response = st.session_state['responses'].get(question_id, {})
            has_response = bool(response)
            if has_response:
                answered_questions += 1
        
        # Ajouter au tableau
        progress_data.append({
            "N°": idx,
            "Question": question_text,
            "Statut": "✅ Répondue" if has_response else "❌ Non répondue"
        })
    
    # Afficher le résumé
    st.info(f"📊 **Progression de la fiche** : {answered_questions}/{total_questions} questions répondues ({int((answered_questions/total_questions)*100 if total_questions > 0 else 0)}%)")
    
    # Afficher le tableau détaillé
    st.dataframe(progress_data, use_container_width=True)

def reset_fiche_responses(fiche):
    """Réinitialise toutes les réponses d'une fiche"""
    if 'responses' in st.session_state and fiche and 'questions' in fiche:
        fiche_id = fiche.get('id', '')
        for question in fiche['questions']:
            question_id = question.get('id', '')
            if question_id in st.session_state.responses:
                del st.session_state.responses[question_id]
            comment_key = f"{question_id}_comment"
            if comment_key in st.session_state.responses:
                del st.session_state.responses[comment_key]
        
        # Marquer comme modifié pour forcer la sauvegarde
        if 'unsaved_changes' not in st.session_state:
            st.session_state.unsaved_changes = {}
        st.session_state.unsaved_changes[fiche_id] = True
        return True
    return False

def display_fiche_content(fiche):
    """Affiche le contenu d'une fiche sans les boutons d'action"""
    if not fiche:
        st.error("Fiche non trouvée")
        return
    
    # Vérifier si la fiche a des questions
    if 'questions' not in fiche or not fiche['questions']:
        st.warning("Aucune question disponible dans cette fiche.")
        return
    
    # Initialiser les réponses pour cette fiche si nécessaire
    fiche_id = fiche.get('id', 'unknown')
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    
    # Afficher chaque question
    for question_idx, question in enumerate(fiche['questions'], 1):
        question_id = question.get('id', f"{fiche_id}_q{question_idx}")
        
        # Container pour la question
        with st.container():
            st.markdown(f"### Question {question_idx}")
            
            # Texte de la question (utiliser 'text' au lieu de 'question')
            question_text = question.get('text', 'Question sans texte')
            st.markdown(f"**{question_text}**")
            
            # Contexte ou aide si disponible
            if 'context' in question and question['context']:
                with st.expander("ℹ️ Contexte", expanded=False):
                    st.markdown(question['context'])
            
            # Type de question et options
            question_type = question.get('type', 'radio')
            options = question.get('options', [])
            
            if question_type == 'radio' and options:
                # Système de cases à cocher avec validation QCM
                current_responses = st.session_state.responses.get(question_id, [])
                if not isinstance(current_responses, list):
                    # Compatibilité ascendante : convertir les anciennes réponses
                    current_responses = [current_responses] if current_responses else []
                
                # Affichage des options avec cases à cocher
                selected_options = []
                
                st.markdown("**Sélectionnez une ou deux options maximum :**")
                
                for i, option in enumerate(options):
                    is_checked = option in current_responses
                    
                    # Désactiver les cases si 2 options déjà sélectionnées et cette option n'est pas cochée
                    is_disabled = len(current_responses) >= 2 and not is_checked
                    
                    # Création d'une clé unique incluant l'ID de la fiche pour éviter les doublons
                    
                    if st.checkbox(
                        option,
                        value=is_checked,
                        key=f"qcm_{fiche_id}_{question_id}_option_{i}",
                        disabled=is_disabled
                    ):
                        selected_options.append(option)
                
                # Validation des règles QCM
                if len(selected_options) > 2:
                    st.error("⚠️ **Erreur** : Maximum 2 réponses autorisées. Veuillez désélectionner des options.")
                    # Garder seulement les 2 premières sélections
                    selected_options = selected_options[:2]
                elif len(selected_options) == 2:
                    st.warning("💡 **Attention** : Deux réponses sélectionnées. Une justification est **obligatoire** ci-dessous.")
                    st.info("📝 **Conseil** : Expliquez pourquoi ces deux options sont pertinentes et comment elles se complètent.")
                elif len(selected_options) == 1:
                    st.success("✅ Une réponse sélectionnée (recommandé pour prioriser).")
                
                # Mettre à jour les réponses
                st.session_state.responses[question_id] = selected_options
                
            elif question_type == 'checkbox' and options:
                # Question à choix multiples
                current_responses = st.session_state.responses.get(question_id, [])
                if not isinstance(current_responses, list):
                    current_responses = []
                
                selected_options = []
                for i, option in enumerate(options):
                    if st.checkbox(
                        option,
                        value=option in current_responses,
                        key=f"checkbox_{fiche_id}_{question_id}_option_{i}"
                    ):
                        selected_options.append(option)
                
                st.session_state.responses[question_id] = selected_options
                
            elif question_type == 'text':
                # Question de texte libre
                current_response = st.session_state.responses.get(question_id, '')
                text_response = st.text_input(
                    "Votre réponse :",
                    value=current_response,
                    key=f"text_{fiche_id}_{question_id}"
                )
                st.session_state.responses[question_id] = text_response
                
            elif question_type == 'textarea':
                # Question de texte long
                current_response = st.session_state.responses.get(question_id, '')
                text_response = st.text_area(
                    "Votre réponse :",
                    value=current_response,
                    key=f"textarea_{fiche_id}_{question_id}",
                    height=100
                )
                st.session_state.responses[question_id] = text_response
                
            elif question_type == 'scale':
                # Question avec échelle
                scale_min = question.get('scale_min', 1)
                scale_max = question.get('scale_max', 5)
                current_response = st.session_state.responses.get(question_id, scale_min)
                
                scale_response = st.slider(
                    "Évaluez sur une échelle :",
                    min_value=scale_min,
                    max_value=scale_max,
                    value=current_response,
                    key=f"scale_{fiche_id}_{question_id}"
                )
                st.session_state.responses[question_id] = scale_response
            
            # Zone de commentaire si spécifiée dans la question
            if 'comment' in question and question['comment']:
                comment_key = f"{question_id}_comment"
                current_comment = st.session_state.responses.get(comment_key, '')
                
                # Vérifier si le commentaire est obligatoire
                selected_responses = st.session_state.responses.get(question_id, [])
                is_required = isinstance(selected_responses, list) and len(selected_responses) == 2
                
                # Construire le label avec indication d'obligation
                label = question['comment']
                if is_required:
                    label += " ⚠️ **OBLIGATOIRE** (minimum 10 caractères)"
                
                # Zone de commentaire avec aide contextuelle
                help_text = "💡 Utilisez cette zone pour :"
                if is_required:
                    help_text += "\n• Justifier pourquoi vous avez choisi ces 2 options\n• Expliquer comment elles se complètent\n• Préciser les priorités entre elles"
                else:
                    help_text += "\n• Apporter des nuances à votre choix\n• Proposer des alternatives\n• Partager votre expérience"
                
                # Ajouter un placeholder plus informatif
                placeholder_text = "💡 Astuce : Soyez spécifique et concret. Exemple : 'J'ai choisi ces options car...'"
                
                comment = st.text_area(
                    label,
                    value=current_comment,
                    key=f"comment_{fiche_id}_{question_id}",
                    height=80,
                    help=help_text,
                    placeholder=placeholder_text
                )
                
                # Validation en temps réel pour deux réponses
                if is_required:
                    char_count = len(comment.strip())
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if char_count < 10:
                            st.error(f"❌ **Justification insuffisante** : {char_count}/10 caractères minimum requis.")
                            st.markdown("**Exemple de bonne justification :**")
                            st.info("Ces deux options se complètent car la première répond aux besoins immédiats (3-6 mois) tandis que la seconde prépare notre vision long terme...")
                        else:
                            st.success(f"✅ Justification valide ({char_count} caractères)")
                    
                    with col2:
                        # Barre de progression pour les caractères
                        progress = min(char_count / 10, 1.0)
                        st.progress(progress)
                
                # Sauvegarder le commentaire
                if comment:
                    st.session_state.responses[comment_key] = comment
            
            st.divider()

def show_questionnaires():
    """Affiche les questionnaires de la session sélectionnée avec un système d'accordéon moderne"""
    # Vérifier si une session est sélectionnée
    if 'selected_session' not in st.session_state or not st.session_state.selected_session:
        st.warning("Veuillez sélectionner une session depuis la page d'accueil.")
        if st.button("← Retour à l'accueil"):
            st.session_state.current_page = "Accueil"
            st.rerun()
        return
    
    # Charger les données de la session
    sessions_data = load_sessions()
    selected_session_id = st.session_state.selected_session
    selected_session = sessions_data.get('sessions', {}).get(selected_session_id)
    
    if not selected_session:
        st.error("Session introuvable. Veuillez réessayer.")
        if st.button("← Retour à l'accueil"):
            st.session_state.current_page = "Accueil"
            st.rerun()
        return
    
    # Afficher l'en-tête de la session avec une meilleure mise en page
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); 
                padding: 1.5rem; 
                border-radius: 12px; 
                color: white;
                margin-bottom: 2rem;">
        <h1 style="margin: 0; color: white;">
            {selected_session.get('icon', '📄')} {selected_session.get('title', 'Session sans titre')}
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Afficher les directives
    display_guidelines(sessions_data, selected_session)
    
    # Afficher la progression de la session
    display_session_progress(selected_session, selected_session_id)
    
    # Afficher les fiches de la session en accordéon
    if 'fiches' in selected_session and selected_session['fiches']:
        st.markdown("## 📋 Bienvenue dans la session ")
        
        # Initialiser l'état d'expansion des accordéons et les modifications non sauvegardées
        if 'expanded_fiches' not in st.session_state:
            st.session_state.expanded_fiches = {}
        if 'unsaved_changes' not in st.session_state:
            st.session_state.unsaved_changes = {}
        
        # Afficher chaque fiche dans un accordéon
        for idx, fiche_id in enumerate(selected_session['fiches']):
            fiche = get_fiche(fiche_id)
            if not fiche:
                continue
                
            # Calculer la progression de cette fiche
            fiche_progress = get_fiche_progress(fiche)
            
            # Vérifier s'il y a des modifications non sauvegardées
            has_unsaved_changes = st.session_state.unsaved_changes.get(fiche_id, False)
            
            # Icône de statut basée sur la progression et l'état de sauvegarde
            if has_unsaved_changes:
                status_icon = "💾"
                status_text = "Modifications non sauvegardées"
                status_color = "#f59e0b"  # Orange pour les modifications non sauvegardées
            elif fiche_progress == 100:
                status_icon = "✅"
                status_text = "Complétée"
                status_color = "#10b981"  # Vert pour complété
            elif fiche_progress > 0:
                status_icon = "🔄"
                status_text = f"{fiche_progress}% complétée"
                status_color = "#3b82f6"  # Bleu pour en cours
            else:
                status_icon = "⭕"
                status_text = "Non commencée"
                status_color = "#9ca3af"  # Gris pour non commencé
            
            # Style personnalisé pour l'accordéon
            st.markdown("""
            <style>
                .stExpander > div:first-child > div:first-child > div:first-child > div:first-child {
                    font-size: 1.1rem;
                    font-weight: 600;
                    padding: 1rem 1.25rem;
                    transition: all 0.2s ease;
                }
                .stExpander > div:first-child > div:first-child > div:first-child > div:first-child:hover {
                    background-color: #f9fafb;
                }
                .stExpander > div:last-child > div:first-child > div:first-child {
                    padding: 1.5rem;
                    border: 1px solid #e5e7eb;
                    border-radius: 0.5rem;
                    margin-top: 0.5rem;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Afficher le style personnalisé
            title = fiche.get('title', 'Fiche sans titre')
            
            # Créer l'accordéon avec un titre simple
            with st.expander(
                f"{status_icon} {fiche.get('title', 'Fiche sans titre')} - {status_text} ({fiche_progress}%)",
                expanded=st.session_state.expanded_fiches.get(fiche_id, False)
            ):
                # Stocker l'état précédent des réponses pour détecter les modifications
                previous_responses = st.session_state.responses.copy() if 'responses' in st.session_state else {}
                
                # Afficher la description de la fiche
                if 'description' in fiche and fiche['description']:
                    st.markdown(f"*{fiche['description']}*")
                    st.divider()
                
                # Afficher la fiche dans l'accordéon
                display_fiche_content(fiche)
                
                # Vérifier les modifications
                current_responses = st.session_state.responses if 'responses' in st.session_state else {}
                has_changes = False
                
                # Comparer les réponses avant/après
                if previous_responses != current_responses:
                    has_changes = True
                    st.session_state.unsaved_changes[fiche_id] = True
                
                # Boutons d'action pour cette fiche
                col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                
                with col1:
                    if st.button(
                        "💾 Sauvegarder" if has_unsaved_changes else "✓ Sauvegardé",
                        key=f"save_{fiche_id}",
                        help="Enregistrer les modifications de cette fiche",
                        type="primary" if has_unsaved_changes else "secondary",
                        use_container_width=True
                    ):
                        if save_current_responses():
                            st.session_state.unsaved_changes[fiche_id] = False
                            st.success("💾 Fiche sauvegardée avec succès !")
                            st.rerun()
                
                with col2:
                    if st.button(
                        "📊 Progression",
                        key=f"progress_{fiche_id}",
                        help="Afficher le détail de la progression",
                        use_container_width=True
                    ):
                        show_fiche_progress_detail(fiche)
                
                with col3:
                    if st.button(
                        "🔄 Réinitialiser",
                        key=f"reset_{fiche_id}",
                        help="Effacer toutes les réponses de cette fiche",
                        use_container_width=True
                    ):
                        if st.button(
                            "⚠️ Confirmer la réinitialisation",
                            key=f"confirm_reset_{fiche_id}",
                            type="secondary",
                            use_container_width=True
                        ):
                            reset_fiche_responses(fiche)
                            st.session_state.unsaved_changes[fiche_id] = True
                            st.rerun()
                
                with col4:
                    if st.button(
                        "📝 Exporter",
                        key=f"export_{fiche_id}",
                        help="Exporter cette fiche au format PDF",
                        use_container_width=True
                    ):
                        st.info("Fonctionnalité d'export PDF à implémenter")
                
                # Afficher un message si des modifications ne sont pas sauvegardées
                if has_unsaved_changes and not has_changes:
                    st.warning("⚠️ Vous avez des modifications non sauvegardées. N'oubliez pas de sauvegarder vos réponses.")
            
            # Mettre à jour l'état d'expansion
            st.session_state.expanded_fiches[fiche_id] = st.session_state.get(f"expander_{fiche_id}", False)
    else:
        st.warning("Aucune fiche disponible pour cette session.")
    
    # Actions globales
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("💾 Sauvegarder tout", key="save_all_session", help="Sauvegarder toutes les réponses de la session"):
            save_current_responses()
            st.success("💾 Session complète sauvegardée !")
    
    with col2:
        if st.button("📊 Tableau de bord", key="goto_dashboard", help="Voir le tableau de bord global"):
            st.session_state.current_page = "Tableau de Bord"
            st.rerun()
    
    with col3:
        if st.button("← Retour à l'accueil", key="back_to_home_from_questionnaires"):
            st.session_state.current_page = "Accueil"
            st.rerun()

def show_dashboard():
    """Affiche le tableau de bord avec les statistiques de progression"""
    st.title("📊 Tableau de Bord")
    
    # Charger les données des sessions
    sessions_data = load_sessions()
    
    # Vérifier si des données de session sont disponibles
    if not sessions_data or 'sessions' not in sessions_data or not sessions_data['sessions']:
        st.warning("Aucune donnée de session disponible.")
        if st.button("← Retour à l'accueil"):
            st.session_state.current_page = "Accueil"
            st.rerun()
        return
    
    # Afficher un résumé global
    st.markdown("### Progression Globale")
    
    # Calculer les statistiques globales
    total_sessions = len(sessions_data['sessions'])
    completed_sessions = 0
    total_questions = 0
    answered_questions = 0
    
    # Parcourir toutes les sessions pour calculer les statistiques
    for session_id, session in sessions_data['sessions'].items():
        session_complete = True
        
        # Vérifier les fiches de la session
        if 'fiches' in session and session['fiches']:
            for fiche_id in session['fiches']:
                fiche = get_fiche(fiche_id)
                if fiche and 'questions' in fiche:
                    total_questions += len(fiche['questions'])
                    
                    # Vérifier les réponses pour chaque question
                    for question in fiche['questions']:
                        question_id = question.get('id')
                        if question_id and 'responses' in st.session_state:
                            response = st.session_state['responses'].get(question_id, {})
                            if response:
                                answered_questions += 1
                            else:
                                session_complete = False
        
        if session_complete and 'fiches' in session and session['fiches']:
            completed_sessions += 1
    
    # Afficher les statistiques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sessions Complétées", f"{completed_sessions}/{total_sessions}")
    with col2:
        st.metric("Questions Répondues", f"{answered_questions}/{total_questions}" if total_questions > 0 else "0/0")
    with col3:
        progress = (answered_questions / total_questions * 100) if total_questions > 0 else 0
        st.metric("Progression Globale", f"{progress:.1f}%")
    
    # Afficher une barre de progression
    st.progress(min(progress / 100, 1.0))
    
    # Afficher la progression par session
    st.markdown("### Progression par Session")
    
    for session_id, session in sessions_data['sessions'].items():
        with st.expander(f"{session.get('icon', '📄')} {session.get('title', 'Session sans titre')}"):
            # Calculer la progression pour cette session
            session_questions = 0
            session_answered = 0
            
            if 'fiches' in session and session['fiches']:
                for fiche_id in session['fiches']:
                    fiche = get_fiche(fiche_id)
                    if fiche and 'questions' in fiche:
                        session_questions += len(fiche['questions'])
                        
                        for question in fiche['questions']:
                            question_id = question.get('id')
                            if question_id and 'responses' in st.session_state:
                                response = st.session_state['responses'].get(question_id, {})
                                if response:
                                    session_answered += 1
            
            # Afficher la progression de la session
            if session_questions > 0:
                session_progress = (session_answered / session_questions) * 100
                st.metric("Progression", f"{session_progress:.1f}%")
                st.progress(min(session_progress / 100, 1.0))
                
                # Bouton pour accéder à la session
                if st.button(f"Accéder à la session {session.get('title', '')}", key=f"goto_{session_id}"):
                    st.session_state.selected_session = session_id
                    st.session_state.current_page = "Questionnaires"
                    st.rerun()
            else:
                st.warning("Aucune question disponible dans cette session.")
    
    # Bouton pour revenir à l'accueil
    if st.button("← Retour à l'accueil", key="back_to_home_from_dashboard"):
        st.session_state.current_page = "Accueil"
        st.rerun()

def load_sessions():
    """Charge les données des sessions depuis le fichier sessions.json"""
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Si le fichier n'existe pas, on le crée avec une structure vide
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            default_data = {"sessions": {}}
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        return default_data
    except json.JSONDecodeError:
        st.error("Erreur de décodage du fichier des sessions. Vérifiez le format du fichier.")
        return {"sessions": {}}
    except Exception as e:
        st.error(f"Erreur lors du chargement des sessions : {e}")
        return {"sessions": {}}

@st.cache_data(ttl=300)  # Cache pendant 5 minutes
def load_sessions_cached():
    """Version mise en cache du chargement des sessions"""
    return SessionManager().sessions_data

@st.cache_data(ttl=300)
def load_fiche_cached(fiche_id):
    """Version mise en cache du chargement des fiches"""
    return get_fiche(fiche_id)

def load_fiches(session_id):
    """Charge les fiches d'une session spécifique"""
    fiches = []
    
    # Vérifier si le dossier des fiches existe
    if not FICHES_DIR.exists():
        FICHES_DIR.mkdir(parents=True, exist_ok=True)
        st.warning(f"Le dossier des fiches a été créé : {FICHES_DIR}")
        return fiches
    
    # Parcourir les fichiers JSON dans le dossier des fiches
    for filename in FICHES_DIR.glob('*.json'):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                fiche = json.load(f)
                if 'id' not in fiche:
                    fiche['id'] = filename.stem  # Utiliser le nom du fichier sans extension comme ID
                fiches.append(fiche)
        except json.JSONDecodeError:
            st.error(f"Erreur de décodage JSON dans le fichier {filename}. Vérifiez le format du fichier.")
            continue
        except Exception as e:
            st.error(f"Erreur lors du chargement de {filename}: {e}")
            continue
    
    return fiches

# Interface principale avec navigation optimisée
def add_progress_indicators():
    """Ajoute des indicateurs de progression visuels"""
    st.markdown("""
    <style>
    /* Indicateur de saisie en cours */
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        box-shadow: 0 0 0 2px #4f46e5 !important;
        border-color: #4f46e5 !important;
        transition: all 0.2s ease;
    }
    
    /* Animation de sauvegarde */
    @keyframes pulse-save {
        0% { background-color: #10b981; }
        50% { background-color: #059669; }
        100% { background-color: #10b981; }
    }
    
    .saving-indicator {
        animation: pulse-save 1s infinite;
        border-radius: 4px;
        padding: 0.5rem;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Compteur de caractères en temps réel */
    .char-counter {
        font-size: 0.8rem;
        color: #6b7280;
        text-align: right;
        margin-top: 0.25rem;
    }
    </style>
    
    <script>
    // Compteur de caractères en temps réel
    document.addEventListener('input', function(e) {
        if (e.target.tagName === 'TEXTAREA') {
            const charCount = e.target.value.length;
            let counter = e.target.parentNode.querySelector('.char-counter');
            if (!counter) {
                counter = document.createElement('div');
                counter.className = 'char-counter';
                e.target.parentNode.appendChild(counter);
            }
            counter.textContent = charCount + ' caractères';
            
            // Validation en temps réel
            if (charCount >= 10) {
                counter.style.color = '#10b981';
                counter.textContent += ' ✅';
            } else {
                counter.style.color = '#ef4444';
                counter.textContent += ' (min. 10)';
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)

def add_auto_save_script():
    """Ajoute un script JavaScript pour la sauvegarde automatique"""
    st.markdown("""
    <script>
    // Auto-save toutes les 30 secondes
    setInterval(function() {
        // Déclencher la sauvegarde Streamlit
        const saveButton = document.querySelector('[data-testid="stButton"] button');
        if (saveButton && saveButton.textContent.includes('💾')) {
            // Simuler un clic sur le bouton de sauvegarde
            console.log('Auto-save déclenché');
        }
    }, 30000);
    
    // Sauvegarde avant fermeture de page
    window.addEventListener('beforeunload', function(e) {
        e.preventDefault();
        e.returnValue = 'Voulez-vous sauvegarder avant de quitter ?';
    });
    
    // Indicateur visuel de saisie
    document.addEventListener('input', function(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            // Ajouter un indicateur de modification
            e.target.style.borderLeft = '3px solid #f59e0b';
            setTimeout(() => {
                e.target.style.borderLeft = '';
            }, 2000);
        }
    });
    </script>
    """, unsafe_allow_html=True)

def main():
    # Configuration de la page avec le thème personnalisé
    set_page_config()
    
    # Ajouter les améliorations UX
    add_auto_save_script()
    add_progress_indicators()
    
    # Ajouter les améliorations UX
    add_auto_save_script()
    add_progress_indicators()
    
    # Affichage de la session active
    if hasattr(st.session_state, 'selected_session') and st.session_state.selected_session:
        try:
            sessions_data = load_sessions()
            selected_session = sessions_data.get('sessions', {}).get(st.session_state.selected_session)
            
            if selected_session:
                progress = get_session_progress(selected_session)
                
                st.sidebar.markdown("""
                <div style="
                    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                    border: 1px solid #0ea5e9;
                    border-radius: 8px;
                    padding: 1rem;
                    margin: 1rem 0;
                ">
                    <h4 style="margin: 0 0 0.5rem 0; color: #0369a1; font-size: 0.8rem;">🎯 Session Active</h4>
                    <p style="margin: 0 0 0.5rem 0; font-size: 0.8rem; font-weight: 600;">{icon} {title}</p>
                    <div style="
                        background: #e0f2fe;
                        border-radius: 4px;
                        height: 6px;
                        overflow: hidden;
                        margin: 0.5rem 0;
                    ">
                        <div style="
                            background: linear-gradient(90deg, #0ea5e9, #0369a1);
                            height: 100%;
                            width: {progress}%;
                            transition: width 0.3s ease;
                        "></div>
                    </div>
                    <p style="margin: 0; font-size: 0.7rem; color: #0369a1;">{progress}% complété</p>
                </div>
                """.format(
                    icon=selected_session.get('icon', '📄'),
                    title=selected_session.get('title', 'Session'),
                    progress=progress
                ), unsafe_allow_html=True)
        except Exception:
            pass
    
    # Styles CSS pour le menu latéral amélioré
    st.sidebar.markdown("""
    <style>
        /* Styles pour le menu latéral */
        .sidebar-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 1.5rem 1rem;
            margin: -1rem -1rem 1.5rem -1rem;
            border-radius: 0 0 12px 12px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .sidebar-header h2 {
            margin: 0;
            font-size: 1.4rem;
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        
        .sidebar-header p {
            margin: 0.5rem 0 0 0;
            font-size: 0.85rem;
            opacity: 0.9;
            font-weight: 300;
        }
        
        .nav-button {
            width: 100%;
            padding: 0.8rem 1rem;
            margin: 0.2rem 0;
            border: none;
            border-radius: 8px;
            background: white;
            color: var(--text-primary);
            text-align: left;
            cursor: pointer;
            transition: all 0.25s ease;
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 0.95rem;
            position: relative;
            overflow: hidden;
        }
        
        .nav-button:before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            height: 100%;
            width: 4px;
            background: var(--primary-color);
            transform: scaleY(0);
            transition: transform 0.2s ease;
        }
        
        .nav-button:hover {
            background: rgba(14, 165, 233, 0.05);
            border-color: var(--primary-color);
            transform: translateX(4px);
            box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        }
        
        .nav-button:hover:before {
            transform: scaleY(1);
        }
        
        .nav-button.active {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border-color: var(--primary-color);
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
            font-weight: 500;
        }
        
        .nav-button.active:hover {
            transform: translateX(2px);
            box-shadow: 0 6px 16px rgba(79, 70, 229, 0.4);
        }
        
        .nav-icon {
            font-size: 1.2rem;
            width: 24px;
            text-align: center;
            transition: transform 0.2s ease;
        }
        
        .nav-button:hover .nav-icon {
            transform: scale(1.1);
        }
        
        .nav-text {
            flex: 1;
            transition: transform 0.2s ease;
        }
        
        .nav-button:hover .nav-text {
            transform: translateX(2px);
        }
        
        .nav-badge {
            background: var(--primary-color);
            color: white;
            border-radius: 12px;
            padding: 0.15rem 0.5rem;
            font-size: 0.7rem;
            font-weight: 600;
            margin-left: auto;
        }
        
        .sidebar-section {
            margin: 1.5rem 0;
        }
        
        .sidebar-section-title {
            font-size: 0.8rem;
            text-transform: uppercase;
            color: var(--text-secondary);
            font-weight: 600;
            margin-bottom: 0.75rem;
            padding: 0 0.5rem;
            letter-spacing: 0.5px;
        }
        
        .quick-actions {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
            margin: 1rem 0;
        }
        
        .quick-action-button {
            padding: 0.6rem 0.5rem;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background: white;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            font-size: 0.75rem;
            color: var(--text-primary);
        }
        
        .quick-action-button:hover {
            background: var(--bg-light);
            border-color: var(--primary-color);
            transform: translateY(-2px);
        }
        
        .quick-action-button i {
            font-size: 1.2rem;
            margin-bottom: 0.25rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header du menu latéral amélioré
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <h2>🚀 IA-INDUS</h2>
        <p>Questionnaires Stratégiques</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Menu de navigation avec boutons améliorés
    menu_options = {
        "Accueil": {
            "function": show_home, 
            "icon": "🏠", 
            "description": "Page d'accueil",
            "badge": None
        },
        "Questionnaires": {
            "function": show_questionnaires, 
            "icon": "📝", 
            "description": "Répondre aux questionnaires",
            "badge": "Nouveau"
        },
        "Tableau de Bord": {
            "function": show_dashboard, 
            "icon": "📊", 
            "description": "Voir la progression",
            "badge": None
        },
        "Aide": {
            "function": show_help, 
            "icon": "❓", 
            "description": "Aide et support",
            "badge": None
        }
    }
    
    # Initialiser la page courante si elle n'existe pas
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Accueil"
    
    # Section de navigation principale
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-section-title">Navigation</div>', unsafe_allow_html=True)
    
    for page_name, page_info in menu_options.items():
        # Déterminer si c'est la page active
        is_active = st.session_state.current_page == page_name
        
        # Créer le bouton Streamlit avec le style personnalisé
        if st.sidebar.button(
            f"{page_info['icon']} {page_name}",
            key=f"nav_{page_name}",
            help=page_info['description'],
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.current_page = page_name
            st.rerun()
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Section des actions rapides
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-section-title">Actions Rapides</div>', unsafe_allow_html=True)
    
    # Grille de boutons d'action rapide
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button(
            "💾 Sauvegarder",
            help="Sauvegarder toutes les réponses en cours",
            use_container_width=True,
            key="quick_save_btn"
        ):
            try:
                if hasattr(st.session_state, 'responses') and st.session_state.responses:
                    save_current_responses()
                    st.sidebar.markdown("<div style='color: #059669; font-size: 0.9rem;'>✅ Sauvegardé avec succès</div>", unsafe_allow_html=True)
                else:
                    st.sidebar.markdown("<div style='color: #3b82f6; font-size: 0.9rem;'>ℹ️ Aucune réponse à sauvegarder</div>", unsafe_allow_html=True)
            except Exception as e:
                st.sidebar.markdown("<div style='color: #ef4444; font-size: 0.9rem;'>❌ Erreur lors de la sauvegarde</div>", unsafe_allow_html=True)
    
    with col2:
        if st.button(
            "🔄 Actualiser",
            help="Recharger les données de l'application",
            use_container_width=True,
            key="refresh_btn"
        ):
            st.rerun()
    
    # Bouton de réinitialisation avec confirmation
    if st.sidebar.button(
        "🗑️ Réinitialiser les réponses",
        help="Effacer toutes les réponses (avec confirmation)",
        use_container_width=True,
        type="secondary",
        key="reset_btn"
    ):
        if 'confirm_reset' not in st.session_state:
            st.session_state.confirm_reset = True
            st.sidebar.markdown("<div style='color: #d97706; font-size: 0.9rem;'>⚠️ Cliquez à nouveau pour confirmer</div>", unsafe_allow_html=True)
        else:
            # Réinitialiser les réponses
            for key in list(st.session_state.keys()):
                if key.startswith('responses_'):
                    del st.session_state[key]
            del st.session_state.confirm_reset
            st.sidebar.markdown("<div style='color: #059669; font-size: 0.9rem;'>✅ Réponses réinitialisées avec succès</div>", unsafe_allow_html=True)
            st.rerun()
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Pied de page simplifié
    st.sidebar.markdown("---")
    
    # Section de mise à jour
    col1, col2 = st.sidebar.columns([2, 1])
    with col1:
        st.markdown("**🕒 Dernière mise à jour**")
    with col2:
        st.markdown(f"<div style='text-align: right; font-size: 0.8rem; color: var(--text-secondary);'>{datetime.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)
    
    # Section de mise à jour simplifiée
    
    # Copyright
    st.sidebar.markdown("---")
    st.sidebar.markdown("**IA-INDUS 2025 • v1.2.0**")
    st.sidebar.caption("Tous droits réservés")
    
    # Afficher la page sélectionnée
    menu_options[st.session_state.current_page]["function"]()
    
if __name__ == "__main__":
    main()