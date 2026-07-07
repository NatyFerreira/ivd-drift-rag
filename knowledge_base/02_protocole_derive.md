# Protocole de réponse à une dérive détectée

Lorsqu'un système de surveillance signale une dérive du capteur ou de l'instrument,
la procédure standard suit trois étapes.

## 1. Confirmation

Avant toute action corrective, confirmer que le signal n'est pas un faux positif :
- Vérifier si un seul point est concerné (probable erreur ponctuelle) ou si la
  dérive persiste sur plusieurs mesures consécutives (probable dérive systématique).
- Comparer avec l'historique récent du même capteur/analyte.
- Vérifier les journaux de maintenance : une recalibration ou un changement de
  réactif récent explique souvent une variation transitoire attendue.

## 2. Classification de la sévérité

- **Mineure** : écart proche du seuil, isolé, sans impact clinique attendu.
  Surveillance renforcée, pas d'arrêt du système.
- **Modérée** : plusieurs mesures consécutives hors seuil (pattern 4-1s ou 10x).
  Suspension des résultats concernés en attente de vérification.
- **Sévère** : dérive brutale et importante, ou violation 1-3s / R-4s.
  Arrêt immédiat de la ligne concernée, recalibration obligatoire avant reprise.

## 3. Actions correctives

- Recalibration de l'instrument selon la procédure du fabricant.
- Si la dérive persiste après recalibration : inspection matérielle (capteur,
  électrodes, réactifs, maintenance préventive en retard).
- Documentation systématique de l'incident : cause identifiée, action corrective,
  validation du retour à la normale avant remise en production.