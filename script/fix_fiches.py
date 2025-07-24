import json
import os
from pathlib import Path
from datetime import datetime

def fix_fiches(fiches_dir):
    """Corrige les fiches JSON pour s'assurer qu'elles ont tous les champs requis"""
    fiches_path = Path(fiches_dir)
    fixed_count = 0
    
    print(f"🔧 Correction des fiches dans : {fiches_path}")
    print("=" * 50)
    
    for fiche_file in fiches_path.glob('*.json'):
        try:
            with open(fiche_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            modified = False
            
            # Vérifier et corriger les champs requis
            if 'id' not in data:
                data['id'] = fiche_file.stem
                modified = True
                print(f"  ➕ Ajout du champ 'id': {data['id']}")
            
            if 'title' not in data:
                # Générer un titre basé sur le nom du fichier
                title = fiche_file.stem.replace('fiche_', 'Fiche ').replace('_', ' ').title()
                data['title'] = title
                modified = True
                print(f"  ➕ Ajout du champ 'title': {title}")
            
            if 'description' not in data:
                data['description'] = f"Description pour {data.get('title', fiche_file.stem)}"
                modified = True
                print(f"  ➕ Ajout du champ 'description'")
            
            if 'questions' not in data:
                data['questions'] = []
                modified = True
                print(f"  ➕ Ajout du champ 'questions' (vide)")
            
            # Vérifier la structure des questions
            if 'questions' in data:
                for i, question in enumerate(data['questions']):
                    if 'id' not in question:
                        question['id'] = f"q{i+1}"
                        modified = True
                    if 'text' not in question and 'texte' not in question:
                        question['text'] = f"Question {i+1}"
                        modified = True
                    if 'type' not in question:
                        question['type'] = 'radio'
                        modified = True
            
            # Sauvegarder si modifié
            if modified:
                with open(fiche_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                fixed_count += 1
                print(f"✅ {fiche_file.name} : Corrigé")
            else:
                print(f"✅ {fiche_file.name} : Déjà correct")
                
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON dans {fiche_file.name}: {e}")
        except Exception as e:
            print(f"❌ Erreur avec {fiche_file.name}: {e}")
    
    print("=" * 50)
    print(f"🎉 Correction terminée : {fixed_count} fichiers modifiés")

def create_backup(fiches_dir):
    """Crée une sauvegarde du dossier fiches"""
    fiches_path = Path(fiches_dir)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = fiches_path.parent / f"fiches_backup_{timestamp}"
    
    import shutil
    shutil.copytree(fiches_path, backup_dir)
    print(f"💾 Sauvegarde créée : {backup_dir}")
    return backup_dir

if __name__ == "__main__":
    fiches_dir = Path("d:/Projects/01-ACTIVE-PROJECTS/questionnaires_mapp/data/fiches")
    
    # Créer une sauvegarde avant correction
    backup_dir = create_backup(fiches_dir)
    
    # Corriger les fiches
    fix_fiches(fiches_dir)