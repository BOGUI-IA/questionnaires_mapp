import json
import os
import logging
import sys
from pathlib import Path
from datetime import datetime
import shutil
from typing import List, Dict, Any, Optional

# Configuration de la journalisation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('update_fiches.log')
    ]
)
logger = logging.getLogger(__name__)

# Chemin par défaut (peut être surchargé par une variable d'environnement)
DEFAULT_FICHES_DIR = Path("d:/Projects/01-ACTIVE-PROJECTS/questionnaires_mapp/data/fiches")

def create_backup(fiches_dir: Path) -> Path:
    """
    Crée une sauvegarde du dossier fiches
    
    Args:
        fiche_dir: Chemin vers le dossier des fiches à sauvegarder
        
    Returns:
        Path: Chemin du dossier de sauvegarde créé
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path(f"fiches_backup_{timestamp}")
        
        if not backup_dir.exists():
            logger.info(f"Création de la sauvegarde dans {backup_dir}")
            shutil.copytree(fiches_dir, backup_dir)
            logger.info(f"Sauvegarde réussie : {backup_dir}")
        else:
            logger.warning(f"Le dossier de sauvegarde existe déjà : {backup_dir}")
            
        return backup_dir
    except Exception as e:
        logger.error(f"Erreur lors de la création de la sauvegarde : {e}", exc_info=True)
        raise

def update_fiche(fiche_path: Path) -> bool:
    """
    Met à jour une fiche selon les spécifications
    
    Args:
        fiche_path: Chemin vers le fichier de la fiche à mettre à jour
        
    Returns:
        bool: True si des modifications ont été apportées, False sinon
    """
    try:
        logger.debug(f"Traitement du fichier : {fiche_path}")
        
        with open(fiche_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        questions = data.get('questions', [])
        
        if not questions:
            logger.warning(f"Aucune question trouvée dans {fiche_path.name}")
            return False
        
        # Parcourir toutes les questions
        for idx, question in enumerate(questions, 1):
            # 1. Changer le type de 'radio' à 'checkbox' si nécessaire
            if question.get('type') == 'radio':
                question['type'] = 'checkbox'
                modified = True
                logger.debug(f"Question {idx}: Type changé en 'checkbox'")
            
            # 2. Ajouter l'option E si elle n'existe pas déjà
            if 'options' in question and isinstance(question['options'], list):
                option_e_exists = any(
                    isinstance(opt, str) and 
                    ('(E)' in opt or '(E) ' in opt) 
                    for opt in question['options']
                )
                if not option_e_exists:
                    question['options'].append("(E) Autre (à préciser dans les commentaires)")
                    modified = True
                    logger.debug(f"Question {idx}: Option E ajoutée")
            
            # 3. Mettre à jour le texte du commentaire
            expected_comment = "Précisions/Commentaires (obligatoire si Option E ou choix multiples) :"
            if 'comment' in question and question['comment'] != expected_comment:
                question['comment'] = expected_comment
                modified = True
                logger.debug(f"Question {idx}: Texte de commentaire mis à jour")
        
        # Sauvegarder si des modifications ont été apportées
        if modified:
            # Créer une sauvegarde du fichier avant modification
            backup_file = fiche_path.with_suffix(f'.{datetime.now().strftime("%Y%m%d_%H%M%S")}.bak')
            shutil.copy2(fiche_path, backup_file)
            logger.debug(f"Sauvegarde du fichier original : {backup_file}")
            
            # Écrire les modifications
            with open(fiche_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, ensure_ascii=False)
            
            logger.info(f"Fiche mise à jour avec succès : {fiche_path.name}")
        else:
            logger.debug(f"Aucune modification nécessaire pour : {fiche_path.name}")
            
        return modified
        
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de décodage JSON dans {fiche_path.name}: {e}", exc_info=True)
        return False
    except PermissionError as e:
        logger.error(f"Erreur de permission sur le fichier {fiche_path.name}: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue avec {fiche_path.name}: {e}", exc_info=True)
        return False

def get_fiches_dir() -> Path:
    """
    Récupère le chemin du dossier des fiches depuis la variable d'environnement
    ou utilise le chemin par défaut.
    """
    fiches_dir = os.environ.get("FICHES_DIR")
    if fiches_dir:
        return Path(fiches_dir)
    return DEFAULT_FICHES_DIR

def main():
    """Fonction principale du script de mise à jour des fiches."""
    try:
        # Configuration du niveau de log
        if "--debug" in sys.argv:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        
        logger.info("Démarrage du script de mise à jour des fiches")
        
        # Récupérer le dossier des fiches
        fiches_dir = get_fiches_dir()
        logger.info(f"Dossier des fiches : {fiches_dir}")
        
        if not fiches_dir.exists() or not fiches_dir.is_dir():
            logger.error(f"Le dossier {fiches_dir} n'existe pas ou n'est pas un dossier valide")
            return 1
        
        # Rechercher les fichiers de fiches
        logger.info("Recherche des fichiers de fiches...")
        fiche_files = list(fiches_dir.glob('*.json'))
        
        if not fiche_files:
            logger.warning("Aucun fichier de fiche trouvé")
            return 0
        
        logger.info(f"{len(fiche_files)} fiches trouvées")
        
        # Créer une sauvegarde complète du dossier
        logger.info("Création d'une sauvegarde du dossier fiches...")
        backup_dir = create_backup(fiches_dir)
        
        # Traiter chaque fiche
        logger.info("Début de la mise à jour des fiches...")
        logger.info("=" * 60)
        
        updated_count = 0
        
        for fiche_file in sorted(fiche_files):
            logger.info(f"Traitement de : {fiche_file.name}")
            logger.debug("-" * 40)
            
            if update_fiche(fiche_file):
                updated_count += 1
        
        # Afficher le résumé
        logger.info("=" * 60)
        logger.info("Mise à jour terminée")
        logger.info(f"{updated_count}/{len(fiche_files)} fiches mises à jour")
        logger.info(f"Sauvegarde disponible dans : {backup_dir}")
        logger.info("=" * 60)
        
        return 0 if updated_count == len(fiche_files) else 2
        
    except Exception as e:
        logger.critical(f"Erreur critique dans la fonction main : {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\nInterruption par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"Erreur inattendue : {e}", exc_info=True)
        sys.exit(1)
