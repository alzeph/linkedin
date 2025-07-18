# Documentation d’utilisation - Script de renommage de fichiers

## Description

Ce script permet de renommer en lot les fichiers d’un dossier selon un modèle personnalisable.
Il supporte le remplacement de texte, l’exclusion de certains fichiers, le tri, la simulation (dry-run), et la confirmation avant exécution.

---

## Installation

1. Installer la dépendance `colorama` (pour la couleur dans la console) :

```bash
pip install colorama
```

2. Placer le script Python `renamer.py` sur votre machine.

---

## Commandes principales

```bash
python renamer.py path/to/directory --pattern "image_{index}_{date}" --dry-run
```

* `path/to/directory` : dossier contenant les fichiers à renommer
* `--pattern` : modèle de nommage. Variables possibles :

  * `{index}` : numéro incrémental (format configurable)
  * `{name}` : nom original (sans extension)
  * `{date}` : date du jour au format AAAAMMJJ
* `--dry-run` : simule sans modifier les fichiers
* `--replace "ancien:nouveau"` : remplace dans le nom l’occurrence `ancien` par `nouveau`
* `--exclude fichier1.txt fichier2.jpg` : exclut certains fichiers du renommage
* `--sort alpha|date` : trie les fichiers par ordre alphabétique (par défaut) ou date de modification
* `--confirm` : demande confirmation avant de renommer
* `--index-format "{:03}"` : format de l’index (ex : `{index}` → 001, 002, 003)

---

## Exemples

### Simuler un renommage

```bash
python renamer.py ./photos --pattern "photo_{index}_{date}" --dry-run
```

### Renommer avec remplacement de texte

```bash
python renamer.py ./docs --pattern "{name}_{index}" --replace "brouillon:final" --confirm
```

### Exclure des fichiers spécifiques

```bash
python renamer.py ./exports --pattern "export_{index}" --exclude "README.md" "notes.txt"
```

---

## Remarques

* Le script ne modifie pas les fichiers en mode `--dry-run`.
* Le numéro `{index}` commence à 1 et est formaté par défaut sur 2 chiffres (01, 02, ...).
* La confirmation permet d’éviter les erreurs accidentelles.

---

