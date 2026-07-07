# Gestion des alertes de monitoring

## Priorisation des alertes

Toutes les alertes ne nécessitent pas une intervention immédiate. Une priorisation
claire évite la fatigue d'alerte (alert fatigue) qui mène à ignorer les signaux
réellement critiques.

- **Critique** : impact direct possible sur des résultats déjà rendus aux
  cliniciens. Intervention immédiate, astreinte déclenchée si hors heures ouvrées.
- **Élevée** : dérive confirmée mais résultats encore en attente de validation.
  Intervention dans l'heure.
- **Modérée** : signal isolé, sous surveillance renforcée. Revue dans la journée.
  Pas d'arrêt de production nécessaire à ce stade.
- **Faible** : information, tendance à surveiller sur plusieurs jours. Revue
  hebdomadaire suffisante.

## Réduction des faux positifs

Un système de détection trop sensible génère des faux positifs qui érodent la
confiance des équipes support. Bonnes pratiques :
- Ajuster les seuils sur des données historiques représentatives, pas sur un
  échantillon trop restreint.
- Distinguer les capteurs peu représentés (peu de données d'entraînement) des
  capteurs bien couverts — un capteur sous-représenté peut générer plus de faux
  positifs par manque de données d'apprentissage.
- Documenter chaque alerte traitée (vrai positif / faux positif) pour affiner
  progressivement les seuils.