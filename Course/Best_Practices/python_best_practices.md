# 🧠 Bonnes pratiques de codage pour Data Scientists (Python)

Ce guide présente les **bases essentielles** pour écrire du code **propre, lisible et reproductible** en Python, adapté au travail de Data Scientist.

---
## 0. Environnements

Ce qui est essentiel, c’est l’environnement Python isolé dans lequel tu travailles.

Deux options principales :

🔹 Option 1 — Conda environment

C’est très courant en data science :

facile à gérer (conda create -n mon_projet python=3.11)

gère aussi les dépendances système (C/C++, CUDA, etc.)

bon pour Jupyter notebooks + packages scientifiques (numpy, pandas, scikit-learn, matplotlib, etc.)

Typiquement :

conda create -n mon_projet python=3.11
conda activate mon_projet
pip install -r requirements.txt

🔹 Option 2 — venv ou virtualenv

Plus “pur Python”, souvent utilisé dans les projets de développement logiciel :

python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
pip install -r requirements.txt

⚙️ 3. Outils typiques associés à cette structure

Tu trouveras souvent :

JupyterLab / VS Code → pour éditer les notebooks et le code.

pytest → pour les tests dans tests/.

Git + GitHub/GitLab → pour le versionnement du code.

.gitignore → pour exclure data/ (souvent trop lourd).

requirements.txt ou environment.yml → pour reproduire l’environnement.

## 🧱 1. Structure minimale d’un projet

Une bonne organisation évite vite le chaos :

```arduino
projet/
├─ data/ # jeux de données (non versionnés)
├─ notebooks/ # explorations, essais
├─ src/ # vrai code Python
│ ├─ init.py
│ └─ utils.py
├─ tests/ # quelques tests unitaires
├─ requirements.txt # dépendances
└─ README.md # comment utiliser le projet
```

👉 Idées :
- Tout ce qui est réutilisable va dans `src/`
- Les notebooks servent à expérimenter
- Le `README` explique comment lancer le projet

---

## 🧹 2. Style de code

Suis les standards de Python : **PEP 8**.  
Mais n’essaie pas de tout retenir → laisse des outils t’aider.

### Outils de base
- **Black** → formate ton code automatiquement  
- **Ruff** → détecte les erreurs & mauvaises pratiques  
- **isort** → range les imports  

Exemple de configuration simple (`pyproject.toml`) :

```toml
[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
Règles clés
1 fonction = 1 rôle
```

Noms explicites : load_data() plutôt que ld()

Commente le pourquoi, pas le quoi

Code lisible > code “malin”

 ## 3. Fonctions propres & testables
Exemple :

```python
import pandas as pd

def compute_ratio(df: pd.DataFrame, num: str, den: str, out: str) -> pd.DataFrame:
    """Ajoute une colonne `out` = num / den."""
    df = df.copy()
    df[out] = df[num] / df[den]
    return df
```

✅ Pas de variable globale
✅ Pas d’effet de bord (ne modifie pas directement les entrées)
✅ Retourne un résultat clair

Et un petit test :

```python
def test_compute_ratio():
    df = pd.DataFrame({"a": [2, 4], "b": [1, 2]})
    out = compute_ratio(df, "a", "b", "r")
    assert list(out["r"]) == [2.0, 2.0]
```

## 🧪 4. Notebooks : exploration oui, bazar non
1 notebook = 1 objectif (exploration, modélisation, visualisation)

Exécute toujours dans l’ordre, sans dépendre d’un état caché

Déplace dans src/ le code que tu veux réutiliser

Évite les chemins en dur : utilise pathlib.Path

## 🗃️ 5. Dépendances & environnement
Utilise un seul gestionnaire : venv ou conda

Liste tes dépendances dans requirements.txt :

nginx
pandas
numpy
scikit-learn
matplotlib
Évite d’avoir plusieurs versions du même package

Fige les versions pour la reproductibilité (pip freeze > requirements.txt)

## 🧾 6. Lisibilité > performance
Code clair > code rapide (la plupart du temps).

Exemples :

✅ df["ratio"] = df["a"] / df["b"]

❌ boucle for sur chaque ligne inutile

✅ df.query("a > 0") pour filtrer simplement

## 🧩 7. Un peu de rigueur sur les données
Vérifie les types (df.dtypes)

Gère les valeurs manquantes (.fillna() ou .dropna())

Documente les colonnes importantes (dans le README ou un dictionnaire de données)

## 📜 8. Logging léger (à la place de print())
python
Copier le code
import logging
logging.basicConfig(level=logging.INFO)
logging.info("Chargement des données terminé.")
Objectif : savoir ce que ton code fait sans inonder la console.

## 🎯 9. Checklist simple avant de livrer
✅ Code auto-formaté (black .)
✅ Pas de variables inutiles ni de print() de debug
✅ Fonctions réutilisables dans src/
✅ Quelques tests unitaires qui passent
✅ Notebook clair et lisible

## 🧰 10. En résumé
Aspect	Bon réflexe
Structure	Sépare code / data / notebooks
Style	Utilise black + ruff
Données	Propres, typées, sans hardcode
Reproductibilité	requirements + seed fixe
Lisibilité	Code clair et simple