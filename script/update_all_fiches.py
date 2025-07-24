import json
import os
from pathlib import Path
import shutil
from datetime import datetime

def update_fiche(file_path):
    """Met à jour une seule fiche avec les modifications requises"""
    print(f"\nTraitement du fichier: {file_path.name}")
    
    try:
        # Lire le fichier
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        
        # Vérifier la structure
        if 'questions' not in data:
            print(f"  ❌ Structure invalide: pas de clé 'questions'")
            return False
        
        # Appliquer les modifications
        for q in data['questions']:
            # 1. Changer le type
            if q.get('type') == 'radio':
                q['type'] = 'checkbox'
                modified = True
                print(f"  🔄 Type changé en 'checkbox'")
            
            # 2. Ajouter l'option E
            if 'options' in q and isinstance(q['options'], list):
                option_e_exists = any(opt.strip().startswith('(E)') for opt in q['options'] if isinstance(opt, str))
                if not option_e_exists:
                    q['options'].append("(E) Autre (à préciser dans les commentaires)")
                    modified = True
                    print(f"  ➕ Option E ajoutée")
            
            # 3. Mettre à jour le commentaire
            new_comment = "Précisions/Commentaires (obligatoire si Option E ou choix multiples) :"
            if 'comment' in q and q['comment'] != new_comment:
                q['comment'] = new_comment
                modified = True
                print(f"  📝 Commentaire mis à jour")
        
        if not modified:
            print("  ℹ️  Aucune modification nécessaire")
            return False
            
        # Créer un dossier de sauvegarde s'il n'existe pas
        backup_dir = Path("fiches_backup")
        backup_dir.mkdir(exist_ok=True)
        
        # Créer une sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        shutil.copy2(file_path, backup_path)
        print(f"  💾 Sauvegarde créée: {backup_path}")
        
        # Écrire les modifications
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Modifications enregistrées")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False

def main():
    fiches_dir = Path("d:/Projects/01-ACTIVE-PROJECTS/questionnaires_mapp/data/fiches")
    
    if not fiches_dir.exists():
        print(f"❌ Le dossier {fiches_dir} n'existe pas")
        return
    
    # Lister tous les fichiers JSON
    fiche_files = list(fiches_dir.glob('*.json'))
    
    if not fiche_files:
        print("ℹ️  Aucun fichier de fiche trouvé")
        return
    
    print(f"\n🔍 {len(fiche_files)} fiches trouvées")
    print("Début de la mise à jour...")
    print("-" * 60)
    
    updated_count = 0
    
    # Traiter chaque fichier
    for fiche_file in sorted(fiche_files):
        if update_fiche(fiche_file):
            updated_count += 1
    
    # Afficher le résumé
    print("\n" + "=" * 60)
    print("✅ Mise à jour terminée")
    print(f"📊 {updated_count}/{len(fiche_files)} fiches mises à jour")
    print(f"💾 Sauvegardes disponibles dans le dossier: fiche_backup/")
    print("=" * 60)

if __name__ == "__main__":
    main()
