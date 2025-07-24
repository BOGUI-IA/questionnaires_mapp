#!/bin/bash

# Création des dossiers nécessaires
mkdir -p data
mkdir -p responses
mkdir -p sessions

# Installation des dépendances Python
pip install -r requirements.txt

# Donner les permissions d'exécution au script
chmod +x setup.sh
