# Types d'erreurs analytiques en diagnostic in vitro

## Erreur aléatoire

Variation imprévisible, sans tendance directionnelle, généralement causée par :
- Bulles d'air dans le circuit fluidique
- Contamination ponctuelle d'un échantillon
- Défaillance mécanique isolée (pipetage, vanne)

Signature statistique : un seul point s'écarte fortement (violation 1-3s ou R-4s),
sans que les mesures voisines soient affectées.

## Erreur systématique

Décalage constant ou progressif dans une direction, causé par :
- Dérive de capteur (vieillissement, encrassement, désétalonnage progressif)
- Dégradation de réactif (lot périmé ou mal conservé)
- Problème d'étalonnage initial

Signature statistique : plusieurs points consécutifs du même côté de la moyenne
(violation 2-2s, 4-1s ou 10x), avec une tendance qui persiste dans le temps.

## Impact sur la fiabilité du système

Les erreurs aléatoires affectent un résultat isolé et sont généralement moins
critiques si détectées rapidement (un seul patient concerné). Les erreurs
systématiques affectent potentiellement tous les résultats produits depuis le
début de la dérive, ce qui impose une revue rétrospective des résultats émis
depuis la dernière calibration valide.