import json
import os
import sys
from pathlib import Path
from datetime import datetime
import shutil
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('fiches_update.log')
    ]
)
logger = logging.getLogger(__name__)

def create_backup(fiches_dir):
    """Crée une sauvegarde du dossier fiches"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path(f"fiches_backup_{timestamp}")
    
    if not backup_dir.exists():
        shutil.copytree(fiches_dir, backup_dir)
        print(f"✅ Sauvegarde créée : {backup_dir}")
    return backup_dir

def update_fiche(fiche_path):
    """Met à jour une fiche selon les spécifications"""
    logger.info(f"Traitement du fichier: {fiche_path}")
    
    try:
        # Vérifier si le fichier existe et est accessible en lecture/écriture
        if not fiche_path.exists():
            logger.error(f"Le fichier {fiche_path} n'existe pas")
            return False
            
        if not os.access(fiche_path, os.R_OK | os.W_OK):
            logger.error(f"Permissions insuffisantes pour lire/écrire dans {fiche_path}")
            return False
        
        # Lire le contenu du fichier
        with open(fiche_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                logger.debug("Fichier JSON chargé avec succès")
            except json.JSONDecodeError as e:
                logger.error(f"Erreur de décodage JSON: {e}")
                return False
        
        modified = False
        
        # Vérifier si le fichier a la structure attendue
        if 'questions' not in data:
            logger.warning(f"Aucune section 'questions' trouvée dans {fiche_path.name}")
            return False
        
        # Parcourir toutes les questions
        for i, question in enumerate(data.get('questions', [])):
            logger.debug(f"Traitement de la question {i+1}")
            
            # 1. Changer le type de 'radio' à 'checkbox' si nécessaire
            current_type = question.get('type')
            if current_type == 'radio':
                question['type'] = 'checkbox'
                modified = True
                logger.info(f"  🔄 Question {i+1}: Type changé de 'radio' à 'checkbox'")
            
            # 2. Ajouter l'option E si elle n'existe pas déjà
            if 'options' in question and isinstance(question['options'], list):
                option_e_exists = any(opt.strip().startswith('(E)') for opt in question['options'] if isinstance(opt, str))
                if not option_e_exists:
                    question['options'].append("(E) Autre (à préciser dans les commentaires)")
                    modified = True
                    logger.info(f"  ➕ Question {i+1}: Option E ajoutée")
            
            # 3. Mettre à jour le texte du commentaire
            current_comment = question.get('comment', '')
            new_comment = "Précisions/Commentaires (obligatoire si Option E ou choix multiples) :"
            if 'comment' in question and current_comment != new_comment:
                question['comment'] = new_comment
                modified = True
                logger.info(f"  📝 Question {i+1}: Texte de commentaire mis à jour")
        
        # Sauvegarder si des modifications ont été apportées
        if modified:
            try:
                # Créer une sauvegarde temporaire
                temp_path = fiche_path.with_suffix('.tmp')
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Remplacer le fichier original
                backup_path = fiche_path.with_suffix('.bak')
                if fiche_path.exists():
                    shutil.copy2(fiche_path, backup_path)
                
                shutil.move(temp_path, fiche_path)
                
                # Vérifier que le fichier a bien été écrit
                if os.path.getsize(fiche_path) > 0:
                    logger.info(f"✅ {fiche_path.name} : Mis à jour avec succès")
                    # Supprimer la sauvegarde si tout s'est bien passé
                    if backup_path.exists():
                        os.remove(backup_path)
                else:
                    logger.error(f"❌ {fiche_path.name} : Échec de l'écriture (fichier vide)")
                    # Restaurer la sauvegarde en cas d'échec
                    if backup_path.exists():
                        shutil.move(backup_path, fiche_path)
                        
            except Exception as e:
                logger.error(f"❌ Erreur lors de la sauvegarde de {fiche_path.name}: {e}")
                # Restaurer la sauvegarde en cas d'erreur
                if 'backup_path' in locals() and backup_path.exists():
                    shutil.move(backup_path, fiche_path)
                return False
        else:
            logger.info(f"ℹ️  {fiche_path.name} : Aucune modification nécessaire")
            
        return modified
        
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de décodage JSON dans {fiche_path.name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur avec {fiche_path.name}: {e}")
        return False

def main():
    # Vérifier les arguments de ligne de commande
    test_mode = '--test' in sys.argv
    
    # Chemin vers le dossier des fiches
    fiches_dir = Path("d:/Projects/01-ACTIVE-PROJECTS/questionnaires_mapp/data/fiches")
    
    # Vérifier que le dossier existe
    if not fiches_dir.exists():
        logger.error(f"❌ Le dossier {fiches_dir} n'existe pas")
        return 1
    
    # Vérifier les permissions
    if not os.access(fiches_dir, os.R_OK | os.W_OK):
        logger.error(f"❌ Permissions insuffisantes pour accéder à {fiches_dir}")
        return 1
    
    logger.info("🔍 Recherche des fichiers de fiches...")
    fiche_files = list(fiches_dir.glob('*.json'))
    
    if not fiche_files:
        logger.warning("ℹ️  Aucun fichier de fiche trouvé")
        return 0
    
    logger.info(f"📋 {len(fiche_files)} fiches trouvées")
    
    # Mode test : ne pas modifier les fichiers
    if test_mode:
        logger.warning("⚠️  MODE TEST - Aucune modification ne sera apportée aux fichiers")
        
        # Tester avec le premier fichier
        test_file = fiche_files[0]
        logger.info(f"\n🔍 Test avec le fichier : {test_file.name}")
        logger.info("-" * 60)
        
        # Afficher le contenu avant modification
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info("=== CONTENU AVANT MODIFICATION ===")
                logger.info(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Simuler les modifications
                modified_data = data.copy()
                modified = False
                
                for i, question in enumerate(modified_data.get('questions', [])):
                    # 1. Vérifier le type
                    if question.get('type') == 'radio':
                        logger.info(f"  🔄 Question {i+1}: Type sera changé de 'radio' à 'checkbox'")
                        modified = True
                    
                    # 2. Vérifier l'option E
                    if 'options' in question and isinstance(question['options'], list):
                        option_e_exists = any(opt.strip().startswith('(E)') for opt in question['options'] if isinstance(opt, str))
                        if not option_e_exists:
                            logger.info(f"  ➕ Question {i+1}: Option E sera ajoutée")
                            modified = True
                    
                    # 3. Vérifier le commentaire
                    current_comment = question.get('comment', '')
                    new_comment = "Précisions/Commentaires (obligatoire si Option E ou choix multiples) :"
                    if current_comment != new_comment:
                        logger.info(f"  📝 Question {i+1}: Le commentaire sera mis à jour")
                        modified = True
                
                if not modified:
                    logger.info("ℹ️  Aucune modification nécessaire pour ce fichier")
                
                logger.info("\n=== FIN DU MODE TEST ===")
                logger.info("Pour appliquer les modifications, exécutez le script sans l'option --test")
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la lecture du fichier de test: {e}")
            return 1
            
        return 0
    
    # Mode normal : créer une sauvegarde complète
    logger.info("\n⚠️  Création d'une sauvegarde complète du dossier fiches...")
    try:
        backup_dir = create_backup(fiches_dir)
        logger.info(f"✅ Sauvegarde créée : {backup_dir}")
    except Exception as e:
        logger.error(f"❌ Échec de la création de la sauvegarde: {e}")
        return 1
    
    logger.info("\n🔄 Début de la mise à jour des fiches...")
    logger.info("=" * 60)
    
    updated_count = 0
    
    # Traiter les fichiers un par un
    for fiche_file in sorted(fiche_files):
        logger.info(f"\n📄 Traitement de : {fiche_file.name}")
        logger.info("-" * 40)
        
        if update_fiche(fiche_file):
            updated_count += 1
    
    # Résumé
    logger.info("\n" + "=" * 60)
    logger.info("✅ Mise à jour terminée")
    logger.info(f"📊 {updated_count}/{len(fiche_files)} fiches mises à jour")
    logger.info(f"💾 Sauvegarde disponible dans : {backup_dir}")
    logger.info("=" * 60)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.warning("\nOpération annulée par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Erreur inattendue: {e}", exc_info=True)
        sys.exit(1)