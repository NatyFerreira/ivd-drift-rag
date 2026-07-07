# Règles de Westgard pour le contrôle qualité

Les règles de Westgard sont un ensemble de critères statistiques utilisés pour accepter
ou rejeter une série analytique en fonction des résultats des contrôles qualité.

## Règles principales

- **1-2s** : alerte si un contrôle dépasse 2 écarts-types (SD) de la moyenne. Règle
  d'avertissement uniquement, ne rejette pas la série seule.
- **1-3s** : rejet si un contrôle dépasse 3 SD. Indique une erreur aléatoire significative.
- **2-2s** : rejet si deux contrôles consécutifs dépassent 2 SD dans la même direction.
  Indique une erreur systématique.
- **R-4s** : rejet si la différence entre deux contrôles consécutifs dépasse 4 SD.
  Indique une erreur aléatoire.
- **4-1s** : rejet si quatre contrôles consécutifs dépassent 1 SD dans la même direction.
  Indique une dérive systématique émergente.
- **10x** : rejet si dix contrôles consécutifs se situent du même côté de la moyenne,
  même sans dépasser 1 SD. Indique un biais systématique persistant.

## Interprétation pratique

Une violation de type 2-2s, 4-1s ou 10x pointe généralement vers une **erreur
systématique** (dérive du capteur, recalibration nécessaire, changement de réactif/lot).
Une violation 1-3s ou R-4s pointe plutôt vers une **erreur aléatoire** (problème
ponctuel : bulle d'air, contamination, défaillance mécanique isolée).