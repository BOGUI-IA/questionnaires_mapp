import json
import os
from pathlib import Path
from datetime import datetime

def fix_numeric_ids():
    """
    Corrige les IDs numériques dans les fiches en les convertissant en chaînes de caractères.
    Crée une sauvegarde avant toute modification.
    """
    # Dossiers
    fiches_dir = Path("data/fiches")
    backup_dir = Path("data/fiches_backup")
    
    # Créer le dossier de sauvegarde s'il n'existe pas
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Horodatage pour le dossier de sauvegarde
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_backup = backup_dir / f"backup_{timestamp}"
    current_backup.mkdir()
    
    # Liste des fiches modifiées
    modified_files = []
    
    # Parcourir tous les fichiers JSON du dossier fiches
    for fiche_path in fiches_dir.glob("*.json"):
        try:
            with open(fiche_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Vérifier si l'ID est numérique
            needs_update = False
            if isinstance(data.get('id'), (int, float)):
                old_id = data['id']
                new_id = f"fiche_{int(old_id)}"  # Convertir en int pour éliminer les décimales
                data['id'] = new_id
                needs_update = True
                
                # Vérifier aussi le champ session s'il est numérique
                if isinstance(data.get('session'), (int, float)):
                    data['session'] = f"session{int(data['session'])}"
                    
                print(f"🔧 Correction de {fiche_path.name}: ID {old_id} -> {new_id}")
            
            # Sauvegarder les modifications si nécessaire
            if needs_update:
                # Sauvegarde du fichier original
                backup_path = current_backup / fiche_path.name
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # Mise à jour du fichier original
                with open(fiche_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                modified_files.append(fiche_path.name)
                
        except Exception as e:
            print(f"❌ Erreur lors du traitement de {fiche_path.name}: {str(e)}")
    
    # Résumé des modifications
    print("\n📝 Résumé des modifications :")
    if modified_files:
        print(f"✅ {len(modified_files)} fiches modifiées :")
        for f in modified_files:
            print(f"  - {f}")
        print(f"\n💾 Une sauvegarde complète est disponible dans : {current_backup}")
    else:
        print("ℹ️ Aucune fiche ne nécessitait de correction.")
    
    return len(modified_files)

if __name__ == "__main__":
    print("🔄 Début de la correction des IDs numériques...")
    modified_count = fix_numeric_ids()
    print(f"\n🎉 Correction terminée ! {modified_count} fiches ont été mises à jour.")
    print("⚠️ N'oubliez pas de vérifier le résultat et de mettre à jour sessions.json si nécessaire.")
