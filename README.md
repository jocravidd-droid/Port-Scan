# Port Scanner Python

Scanner de ports TCP écrit en Python, en asynchrone avec `asyncio`.

```text
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

Le script teste une plage de ports sur une cible donnée (adresse IP IPv4 ou nom de domaine) et affiche les ports ouverts avec le nom du service associé (ex. SSH, HTTP, MySQL). 

Il valide le format de la cible via des expressions régulières. Lorsqu'un nom de domaine est renseigné, le script recherche son extension dans sa base de données d'extensions (TLD) pour afficher son type d'usage.

Tous les paramètres sont demandés à l'utilisateur : la cible, le port de départ, le port de fin, le timeout et le nombre maximum de connexions simultanées.

Le programme tourne en boucle : après un scan, il redemande une cible. Taper `exit` termine proprement.

## Comment ça marche

Chaque port est testé par une coroutine `scan_port`, qui tente d'ouvrir une connexion avec `asyncio.open_connection` et applique le timeout choisi via `asyncio.wait_for`. Si la connexion aboutit, le numéro du port est renvoyé ; sinon (timeout, connexion refusée, ou autre erreur réseau) la coroutine renvoie `None`.

La méthode `scan` construit une coroutine par port, puis les lance toutes ensemble avec `asyncio.gather`. Les ports fermés sont ensuite filtrés du résultat.

À la fin du scan, les ports trouvés sont croisés avec le dictionnaire `ports_services_complet` pour formater l'affichage avec le nom lisible des services ("Unknown service" si le port n'est pas référencé).

Un `asyncio.Semaphore` limite le nombre de connexions ouvertes en même temps pour éviter de dépasser la limite de descripteurs du système.

## Journalisation

Le script écrit un journal dans `scan/scan.log`, créé automatiquement au lancement avec `pathlib`. Chaque ligne porte un horodatage et un niveau de gravité.

Les niveaux utilisés :

- `DEBUG` : chaque port testé et son résultat
- `INFO` : démarrage d'un scan avec tous ses paramètres, et résultat final
- `WARNING` : timeout élevé, ou nombre de connexions simultanées faible
- `ERROR` : paramètres de ports invalides

## Gestion des erreurs

- Saisie d'une cible au format invalide (rejette les entrées qui ne sont ni une IP IPv4 ni un nom de domaine)
- `ValueError` pour une valeur non numérique là où un nombre est attendu
- `EOFError` et `KeyboardInterrupt` pour Ctrl+D et Ctrl+C
- Plage de ports invalide (départ > fin, départ < 1, fin > 65535)

## Utilisation

```bash
python scan.py
```

Exemple sur un domaine :

```text
Target or exit: google.com
Type de domaine : Commercial / Universel
Start_port: 1
End_port (limit 65535): 1000
Timeout: 1
Max Connections: 500

Port Found for google.com:
80 (HTTP)
443 (HTTPS)
```

## Ce qui est prévu en 2028

Côté style et présentation :

- personnalisation de la bannière et de l'affichage général
- sortie colorée pour distinguer les ports ouverts, les erreurs et les informations
- affichage d'une barre de progression pendant le scan
- résultats présentés sous forme de tableau

Côté fonctionnalités :

- support des adresses IPv6
- passage d'arguments en ligne de commande (CLI arguments)
- export des résultats dans un fichier (JSON / Text)
- mesure de la durée totale du scan
- rotation automatique des fichiers de logs
