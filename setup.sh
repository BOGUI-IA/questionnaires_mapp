#!/bin/bash

# Création des dossiers nécessaires
mkdir -p data/fiches
mkdir -p data/responses
mkdir -p data/sessions

# Créer un fichier sessions.json avec contenu par défaut s'il n'existe pas
if [ ! -f "data/sessions.json" ]; then
    cat > data/sessions.json << 'EOF'
{
  "sessions": {
    "session1_fondations": {
      "id": "session1_fondations",
      "title": "Fondations & Stratégie MVP",
      "description": "Établir les bases solides de votre projet IA",
      "icon": "🏗️",
      "deliverable": "Feuille de route MVP avec priorités définies",
      "fiches": ["fiche_1", "fiche_2", "fiche_3", "fiche_4", "fiche_5"]
    },
    "session2_experience": {
      "id": "session2_experience",
      "title": "Cœur Produit, Données & Expérience Utilisateur",
      "description": "Concevoir l'expérience utilisateur et l'architecture des données",
      "icon": "🎯",
      "deliverable": "Spécifications UX/UI et architecture des données",
      "fiches": ["fiche_6", "fiche_7", "fiche_8", "fiche_9", "fiche_10"]
    },
    "session3_intelligence": {
      "id": "session3_intelligence",
      "title": "Algorithme Maître, Business & Vision Long Terme",
      "description": "Développer l'intelligence artificielle et le modèle économique",
      "icon": "🧠",
      "deliverable": "Algorithme principal et business model",
      "fiches": ["fiche_11", "fiche_12", "fiche_13", "fiche_14", "fiche_15"]
    },
    "session4_strategie": {
      "id": "session4_strategie",
      "title": "Stratégie d'Entreprise, Risques & Avenir",
      "description": "Planifier la croissance et gérer les risques",
      "icon": "🚀",
      "deliverable": "Plan stratégique complet et analyse des risques",
      "fiches": ["fiche_16", "fiche_17", "fiche_18", "fiche_19", "fiche_20"]
    }
  }
}
EOF
fi

# Donner les bonnes permissions
chmod -R 755 data
chmod 644 data/sessions.json

# Installation des dépendances Python
pip install -r requirements.txt

# Donner les permissions d'exécution au script
chmod +x setup.sh

echo "Configuration terminée avec succès"
