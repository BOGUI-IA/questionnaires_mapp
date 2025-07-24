import os
import shutil
import json
from datetime import datetime
from pathlib import Path
import zipfile
import hashlib
from typing import List, Dict, Optional
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backup.log')
    ]
)
logger = logging.getLogger(__name__)

class ProjectBackup:
    def __init__(self, project_path: str, backup_dir: str = 'backups'):
        """
        Initialise le système de sauvegarde
        
        Args:
            project_path: Chemin du projet à sauvegarder
            backup_dir: Dossier où stocker les sauvegardes
        """
        self.project_path = Path(project_path).resolve()
        self.backup_dir = Path(backup_dir).resolve()
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.backup_dir / 'backup_config.json'
        self.config = self._load_config()
        
        # Dossiers à exclure par défaut
        self.default_excludes = [
            '__pycache__',
            '.git',
            '.venv',
            'venv',
            'env',
            'node_modules',
            '.idea',
            '.vscode',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.Python',
            'env.bak/',
            'venv.bak/'
        ]
        
        # Fichiers à exclure par défaut
        self.default_file_excludes = [
            '*.log',
            '*.tmp',
            '*.temp',
            '*.swp',
            '*.swo',
            '*~',
            '.DS_Store',
            'Thumbs.db'
        ]
    
    def _load_config(self) -> Dict:
        """Charge la configuration des sauvegardes"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erreur lors du chargement de la configuration: {e}")
        
        # Configuration par défaut
        return {
            'version': 1,
            'last_backup': None,
            'backups': [],
            'excludes': [],
            'file_excludes': [],
            'max_backups': 10
        }
    
    def _save_config(self):
        """Sauvegarde la configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la configuration: {e}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Calcule le hash d'un fichier"""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(65536):  # 64kb chunks
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Erreur lors du calcul du hash pour {file_path}: {e}")
            return ""
    
    def _should_exclude(self, path: Path, is_dir: bool = False) -> bool:
        """Détermine si un fichier/dossier doit être exclu"""
        rel_path = str(path.relative_to(self.project_path))
        
        # Vérifier les exclusions par défaut
        for pattern in self.default_excludes + self.config.get('excludes', []):
            if is_dir and pattern.endswith('/') and path.match(pattern[:-1]):
                return True
            if path.match(pattern):
                return True
        
        # Vérifier les exclusions de fichiers
        if not is_dir:
            for pattern in self.default_file_excludes + self.config.get('file_excludes', []):
                if path.match(pattern):
                    return True
        
        return False
    
    def create_backup(self, comment: str = "") -> Optional[Path]:
        """
        Crée une nouvelle sauvegarde du projet
        
        Args:
            comment: Commentaire optionnel pour la sauvegarde
            
        Returns:
            Chemin vers le fichier de sauvegarde créé ou None en cas d'échec
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}"
        backup_path = self.backup_dir / f"{backup_name}.zip"
        
        try:
            # Créer une archive ZIP
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Parcourir tous les fichiers du projet
                for root, dirs, files in os.walk(self.project_path):
                    root_path = Path(root)
                    
                    # Filtrer les dossiers à exclure
                    dirs[:] = [d for d in dirs 
                              if not self._should_exclude(root_path / d, is_dir=True)]
                    
                    # Ajouter les fichiers à l'archive
                    for file in files:
                        file_path = root_path / file
                        rel_path = file_path.relative_to(self.project_path)
                        
                        if not self._should_exclude(file_path):
                            try:
                                zipf.write(file_path, rel_path)
                            except Exception as e:
                                logger.error(f"Erreur lors de l'ajout de {file_path} à l'archive: {e}")
            
            # Mettre à jour la configuration
            backup_info = {
                'name': backup_name,
                'path': str(backup_path.relative_to(self.backup_dir)),
                'timestamp': datetime.now().isoformat(),
                'size_mb': round(backup_path.stat().st_size / (1024 * 1024), 2),
                'comment': comment,
                'project_version': self._get_project_version()
            }
            
            self.config['last_backup'] = backup_info
            self.config['backups'].append(backup_info)
            
            # Limiter le nombre de sauvegardes conservées
            max_backups = self.config.get('max_backups', 10)
            while len(self.config['backups']) > max_backups:
                oldest = self.config['backups'].pop(0)
                try:
                    os.remove(self.backup_dir / oldest['path'])
                    logger.info(f"Ancienne sauvegarde supprimée: {oldest['name']}")
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression de {oldest['path']}: {e}")
            
            self._save_config()
            logger.info(f"Sauvegarde créée avec succès: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
            if backup_path.exists():
                try:
                    backup_path.unlink()
                except:
                    pass
            return None
    
    def _get_project_version(self) -> str:
        """Récupère la version du projet (à personnaliser selon votre projet)"""
        # Exemple: lire depuis un fichier de version
        version_file = self.project_path / 'VERSION'
        if version_file.exists():
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except:
                pass
        
        # Sinon, utiliser git si disponible
        if (self.project_path / '.git').exists():
            try:
                import subprocess
                result = subprocess.run(
                    ['git', 'describe', '--tags', '--always'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except:
                pass
        
        # Par défaut, utiliser la date
        return f"unversioned-{datetime.now().strftime('%Y%m%d')}"
    
    def list_backups(self) -> List[Dict]:
        """Liste toutes les sauvegardes disponibles"""
        return self.config.get('backups', [])
    
    def restore_backup(self, backup_name: str, target_dir: str = None) -> bool:
        """
        Restaure une sauvegarde de manière sécurisée
            
        Args:
            backup_name: Nom de la sauvegarde à restaurer
            target_dir: Dossier cible pour la restauration (par défaut: emplacement d'origine)
                
        Returns:
            True si la restauration a réussi, False sinon
        """
        # Trouver la sauvegarde
        backup = next((b for b in self.config.get('backups', []) 
                      if b['name'] == backup_name), None)
        
        if not backup:
            logger.error(f"Sauvegarde introuvable: {backup_name}")
            return False
                
        backup_path = self.backup_dir / backup['path']
            
        if not backup_path.exists():
            logger.error(f"Fichier de sauvegarde introuvable: {backup_path}")
            return False
                
        # Déterminer le dossier cible
        target_path = Path(target_dir) if target_dir else self.project_path
        temp_restore_dir = target_path.parent / f"{target_path.name}_temp_restore"
        backup_old = target_path.parent / f"{target_path.name}_old_{int(datetime.now().timestamp())}"
        
        try:
            logger.info(f"Début de la restauration de la sauvegarde: {backup_name}")
                
            # Étape 1: Créer un dossier temporaire pour l'extraction
            if temp_restore_dir.exists():
                shutil.rmtree(temp_restore_dir)
            temp_restore_dir.mkdir(parents=True)
            logger.debug(f"Dossier temporaire créé: {temp_restore_dir}")
                
            # Étape 2: Extraire l'archive dans le dossier temporaire
            logger.info(f"Extraction de l'archive: {backup_path}")
            with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                zip_ref.extractall(temp_restore_dir)
                
            # Étape 3: Vérifier l'intégrité de l'extraction
            extracted_items = list(temp_restore_dir.glob('*'))
            if not extracted_items:
                raise ValueError("L'archive est vide ou corrompue")
                    
            extracted_dir = extracted_items[0]
            if not extracted_dir.is_dir():
                raise ValueError("La structure de l'archive est invalide")
                    
            # Étape 4: Vérifier les fichiers essentiels (ajuster selon votre projet)
            required_files = ['app.py', 'requirements.txt']
            for req_file in required_files:
                if not (extracted_dir / req_file).exists():
                    logger.warning(f"Fichier requis non trouvé: {req_file}")
                
            logger.info("Vérification de l'intégrité terminée avec succès")
                
            # Étape 5: Sauvegarder l'ancien dossier s'il existe
            if target_path.exists():
                logger.info(f"Sauvegarde de l'ancien projet dans: {backup_old}")
                shutil.move(str(target_path), str(backup_old))
                
            # Étape 6: Déplacer le contenu extrait vers la destination finale
            logger.info(f"Déploiement de la sauvegarde vers: {target_path}")
            shutil.move(str(extracted_dir), str(target_path))
                
            # Étape 7: Nettoyer
            shutil.rmtree(temp_restore_dir, ignore_errors=True)
                
            logger.info(f"✅ Restauration terminée avec succès depuis: {backup_name}")
                
            # Supprimer la sauvegarde de l'ancien projet après un délai (optionnel)
            # import time
            # time.sleep(60)  # Attendre 1 minute avant de supprimer
            # shutil.rmtree(backup_old, ignore_errors=True)
                
            return True
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la restauration: {e}")
                
            # En cas d'erreur, restaurer l'ancien projet s'il existe
            if 'backup_old' in locals() and backup_old.exists():
                try:
                    if target_path.exists():
                        shutil.rmtree(target_path, ignore_errors=True)
                    shutil.move(str(backup_old), str(target_path))
                    logger.info("Ancien projet restauré suite à une erreur")
                except Exception as restore_error:
                    logger.error(f"Erreur lors de la restauration de l'ancien projet: {restore_error}")
                
            # Nettoyer
            shutil.rmtree(temp_restore_dir, ignore_errors=True)
                
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Système de sauvegarde avec versionnement")
    subparsers = parser.add_subparsers(dest='command', help='Commande à exécuter')
    
    # Commande: create
    create_parser = subparsers.add_parser('create', help='Créer une nouvelle sauvegarde')
    create_parser.add_argument('-c', '--comment', default='', help='Commentaire pour la sauvegarde')
    
    # Commande: list
    list_parser = subparsers.add_parser('list', help='Lister les sauvegardes disponibles')
    
    # Commande: restore
    restore_parser = subparsers.add_parser('restore', help='Restaurer une sauvegarde')
    restore_parser.add_argument('backup_name', help='Nom de la sauvegarde à restaurer')
    restore_parser.add_argument('-t', '--target', help='Dossier cible pour la restauration')
    
    args = parser.parse_args()
    
    # Initialiser le système de sauvegarde
    backup = ProjectBackup('.')
    
    if args.command == 'create':
        print(f"Création d'une nouvelle sauvegarde...")
        backup_path = backup.create_backup(args.comment)
        if backup_path:
            print(f"✅ Sauvegarde créée avec succès: {backup_path}")
        else:
            print("❌ Échec de la création de la sauvegarde")
    
    elif args.command == 'list':
        print("\nSauvegardes disponibles:")
        print("-" * 80)
        for i, b in enumerate(backup.list_backups()):
            print(f"{i+1}. {b['name']}")
            print(f"   Date: {b['timestamp']}")
            print(f"   Taille: {b['size_mb']} Mo")
            if b.get('comment'):
                print(f"   Commentaire: {b['comment']}")
            if b.get('project_version'):
                print(f"   Version: {b['project_version']}")
            print("-" * 80)
    
    elif args.command == 'restore':
        print(f"Restauration de la sauvegarde: {args.backup_name}")
        if backup.restore_backup(args.backup_name, args.target):
            print("✅ Restauration terminée avec succès")
        else:
            print("❌ Échec de la restauration")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
