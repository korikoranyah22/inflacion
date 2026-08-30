# HSBC Bank Argentina S.A. — CNV presentation metadata audit V98

The target publicviews already recorded in V88 are confirmed and can now be pinned to exact CNV document numbers:

- 30/09/2023: presentation **#3121099**, NIIF, **INDIVIDUAL**, periodicity 3, close 2023-09-30; publicview UUID `d483d33a-5c86-4fbb-ab9c-6528bf43f572`.
- 31/12/2023: presentation **#3163537**, NIIF, **INDIVIDUAL**, periodicity 1, close 2023-12-31; publicview UUID `39f37eb9-5637-4cb3-ab6b-715da7830bd1`.

The current CNV company page is labeled **BANCO GGAL S.A.** under the same CUIT `33-53718600-9` after the later corporate reorganization. This live label must not be misread as evidence that the 2023 filing belonged to Galicia. The document numbers, dates, CUIT and historical presentation route are the recovery anchors.

Both publicviews still resolve only to the CNV dynamic shell in the current retrieval route; the actual attachment bytes are not exposed. Existing raw entity `00150` remains control-only:

- Sep: `511027=68,481,253k`; `521022=169,767k`;
- Dec: `511027=204,724,664k`; `521022=542,204k`.

Decision: **HOLD / N/D_STRICT** until the actual 2023 individual attachment(s) are physically recovered and provide an entity-specific counterparty crosswalk.
