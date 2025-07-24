import json
import os
from pathlib import Path

def fix_fiche_ids():
    """
    Corrige les IDs des fiches pour qu'ils correspondent exactement à sessions.json
    """
    
    # Mapping des corrections nécessaires
    corrections = {
        "fiche_1.json": {
            "id": "fiche_1",
            "session": "session1_fondations"
        },
        "fiche_2.json": {
            "id": "fiche_2", 
            "session": "session1_fondations"
        },
        "fiche_5.json": {
            "id": "fiche_5",
            "session": "session2_experience"
        },
        "fiche_8.json": {
            "id": "fiche_8",
            "session": "session1_fondations"
        },
        "fiche_12.json": {
            "id": "fiche_12",
            "session": "session1_fondations"
        },
        "fiche_14b.json": {
            "id": "fiche_14b",
            "session": "session1_fondations"
        },
        "fiche_15.json": {
            "id": "fiche_15",
            "session": "session2_experience"
        },
        "fiche_16.json": {
            "id": "fiche_16",
            "session": "session2_experience"
        },
        "fiche_17.json": {
            "id": "fiche_17",
            "session": "session2_experience"
        },
        "fiche_3.json": {
            "id": "fiche_3",
            "session": "session3_intelligence"
        },
        "fiche_4.json": {
            "id": "fiche_4",
            "session": "session3_intelligence"
        },
        "fiche_13a.json": {
            "id": "fiche_13a",
            "session": "session3_intelligence"
        },
        "fiche_13b.json": {
            "id": "fiche_13b",
            "session": "session3_intelligence"
        },
        "fiche_14a.json": {
            "id": "fiche_14a",
            "session": "session3_intelligence"
        },
        "fiche_18.json": {
            "id": "fiche_18",
            "session": "session3_intelligence"
        },
        "fiche_19.json": {
            "id": "fiche_19",
            "session": "session3_intelligence"
        },
        "fiche_6.json": {
            "id": "fiche_6",
            "session": "session4_strategie"
        },
        "fiche_7.json": {
            "id": "fiche_7",
            "session": "session4_strategie"
        },
        "fiche_9.json": {
            "id": "fiche_9",
            "session": "session4_strategie"
        },
        "fiche_10.json": {
            "id": "fiche_10",
            "session": "session4_strategie"
        },
        "fiche_11.json": {
            "id": "fiche_11",
            "session": "session4_strategie"
        }
    }
    
    fiches_dir = Path("data/fiches")
    backup_dir = Path("data/fiches_backup_ids")
    
    # Créer le dossier de sauvegarde
    backup_dir.mkdir(exist_ok=True)
    
    corrected_files = []
    errors = []
    
    for filename, correction in corrections.items():
        fiche_path = fiches_dir / filename
        
        if not fiche_path.exists():
            print(f"⚠️  Fichier non trouvé : {filename}")
            continue
            
        try:
            # Sauvegarde
            backup_path = backup_dir / filename
            with open(fiche_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Chargement et correction
            with open(fiche_path, 'r', encoding='utf-8') as f:
                fiche_data = json.load(f)
            
            # Corrections
            old_id = fiche_data.get('id')
            old_session = fiche_data.get('session')
            
            fiche_data['id'] = correction['id']
            fiche_data['session'] = correction['session']
            
            # Correction des IDs de questions pour fiche_5 (exemple)
            if filename == "fiche_5.json" and 'questions' in fiche_data:
                for i, question in enumerate(fiche_data['questions']):
                    if isinstance(question.get('id'), int):
                        question['id'] = f"q{question['id']}_ux_ui"
            
            # Sauvegarde des corrections
            with open(fiche_path, 'w', encoding='utf-8') as f:
                json.dump(fiche_data, f, indent=2, ensure_ascii=False)
            
            corrected_files.append({
                'file': filename,
                'old_id': old_id,
                'new_id': correction['id'],
                'old_session': old_session,
                'new_session': correction['session']
            })
            
            print(f"✅ {filename}: ID '{old_id}' → '{correction['id']}', Session '{old_session}' → '{correction['session']}'")
            
        except Exception as e:
            error_msg = f"❌ Erreur avec {filename}: {str(e)}"
            errors.append(error_msg)
            print(error_msg)
    
    # Rapport final
    print(f"\n📊 RAPPORT DE CORRECTION:")
    print(f"✅ Fichiers corrigés: {len(corrected_files)}")
    print(f"❌ Erreurs: {len(errors)}")
    print(f"💾 Sauvegardes dans: {backup_dir}")
    
    if errors:
        print("\n❌ ERREURS:")
        for error in errors:
            print(f"  {error}")
    
    return corrected_files, errors

if __name__ == "__main__":
    print("🔧 Correction des IDs des fiches...")
    corrected, errors = fix_fiche_ids()
    print("\n🎉 Correction terminée !")