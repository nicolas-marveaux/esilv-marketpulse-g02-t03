# Bloomberg Field Mapping

## 1. Objectif et modes autorisés

Le fournisseur Bloomberg (`src/providers/bloomberg_provider.py`) convertit les séries Bloomberg au format canonique MarketPulse, identique à celui produit par `src/providers/yahoo_provider.py`. Le module `src/analytics.py` consomme ce format sans dépendre de la source des données.

| Mode | Source | Usage |
|---|---|---|
| `APPROVED_SAMPLE` (par défaut) | `data/sample/bloomberg_reference_sample.json` | Exécution reproductible, sans Terminal Bloomberg |
| `LIVE` | Terminal Bloomberg autorisé | Point d'extension non implémenté : lève `NotImplementedError` |

L'échantillon approuvé est une fixture fournie par l'enseignant (`sample_kind: instructor_approved_fallback_fixture`, `access_mode: approved_sample`, `is_live_bloomberg_output: false`). Ses valeurs sont pédagogiques, reprises de `data/sample/prices.csv` : ce ne sont pas des observations historiques Bloomberg certifiées.

## 2. Identifiants AAPL / SP500

| Ticker MarketPulse | Identifiant Bloomberg | Rôle dans l'échantillon | Instrument |
|---|---|---|---|
| `AAPL` | `AAPL US Equity` | `instrument` | Apple Inc. (action) |
| `SP500` | `SPX Index` | `benchmark` | S&P 500 (indice) |

Les observations canoniques utilisent toujours le ticker MarketPulse (`AAPL`, `SP500`), jamais l'identifiant Bloomberg.

Dans le JSON, chaque série est repérée par `provider_identifier`. Elle porte son ticker interne dans `canonical_ticker`, son rôle dans `role` et ses données dans `observations` (21 observations par série dans l'échantillon) :

```json
{
  "sample_kind": "...",
  "access_mode": "approved_sample",
  "series": [
    {
      "role": "instrument",
      "canonical_ticker": "AAPL",
      "provider_identifier": "AAPL US Equity",
      "observations": [ { "observation_date": "...", "open_value": 0.0 } ]
    }
  ]
}
```

## 3. Correspondance des champs et types

| Champ source | Champ MarketPulse | Type cible |
|---|---|---|
| `observation_date` | `date` | `str` (AAAA-MM-JJ) |
| `canonical_ticker` (niveau série) | `ticker` | `str` |
| `open_value` | `open` | `float` |
| `high_value` | `high` | `float` |
| `low_value` | `low` | `float` |
| `close_value` | `close` | `float` |
| `volume_value` | `volume` | `int` |

Les champs `role` et `provider_identifier` servent à sélectionner la série, ils ne figurent pas dans l'observation canonique.

Conversions : dans l'échantillon, les valeurs sont des nombres JSON, mais certains prix sont des entiers (par exemple `250`). La conversion explicite `float()` garantit des prix de type `float`, et `int()` un volume de type `int`, quel que soit le format source.

Note : d'après `schema_note`, les clés `*_value` sont des clés pédagogiques, pas des mnémoniques de champs Bloomberg.

## 4. Exemple fictif : brut → canonique

> Données fictives : cet exemple illustre le contrat, il ne provient pas d'une extraction Bloomberg.

Observation brute (série `canonical_ticker = "AAPL"`) :

```python
raw = {
    "observation_date": "2026-11-18",
    "open_value": 100.0,
    "high_value": 112.0,
    "low_value": 99.0,
    "close_value": 110,
    "volume_value": 1500,
}
```

Observation canonique :

```python
canonical = {
    "date": "2026-11-18",
    "ticker": "AAPL",
    "open": 100.0,
    "high": 112.0,
    "low": 99.0,
    "close": 110.0,
    "volume": 1500,
}
```

`close_value` vaut l'entier `110` dans la source et devient le `float` `110.0`.

## 5. Vérifications et limites du mode LIVE

Chaque observation canonique doit vérifier :
- exactement les 7 clés `date`, `ticker`, `open`, `high`, `low`, `close`, `volume` ;
- un ticker interne (`AAPL` ou `SP500`) ;
- des prix en `float` et un volume en `int`.

Contrôle de conformité : `data/sample/bloomberg_reference_expected.json` contient les 42 lignes canoniques attendues (21 AAPL, 21 SP500). La conformité se prouve en comparant les lignes normalisées à ce fichier, pas par sa simple présence.

Erreurs attendues :
- identifiant absent du JSON : `ValueError` ;
- ticker inconnu de `BLOOMBERG_IDENTIFIERS` : `KeyError` ;
- mode inconnu : `ValueError` ;
- série invalide (liste d'observations vide, champ obligatoire manquant, date dupliquée) : `ValueError` explicite levée avant la normalisation.

Cas particulier : le volume de la série `SP500` vaut `0` dans l'échantillon. Un indice n'a pas de volume échangé propre ; `0` reste un `int` valide.

Limites du mode LIVE : il exige un Terminal Bloomberg autorisé et n'est pas implémenté. Aucune connexion réussie ne doit être simulée, et chaque capture indique le mode réellement utilisé.