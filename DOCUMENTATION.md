# Documentation technique — scan.py

Document de référence sur le fonctionnement interne du scanner.

## Structure du fichier

Le fichier suit cet ordre :

1. Imports (`asyncio`, `pathlib.Path`, `logging`, `re`)
2. Affichage de la bannière
3. Dictionnaires de référence (`ports_services_complet` et `extensions_domaine_complet`)
4. Création du dossier de journal et configuration de `logging`
5. Définition de la classe `Scanner`
6. Définition de la fonction `scan_port`
7. Boucle principale interactive

`scan_port` est définie en dehors de la classe parce qu'elle n'accède à aucune donnée d'instance : tout ce dont elle a besoin lui est passé en paramètres. Elle est donc réutilisable telle quelle dans un autre script.

## Configuration du journal

```python
log_dir = Path("scan")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename=log_dir / "scan.log"
)
```

`parents=True` crée les dossiers intermédiaires manquants, `exist_ok=True` évite une erreur si le dossier existe déjà.

`basicConfig` doit être appelé une seule fois, avant tout appel de log. Le chemin est un objet `Path`, assemblé avec l'opérateur `/`.

Le dossier est créé relativement au répertoire courant du terminal, pas à l'emplacement du fichier `.py`.

## Classe Scanner

### Attributs

| Attribut | Type | Rôle |
|---|---|---|
| `target` | `str` | Adresse IP ou nom de domaine à scanner |
| `port_range` | `range` | Plage de ports à tester |
| `timeout_value` | `int` | Délai maximum en secondes par port |
| `semaphore` | `asyncio.Semaphore` | Limite de connexions simultanées |
| `results` | `list` | Attribut présent mais non utilisé actuellement |

### Méthode scan

```python
async def scan(self):
    tasks = [scan_port(...) for port in self.port_range]
    result = await asyncio.gather(*tasks)
    save = [p for p in result if p is not None]
    return save
```

Trois étapes :

1. Une compréhension de liste crée une coroutine par port. Aucune n'est exécutée à ce stade : appeler une fonction `async def` produit un objet coroutine en attente.
2. `asyncio.gather(*tasks)` les lance toutes ensemble. L'astérisque éclate la liste en arguments séparés.
3. `gather` renvoie les résultats dans l'ordre de la liste d'origine, pas dans l'ordre d'arrivée. Les `None` (ports fermés) sont filtrés.

## Fonction scan_port

```python
async def scan_port(target, port, timeout_value, semaphore):
    async with semaphore:
        try:
            conn = asyncio.open_connection(target, port)
            _reader, writer = await asyncio.wait_for(conn, timeout=timeout_value)
            writer.close()
            await writer.wait_closed()
            return port
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return None
```

`async with semaphore` bloque tant que le nombre maximum de connexions simultanées est atteint. Le sémaphore est relâché automatiquement à la sortie du bloc, y compris en cas d'erreur.

`asyncio.open_connection` renvoie une coroutine sans l'exécuter ; c'est `wait_for` qui la lance et lui applique le timeout.

`_reader` est déballé mais inutilisé — l'underscore est la convention Python pour le signaler.

`close()` demande la fermeture, `wait_closed()` attend qu'elle soit effective.

### Exceptions traitées

| Exception | Signification |
|---|---|
| `asyncio.TimeoutError` | Aucune réponse dans le délai imparti |
| `ConnectionRefusedError` | La cible a répondu en refusant la connexion |
| `OSError` | Erreur réseau générale (hôte injoignable, DNS échoué, etc.) |

Les trois sont traitées identiquement : le port est considéré comme non ouvert.

## Boucle principale

Ordre des opérations à chaque tour :

1. Saisie de la cible ; `exit` (insensible à la casse) termine le programme.
2. Validation de la cible via des expressions régulières (`re`) :
   - Détection d'IP IPv4.
   - Détection de nom de domaine. Si le nom est valide, recherche du TLD dans `extensions_domaine_complet` pour afficher sa description.
   - Si la cible n'est ni une IP ni un nom de domaine valide, affichage d'une erreur et réinvitation de l'utilisateur.
3. Saisie des quatre paramètres numériques.
4. Avertissements non bloquants : timeout élevé, connexions simultanées insuffisantes.
5. Création du sémaphore.
6. Validation de la plage de ports.
7. Si tout est valide : création du `Scanner`, exécution via `asyncio.run`, mise en correspondance des ports ouverts avec le dictionnaire `ports_services_complet` et affichage structuré.

### Validation

Les trois vérifications de plage forment une chaîne `if/elif/else`. Les avertissements sont des `if` indépendants, placés avant : les inclure dans la chaîne empêcherait le `else` de s'exécuter.

| Condition | Message |
|---|---|
| `start_port > end_port` | Plage inversée |
| `start_port < 1` | Port 0 ou négatif |
| `end_port > 65535` | Au-delà du maximum TCP |

## Limites connues

- Prise en charge uniquement des adresses IPv4 (pas d'IPv6)
- L'attribut `results` de la classe n'est pas exploité
- Le fichier de journal grossit indéfiniment (pas de rotation)
- Aucune barre de progression pendant le scan
