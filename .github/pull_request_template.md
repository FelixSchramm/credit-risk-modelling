## Summary
Kurz: Was ändert dieser PR und warum?

## Type of change
- [ ] Bugfix
- [ ] New feature / analysis
- [ ] Refactoring (keine Verhaltensänderung)
- [ ] Documentation
- [ ] Model/metrics change

## Related issue
Closes docs/issues/XX-....md (oder GitHub-Issue-Link)

## Changes
- ...
- ...

## Model/Data-Leakage-Check (falls Notebook/Modell/Features betroffen)
- [ ] Beeinflusst dieser PR Trainingsdaten, Features oder das Modell?
- [ ] Falls ja: alte vs. neue Metriken (AUC, KS, Gini) im PR angegeben?
- [ ] Keine neuen Features verwendet, die erst nach Kreditvergabe/Ausfall bekannt sind
      (z. B. `total_pymnt`, `recoveries`, `out_prncp`, `last_pymnt_amnt`, `hardship_*`)?
- [ ] Ein auffällig hoher/niedriger Metrikwert wurde erklärt, nicht nur berichtet?

## How to test / Verification
Wie wurde geprüft, dass die Änderung funktioniert? (z. B. "Notebook Restart & Run All",
"pytest tests/ grün", "CI grün")

## Checklist
- [ ] Notebook läuft sauber von oben nach unten durch
- [ ] Tests laufen durch (`pytest tests/`)
- [ ] README ggf. aktualisiert und weiterhin konsistent mit dem tatsächlichen Repo-Inhalt
- [ ] Keine Secrets/Zugangsdaten committet
