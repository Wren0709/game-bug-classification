# Labelling guidelines

Each record is assigned one primary category based on the **symptom described**, not a presumed root cause. The five categories are deliberately broad; they are not a complete bug taxonomy.

| Category | Use when the main complaint concerns | Common ambiguity |
|---|---|---|
| Audio | Sound output, volume, audio playback or voice | Missing dialogue caused by a failed quest trigger |
| Gameplay | Game rules, progression, abilities, items or state | A delayed action caused by a network stall |
| Network | Connections, session synchronisation, matchmaking or disconnects | A local frame freeze during online play |
| Performance | Frame rate, stutter, freezes, loading time or resource usage | An animation that does not complete because of game logic |
| UI | Interface display, layout, navigation or controls in menus | Unresponsive gameplay controls outside the interface |

## Ambiguous descriptions

1. Use the symptom the player explicitly reports; do not infer technical causes that are not observed.
2. When multiple symptoms appear, use the dominant complaint as the primary label for this single-label experiment.
3. If the dominant complaint is unclear, record the ambiguity for human review. The prototype does not implement multiple labels or an automatic unknown class.
4. Treat model scores as relative decision scores, not calibrated probabilities or proof of a defect's cause.

## Dataset provenance and limitations

The 140 original reports are fictional. The additional 100 training examples and 50 challenge examples were drafted with generative-AI assistance and reviewed for schema consistency. The labels have **not** been independently annotated or adjudicated by multiple reviewers. They cannot support claims of real-player accuracy, label agreement or production readiness.

The separate challenge set prevents **direct reuse** of those records in model training, but it was prepared within the same project and includes conceptually related scenarios. It is not an independent real-world test set. The final report should therefore present both experiments as development assessments only.
