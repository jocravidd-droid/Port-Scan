# Port Scanner Python

Scanner de ports écrit en Python, en asynchrone avec `asyncio`.

## Ce que ça fait

Le script demande une adresse IP ou un nom de domaine, ainsi qu'un numéro de port maximum, puis teste tous les ports de 1 jusqu'à cette valeur pour voir lesquels sont ouverts.

## Comment ça marche

Chaque port est testé par une coroutine `scan_port`, qui tente d'ouvrir une connexion avec `asyncio.open_connection` et applique un timeout d'1 seconde via `asyncio.wait_for`. Si la connexion aboutit, le numéro du port est renvoyé ; sinon (timeout, connexion refusée, ou autre erreur réseau) la coroutine renvoie `None`.

La méthode `scan` construit une coroutine par port, puis les lance toutes ensemble avec `asyncio.gather`. Les ports fermés sont ensuite filtrés du résultat.

C'est ce fonctionnement concurrent qui fait la différence : pendant qu'une connexion attend sa réponse, les autres avancent. Scanner plusieurs milliers de ports prend quelques secondes, là où une version bloquante, port après port, prendrait plus d'une heure.

## Utilisation

```
python Scanner.py
```

Exemple sur `8.8.8.8` (DNS de Google), avec 6589 ports testés :

```
Target: 8.8.8.8
MAX PORT: 6589
[53, 443, 853]
```

Les trois ports correspondent au DNS classique (53), au DNS-over-HTTPS (443) et au DNS-over-TLS (853).

## Historique

La première version utilisait le module `socket` en mode bloquant, avec une plage de ports figée dans le code. Elle a ensuite été réécrite en asynchrone, ce qui a permis de passer de quelques dizaines de ports à plusieurs milliers dans un temps raisonnable.

## Pourquoi ce projet

Premier projet où j'ai structuré du code avec une classe plutôt que de suivre un exercice guidé. Il m'a servi à comprendre concrètement `self`, l'intérêt d'un timeout en réseau, les context managers, puis le passage de code bloquant à du code concurrent avec `asyncio`.

## À améliorer

- Pas de détection du service derrière un port ouvert
- Pas de limite sur le nombre de connexions simultanées, ce qui peut poser problème sur de très grandes plages
- La fermeture des connexions ne fait pas encore de `await writer.wait_closed()`
