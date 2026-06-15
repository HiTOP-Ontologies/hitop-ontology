# HiTOP Basiscode-Vokabular

Diese Datei beschreibt `hitop_base_vocabulary.csv`.

## Zweck

`hitop_base_vocabulary.csv` ist die lokale Lookup-Tabelle fuer stabile
HiTOP-Basiscodes. Sie wird verwendet, wenn eine DZPG-MDS-Quellzeile keinen
fertigen `hitop_base_code` enthaelt und der Basiscode aus dem HiTOP-Konzeptlabel
aufgeloest werden muss.

Die Datei ist kein Manifestationssuffix-Export. Sie beschreibt nur die
HiTOP-Basisbegriffe und deren kanonische Basiskennung.

## Ablageort

Die Datei liegt unter `src/data/hitop_base_vocabulary.csv`. Sie ist ein
repository-lokales Datenartefakt, das von den Generierungsskripten als
Eingabequelle verwendet wird.

## Spalten

| Spalte | Bedeutung |
| --- | --- |
| `Code` | lokaler alphanumerischer Konzeptcode ohne Segment und Pruefziffer |
| `Label` | bevorzugtes HiTOP-Konzeptlabel |
| `Segment` | HiTOP-Hierarchiesegment, z.B. `C`, `U`, `T` |
| `Segment Level` | numerische Segmentebene |
| `CheckDigit` | zweistelliger Base62-Pruefteil |
| `HiTOP` | Basiscode ohne ausgeschriebenes Prefix, z.B. `C001qy` |

Beim Laden als Vokabular wird `HiTOP` bei Bedarf mit dem Prefix `HiTOP`
normalisiert, sodass aus `C001qy` der Basiscode `HiTOPC001qy` wird.

## Rebuild

Vom Repository-Root aus:

```bash
.venv/bin/hitop-codegen \
  src/data/hitop_base_vocabulary.csv \
  /tmp/hitop_base_vocabulary.csv \
  --prefix HiTOP
```

Der Rebuild muss die bestehenden Pruefziffern stabil reproduzieren. Ein
schneller Plausibilitaetstest ist:

```bash
scripts/validate_hitop_suffix_tooling.sh
```
