# Banco de Corrientes S.A. — exact official FY binary endpoint V98

The official Banco de Corrientes `Memoria y Balance 2023` page exposes one 3.27 MB download titled **“Memoria y Estados Financieros Banco de Corrientes S.A. 31-12-2023”**.

Exact download endpoint identified in V98:

`https://www.bancodecorrientes.com.ar/DesktopModules/EasyDNNNews/DocumentDownload.ashx?articleid=221&documentid=1193&moduleid=1510&portalid=0`

The web retrieval layer recognizes this as `application/octet-stream`, but the working container cannot resolve the issuer host, so the binary could not be physically persisted or parsed in this run.

Existing BCRA raw entity `00094` remains:

- Sep `511108=16,968,619k`;
- Dec `511108=40,870,153k`.

No counterparty classification follows from the raw name. Decision: **HOLD / N/D_STRICT**. The exact endpoint is now suitable for manual rescue; after recovery, inspect FY Annex Q and then obtain a compatible Sep bridge.
