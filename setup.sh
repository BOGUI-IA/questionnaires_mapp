#!/bin/bash

# Création des dossiers nécessaires
mkdir -p data/fiches
mkdir -p responses
mkdir -p sessions

# Créer un fichier sessions.json vide s'il n'existe pas
if [ ! -f "data/sessions.json" ]; then
    echo '{"sessions": {}}' > data/sessions.json
fi

# Donner les bonnes permissions
chmod -R 755 data
chmod 644 data/sessions.json

# Installation des dépendances Python
pip install -r requirements.txt

# Donner les permissions d'exécution au script
chmod +x setup.sh

echo "Configuration terminée avec succès"
