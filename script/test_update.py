import json
import os
from pathlib import Path
import shutil

def update_single_fiche(file_path):
    """Met à jour une seule fiche avec des logs détaillés"""
    print(f"\n{'='*80}")
    print(f"Traitement du fichier: {file_path}")
    print(f"Le fichier existe: {file_path.exists()}")
    
    # Vérifier les permissions
    print(f"Peut lire: {os.access(file_path, os.R_OK)}")
    print(f"Peut écrire: {os.access(file_path, os.W_OK)}")
    
    # Lire le fichier
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("✅ Fichier lu avec succès")
    except Exception as e:
        print(f"❌ Erreur de lecture: {e}")
        return
    
    # Vérifier la structure
    if 'questions' not in data:
        print("❌ Structure invalide: pas de clé 'questions'")
        return
    
    # Afficher les 2 premières questions avant modification
    print("\n=== AVANT MODIFICATION ===")
    for i, q in enumerate(data['questions'][:2], 1):
        print(f"\nQuestion {i}:")
        print(f"  Type: {q.get('type')}")
        print(f"  Options: {q.get('options', [])}")
        print(f"  Comment: {q.get('comment', 'N/A')}")
    
    # Appliquer les modifications
    modified = False
    for q in data['questions']:
        # 1. Changer le type
        if q.get('type') == 'radio':
            q['type'] = 'checkbox'
            modified = True
        
        # 2. Ajouter l'option E
        if 'options' in q and isinstance(q['options'], list):
            option_e_exists = any(opt.strip().startswith('(E)') for opt in q['options'] if isinstance(opt, str))
            if not option_e_exists:
                q['options'].append("(E) Autre (à préciser dans les commentaires)")
                modified = True
        
        # 3. Mettre à jour le commentaire
        new_comment = "Précisions/Commentaires (obligatoire si Option E ou choix multiples) :"
        if 'comment' in q and q['comment'] != new_comment:
            q['comment'] = new_comment
            modified = True
    
    if not modified:
        print("\nℹ️  Aucune modification nécessaire")
        return
    
    # Créer une sauvegarde
    backup_path = file_path.with_suffix('.bak')
    try:
        shutil.copy2(file_path, backup_path)
        print(f"\n💾 Sauvegarde créée: {backup_path}")
        
        # Écrire les modifications
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Vérifier l'écriture
        if os.path.getsize(file_path) > 0:
            print("✅ Modifications enregistrées avec succès")
            
            # Afficher les 2 premières questions après modification
            print("\n=== APRÈS MODIFICATION ===")
            with open(file_path, 'r', encoding='utf-8') as f:
                updated_data = json.load(f)
                for i, q in enumerate(updated_data['questions'][:2], 1):
                    print(f"\nQuestion {i}:")
                    print(f"  Type: {q.get('type')}")
                    print(f"  Options: {q.get('options', [])}")
                    print(f"  Comment: {q.get('comment', 'N/A')}")
        else:
            print("❌ Erreur: le fichier est vide après l'écriture")
            
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde/écriture: {e}")
        if backup_path.exists():
            shutil.move(backup_path, file_path)
            print("⚠️  Fichier restauré à partir de la sauvegarde")

if __name__ == "__main__":
    fiches_dir = Path("d:/Projects/01-ACTIVE-PROJECTS/questionnaires_mapp/data/fiches")
    test_file = fiches_dir / "fiche_1.json"
    
    if test_file.exists():
        update_single_fiche(test_file)
    else:
        print(f"❌ Fichier de test non trouvé: {test_file}")
