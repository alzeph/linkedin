# 🔐 Script de Chiffrement/Déchiffrement en Python (3ème outil)

## 🚀 Objectif

Ce script a été conçu dans un but **pédagogique**, pour illustrer comment Python peut être utilisé de manière simple et efficace dans des cas concrets de sécurité de fichiers. Il vise à sensibiliser les débutants comme les curieux à l’impact direct d’un outil bien pensé.

## ✅ Fonctionnalités

- Mode **chiffrement** d'un fichier texte avec mot de passe
- Mode **déchiffrement** d'un fichier préalablement chiffré
- Vérification de la validité du mot de passe avant toute génération de fichier
- Refus de traitement inapproprié (ex : déchiffrer un fichier non chiffré ou inversement)

## ⚠️ Rappel important

Ce script **n'est pas destiné à un usage en production**. Il utilise des principes simples de cryptographie pour des raisons **d'apprentissage uniquement**. N'utilisez pas ce code pour protéger des données sensibles.

## 📃 Utilisation

L'utilisateur choisit :

1. **Chiffrer** ou **Déchiffrer**
2. Fournit le **chemin du fichier**
3. Le script vérifie la cohérence de l'opération (pas de chiffrement sur fichier déjà chiffré, etc.)
4. Demande un **mot de passe** et le **vérifie**
5. En cas d'échec, demande si on souhaite en réessayer un nouveau
6. Si le mot de passe est correct, génère le fichier résultant

## 📝 Améliorations possibles

Voici quelques axes d'évolution que tu peux implémenter pour aller plus loin :

- ✏️ Interface graphique avec `Tkinter` ou `PyQt`
- ⚖️ Support des fichiers binaires et non-texte
- ⛓️ Intégration d'un système de hachage plus robuste pour la vérification du mot de passe
- 🔐 Passage à une bibliothèque de chiffrement plus sécurisée comme `cryptography`
- 🔢 Journalisation des actions (logs)
- ✉️ Envoi du fichier chiffré par mail ou sauvegarde sur le cloud

## ✨ Conclusion

Ce troisième outil est un pas de plus dans ma démarche de **démonstration par la pratique**. Python est un langage d’action. Il n’a pas besoin d'être glorifié : il suffit de montrer ce qu’on peut faire avec.

Et ce n’est que le début.
