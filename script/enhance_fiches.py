import json
import os
from pathlib import Path

def enhance_fiche_structure(fiches_dir):
    """
    Améliore la structure des fiches JSON :
    - Ajoute l'option (E) à toutes les questions
    - Change le type en 'checkbox' pour permettre choix multiples
    - Améliore les commentaires pour encourager l'option E
    """
    
    fiches_path = Path(fiches_dir)
    enhanced_count = 0
    
    for fiche_file in fiches_path.glob('fiche_*.json'):
        try:
            # Charger la fiche
            with open(fiche_file, 'r', encoding='utf-8') as f:
                fiche_data = json.load(f)
            
            # Modifier chaque question
            for question in fiche_data.get('questions', []):
                # Ajouter l'option (E) si elle n'existe pas
                options = question.get('options', [])
                has_option_e = any('(E)' in opt for opt in options)
                
                if not has_option_e and len(options) == 4:
                    options.append("(E) Autre (à préciser dans les commentaires)")
                    question['options'] = options
                
                # Changer le type en checkbox pour choix multiples
                if question.get('type') == 'radio':
                    question['type'] = 'checkbox'
                
                # Améliorer le texte des commentaires
                current_comment = question.get('comment', '')
                if 'Précisions/Commentaires' in current_comment:
                    question['comment'] = "Précisions/Commentaires (obligatoire si Option E ou choix multiples) :"
            
            # Sauvegarder la fiche modifiée
            with open(fiche_file, 'w', encoding='utf-8') as f:
                json.dump(fiche_data, f, ensure_ascii=False, indent=2)
            
            enhanced_count += 1
            print(f"✅ Fiche {fiche_file.name} améliorée")
            
        except Exception as e:
            print(f"❌ Erreur avec {fiche_file.name}: {e}")
    
    return enhanced_count

if __name__ == "__main__":
    fiches_directory = "data/fiches"
    
    print("🚀 Amélioration des fiches JSON...")
    count = enhance_fiche_structure(fiches_directory)
    print(f"\n✨ {count} fiches améliorées avec succès !")
    
    print("\n📋 Modifications apportées :")
    print("   • Option (E) ajoutée à toutes les questions")
    print("   • Type changé de 'radio' vers 'checkbox'")
    print("   • Commentaires améliorés pour encourager l'option E")