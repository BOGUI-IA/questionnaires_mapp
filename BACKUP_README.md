# Système de Sauvegarde avec Versionnement

Ce système permet de créer des sauvegardes complètes du projet avec versionnement, de les lister et de les restaurer facilement.

## Fonctionnalités

- Création de sauvegardes compressées (ZIP) du projet
- Versionnement automatique avec horodatage
- Conservation d'un historique des sauvegardes
- Limitation du nombre de sauvegardes conservées
- Exclusion automatique des fichiers/dossiers inutiles (cache, fichiers temporaires, etc.)
- Support des commentaires pour chaque sauvegarde
- Intégration avec Git (si disponible)

## Installation

Aucune installation requise. Le script utilise uniquement des bibliothèques Python standard.

## Utilisation

### Créer une sauvegarde

```bash
python backup_project.py create -c "Commentaire optionnel"
```

### Lister les sauvegardes disponibles

```bash
python backup_project.py list
```

### Restaurer une sauvegarde

```bash
python backup_project.py restore backup_20250724_020000
```

Pour restaurer dans un dossier spécifique :

```bash
python backup_project.py restore backup_20250724_020000 -t chemin/vers/dossier/cible
```

## Configuration

Le fichier de configuration `backups/backup_config.json` est créé automatiquement et contient :

- Historique des sauvegardes
- Paramètres d'exclusion
- Nombre maximum de sauvegardes à conserver

### Personnalisation des exclusions

Vous pouvez ajouter des motifs d'exclusion personnalisés en modifiant le fichier de configuration :

```json
{
  "excludes": ["dossier_a_exclure", "*.tmp"],
  "file_excludes": ["*.log", "*.tmp"],
  "max_backups": 10
}
```

## Intégration avec Git (optionnel)

Si votre projet utilise Git, le script détectera automatiquement la version actuelle du projet en utilisant `git describe --tags --always`.

## Bonnes pratiques

1. Créez des sauvegardes avant des changements majeurs
2. Ajoutez des commentaires explicites pour faciliter la restauration
3. Vérifiez régulièrement l'espace disque utilisé par les sauvegardes
4. Considérez la configuration d'une sauvegarde automatique (cron job, etc.)

## Fichiers exclus par défaut

- Fichiers système (`.DS_Store`, `Thumbs.db`, etc.)
- Fichiers temporaires (`*.tmp`, `*.log`, `*~`)
- Dossiers d'environnement virtuel (`.venv`, `venv`, `env`)
- Dossiers de cache (`__pycache__`, `.mypy_cache`)
- Dossiers de contrôle de version (`.git`, `.hg`)
- Dossiers d'IDE (`.vscode`, `.idea`)
- Dossiers de dépendances (`node_modules`)

## Journalisation

Toutes les opérations sont enregistrées dans `backup.log`.

## Licence

Ce script est fourni tel quel, sans garantie d'aucune sorte.
