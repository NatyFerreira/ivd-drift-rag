# Documentation des incidents qualité

## Éléments obligatoires d'un rapport d'incident

Tout incident de dérive ou d'anomalie détectée doit être documenté avec :
- Horodatage précis du début et de la fin de l'incident
- Capteur(s) ou paramètre(s) concerné(s)
- Score d'anomalie ou valeur de déviation observée
- Classification (erreur aléatoire vs systématique)
- Action corrective entreprise
- Résultats potentiellement impactés (plage temporelle à revoir)
- Statut de résolution (en cours / résolu / sous surveillance)

## Traçabilité réglementaire

Dans un environnement réglementé (ICH, FDA, BPC), la documentation d'incident
fait partie intégrante de la traçabilité qualité. Un incident non documenté,
même mineur et sans impact clinique confirmé, constitue un manquement à la
traçabilité attendue lors d'un audit.

## Boucle d'amélioration continue

Chaque incident documenté alimente une base de connaissance interne permettant :
- D'affiner les seuils de détection automatique
- D'identifier des patterns récurrents (même capteur, même période, même type
  de réactif)
- De réduire le temps moyen de résolution (MTTR) pour les incidents similaires
  déjà rencontrés