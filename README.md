# Port Scanner Python

Petit scanner de ports écrit en Python, avec le module `socket`.

## Ce que ça fait

Le script demande une adresse IP ou un nom de domaine, puis teste une plage de ports (1 à 99 pour l'instant) pour voir lesquels sont ouverts.

## Comment ça marche

Pour chaque port de la plage, le scanner essaie d'ouvrir une connexion avec `socket.connect_ex()`. Si la connexion réussit (code retour 0), le port est considéré comme ouvert et ajouté à la liste des résultats. Un timeout d'1 seconde est fixé pour éviter que le script reste bloqué trop longtemps sur un port qui ne répond pas.

## Utilisation

```
python Scanner.py
```

Le script demande ensuite l'IP ou le domaine à scanner.

Exemple avec `8.8.8.8` (DNS de Google) :

```
IP OR DOMAINE: 8.8.8.8
[53]
```

## Pourquoi ce projet

Premier petit projet où j'ai vraiment utilisé une classe pour structurer du code, plutôt que de juste suivre un exercice guidé. Ça m'a servi à comprendre concrètement à quoi sert `self`, et pourquoi un timeout est indispensable dès qu'on fait du réseau.

## À améliorer

- La plage de ports est fixée dans le code (1 à 99), pas encore demandée à l'utilisateur
- Pas de multithreading, donc le scan est lent sur une grande plage de ports
- Pas de détection du service derrière un port ouvert
