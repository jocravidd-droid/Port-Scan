# Port Scanner Python

Scanner de ports TCP écrit en Python, en asynchrone avec `asyncio`.

```
╭───────────────────────────────────────────────╮
│    ___  ___  ___ _____ ___  ___   _   _  _    │
│   | _ \/ _ \| _ \_   _/ __|/ __| /_\ | \| |   │
│   |  _/ (_) |   / | | \__ \ (__ / _ \| .` |   │
│   |_|  \___/|_|_\ |_| |___/\___/_/ \_\_|\_|   │
│                                               │
│   asynchronous tcp scanner  //  python 3      │
╰───────────────────────────────────────────────╯
```

## Ce que ça fait

Le script teste une plage de ports sur une cible donnée et affiche ceux qui sont ouverts. Tous les paramètres sont demandés à l'utilisateur au lancement, plutôt que figés dans le code : la cible, le port de départ, le port de fin, le timeout et le nombre maximum de connexions simultanées. L'idée est de laisser le plus de contrôle possible à celui qui l'utilise, sans avoir à modifier le fichier.

## Comment ça marche

Chaque port est testé par une coroutine `scan_port`, qui tente d'ouvrir une connexion avec `asyncio.open_connection` et applique le timeout choisi via `asyncio.wait_for`. Si la connexion aboutit, le numéro du port est renvoyé ; sinon (timeout, connexion refusée, ou autre erreur réseau) la coroutine renvoie `None`.

La méthode `scan` construit une coroutine par port, puis les lance toutes ensemble avec `asyncio.gather`. Les ports fermés sont ensuite filtrés du résultat.

C'est ce fonctionnement concurrent qui fait la différence : pendant qu'une connexion attend sa réponse, les autres avancent. Scanner plusieurs milliers de ports prend quelques secondes, là où une version bloquante, port après port, prendrait plus d'une heure.

Un `asyncio.Semaphore` limite le nombre de connexions ouvertes en même temps. Sans cette limite, une grande plage de ports ouvrirait des milliers de connexions d'un coup et dépasserait le nombre de descripteurs de fichiers autorisés par le système. La valeur est laissée au choix de l'utilisateur, pour qu'il puisse l'adapter à sa machine et à sa connexion.

Le timeout et le sémaphore sont passés en paramètres jusqu'à `scan_port`, plutôt que lus dans l'espace global. La fonction est ainsi autonome et réutilisable telle quelle dans un autre script.

## Gestion des erreurs

Les saisies sont protégées sur plusieurs plans :

- `ValueError` pour une valeur non numérique là où un nombre est attendu
- `EOFError` pour une interruption par Ctrl+D
- port de départ supérieur au port de fin
- port de départ inférieur à 1
- port de fin supérieur à 65535

Chaque cas affiche un message explicite, plutôt qu'un scan vide et silencieux.

## Utilisation

```
python scanner.py
```

Exemple sur `8.8.8.8` (DNS de Google) :

```
Target: 8.8.8.8
Start_port: 1
End_port (limit 65535): 1000
Timeout: 1
Max Connections: 500

Port Found for 8.8.8.8: [53, 443, 853]
```

Les trois ports correspondent au DNS classique (53), au DNS-over-HTTPS (443) et au DNS-over-TLS (853).

## Historique

La première version utilisait le module `socket` en mode bloquant, avec une plage de ports figée dans le code. Elle a ensuite été réécrite en asynchrone, puis complétée par une limite de connexions simultanées, une fermeture propre des connexions, le passage de tous les paramètres en saisie utilisateur, la suppression des dépendances globales, une plage de ports configurable, la validation des saisies et une bannière au lancement.

## Pourquoi ce projet

Premier projet où j'ai structuré du code avec une classe plutôt que de suivre un exercice guidé. Il m'a servi à comprendre concrètement `self`, l'intérêt d'un timeout en réseau, les context managers, puis le passage de code bloquant à du code concurrent avec `asyncio`.

## Ce qui est prévu

Ce projet n'est pas figé, je compte continuer à le faire évoluer, aussi bien sur le fond que sur la forme.

Côté style et présentation :

- personnalisation de la bannière et de l'affichage général
- sortie colorée pour distinguer les ports ouverts, les erreurs et les informations
- affichage de la progression pendant un scan long
- résultats présentés sous forme de tableau plutôt qu'une simple liste

Côté fonctionnalités :

- détection du service derrière un port ouvert
- possibilité de passer les paramètres en arguments de ligne de commande, en plus des saisies interactives
- export des résultats dans un fichier
- scan de plusieurs cibles à la suite
- mesure et affichage de la durée du scan
