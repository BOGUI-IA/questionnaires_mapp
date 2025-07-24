import json
from pathlib import Path
from typing import Dict, List, Optional

def validate_fiche(fiche_path: Path) -> Dict:
    """Valide une fiche individuelle"""
    try:
        with open(fiche_path, 'r', encoding='utf-8') as f:
            fiche = json.load(f)
            
        errors = []
        warnings = []
        
        # Vérifier les champs requis (utiliser 'title' au lieu de 'titre')
        required_fields = ['id', 'title', 'description', 'questions']
        for field in required_fields:
            if field not in fiche:
                errors.append(f"Champ manquant : {field}")
        
        # Vérifications supplémentaires
        if 'title' in fiche and not fiche['title'].strip():
            warnings.append("Le titre est vide")
            
        if 'description' in fiche and not fiche['description'].strip():
            warnings.append("La description est vide")
        
        # Vérifier la structure des questions
        if 'questions' in fiche:
            if not isinstance(fiche['questions'], list):
                errors.append("Le champ 'questions' doit être une liste")
            elif len(fiche['questions']) == 0:
                warnings.append("Aucune question définie")
            else:
                for i, question in enumerate(fiche['questions']):
                    # Accepter 'text' ou 'texte' pour la compatibilité
                    q_required = ['id', 'type']
                    for field in q_required:
                        if field not in question:
                            errors.append(f"Question {i+1}: Champ manquant '{field}'")
                    
                    # Vérifier qu'il y a un texte de question
                    if 'text' not in question and 'texte' not in question:
                        errors.append(f"Question {i+1}: Champ 'text' ou 'texte' manquant")
                    
                    # Vérifier le type de question
                    valid_types = ['radio', 'checkbox', 'text', 'textarea', 'select', 'multiselect']
                    if 'type' in question and question['type'] not in valid_types:
                        warnings.append(f"Question {i+1}: Type '{question['type']}' non standard")
        
        return {
            'valid': len(errors) == 0,
            'file': str(fiche_path),
            'errors': errors,
            'warnings': warnings
        }
        
    except json.JSONDecodeError as e:
        return {
            'valid': False,
            'file': str(fiche_path),
            'errors': [f"Erreur de décodage JSON: {str(e)}"],
            'warnings': []
        }
    except Exception as e:
        return {
            'valid': False,
            'file': str(fiche_path),
            'errors': [f"Erreur inattendue: {str(e)}"],
            'warnings': []
        }

def validate_all_fiches(fiches_dir: str) -> Dict:
    """Valide toutes les fiches et retourne un rapport complet"""
    fiches_path = Path(fiches_dir)
    results = {
        'total_files': 0,
        'valid_files': 0,
        'invalid_files': 0,
        'files_with_warnings': 0,
        'details': []
    }
    
    print("\n" + "="*60)
    print("🔍 VALIDATION DES FICHES JSON")
    print("="*60)
    
    if not fiches_path.exists():
        print(f"❌ Le dossier {fiches_path} n'existe pas")
        return results
    
    fiche_files = sorted(fiches_path.glob('*.json'))
    if not fiche_files:
        print(f"⚠️ Aucun fichier JSON trouvé dans {fiches_path}")
        return results
    
    results['total_files'] = len(fiche_files)
    
    for fiche_file in fiche_files:
        result = validate_fiche(fiche_file)
        results['details'].append(result)
        
        if result['valid']:
            results['valid_files'] += 1
            if result['warnings']:
                results['files_with_warnings'] += 1
                print(f"✅ {fiche_file.name}: Valide (avec avertissements)")
                for warning in result['warnings']:
                    print(f"   ⚠️ {warning}")
            else:
                print(f"✅ {fiche_file.name}: Parfait")
        else:
            results['invalid_files'] += 1
            print(f"\n❌ {fiche_file.name}: INVALIDE")
            for error in result['errors']:
                print(f"   🔴 {error}")
            if result['warnings']:
                for warning in result['warnings']:
                    print(f"   ⚠️ {warning}")
    
    # Résumé final
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DE LA VALIDATION")
    print("="*60)
    print(f"📁 Total des fichiers : {results['total_files']}")
    print(f"✅ Fichiers valides : {results['valid_files']}")
    print(f"❌ Fichiers invalides : {results['invalid_files']}")
    print(f"⚠️ Fichiers avec avertissements : {results['files_with_warnings']}")
    
    if results['invalid_files'] == 0:
        print("\n🎉 Toutes les fiches sont valides !")
    else:
        print(f"\n🔧 {results['invalid_files']} fichier(s) nécessitent des corrections.")
        print("   Utilisez le script fix_fiches.py pour les corriger automatiquement.")
    
    return results

if __name__ == "__main__":
    fiches_dir = "d:/Projects/01-ACTIVE-PROJECTS/questionnaires_mapp/data/fiches"
    validate_all_fiches(fiches_dir)