# Questionnaires MAPP

Application de gestion de questionnaires pour MAPP.

## Déploiement sur Render

### Prérequis

- Un compte [Render](https://render.com/)
- Un dépôt GitHub avec le code de l'application

### Étapes de déploiement

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/BOGUI-IA/questionnaires_mapp.git
   cd questionnaires_mapp
   ```

2. **Créer un nouveau service Web sur Render**
   - Allez sur [Render Dashboard](https://dashboard.render.com/)
   - Cliquez sur "New" puis sélectionnez "Web Service"
   - Connectez votre compte GitHub si ce n'est pas déjà fait
   - Sélectionnez le dépôt `BOGUI-IA/questionnaires_mapp`

3. **Configuration du service**
   - **Nom** : `questionnaires-mapp` (ou un nom de votre choix)
   - **Région** : Choisissez la région la plus proche de vos utilisateurs
   - **Branch** : `main`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`

4. **Variables d'environnement**
   - `PYTHONUNBUFFERED` : `True`
   - `PORT` : `10000`

5. **Déploiement**
   - Cliquez sur "Create Web Service"
   - Render va maintenant construire et déployer votre application

6. **Accès à l'application**
   Une fois le déploiement terminé, vous recevrez une URL pour accéder à votre application (par exemple : `https://questionnaires-mapp.onrender.com`)

## Développement local

### Configuration requise

- Python 3.9+
- pip

### Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/BOGUI-IA/questionnaires_mapp.git
   cd questionnaires_mapp
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: .\venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Lancer l'application**
   ```bash
   streamlit run app.py
   ```
   L'application sera disponible à l'adresse : http://localhost:8501

## Structure du projet

- `app.py` : Point d'entrée de l'application Streamlit
- `requirements.txt` : Dépendances Python
- `data/` : Fichiers de données de l'application
- `script/` : Scripts utilitaires
- `sessions/` : Fichiers de session utilisateur
- `responses/` : Réponses aux questionnaires

## Licence

Tous droits réservés - IA-INDUS 2025
