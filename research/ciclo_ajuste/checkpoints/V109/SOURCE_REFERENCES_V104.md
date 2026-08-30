# Source references V104

## Primary route-forensics evidence
Hybrid Analysis browser capture of an AIF PublicView, submitted 2025-04-30:
- https://hybrid-analysis.com/sample/ac87b43af4c0dbf25d023fe4ce82067902593276ae57d244701dea2b55fd8258/681254b0322cb01225073c1b

The report exposes network metadata for the exact frontend resources listed in `CNV_PUBLICVIEW_FRONTEND_FORENSICS_V104.csv`, and records a hashed extracted PublicView HTML artifact.

## Exact CNV targets
See `CNV_EXACT_PRESENTATION_TARGETS_V104.csv`. These target IDs/GUIDs are inherited from the V103 revalidation; V104 direct fetch was unavailable and is not misrepresented as a new revalidation.

## V103 secondary route evidence — availability drift
V103 used the technical dataset description previously available at:
- https://almanac.ar/datasets/cnv.ons.colocaciones

During V104 that URL returned “Dataset no encontrado”. It is therefore retained only as **inherited V103 route evidence**, not used as the sole basis of the new V104 finding.

## Issuer preservation targets
See `HIGH_PAYOFF_SOURCE_REVALIDATION_V104.md` and `research/ciclo_ajuste/source_audit/SOURCE_PRESERVATION_MISSING_V104.csv`.
