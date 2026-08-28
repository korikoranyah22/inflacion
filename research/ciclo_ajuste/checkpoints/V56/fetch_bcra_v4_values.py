#!/usr/bin/env python3
"""Fetch BCRA v4 monthly values for the V56 result subaccounts.
Run only in a network-capable environment. Writes raw JSON, combined CSV, and SHA256 manifest.
No third-party dependencies.
"""
from pathlib import Path
import urllib.request, urllib.parse, json, csv, hashlib, time
CODES=list(range(1150,1163))+list(range(1183,1193))
BASE="https://api.bcra.gob.ar/estadisticas/v4.0/monetarias/{code}"
OUT=Path("raw_bcra_v4_2023"); OUT.mkdir(exist_ok=True)
records=[]; manifest=[]
for code in CODES:
    qs=urllib.parse.urlencode({"desde":"2023-09-01","hasta":"2023-12-31","limit":1000,"offset":0})
    url=BASE.format(code=code)+"?"+qs
    req=urllib.request.Request(url,headers={"User-Agent":"CicloAjuste-V56/1.0"})
    with urllib.request.urlopen(req,timeout=30) as r: data=r.read()
    p=OUT/f"series_{code}_2023.json"; p.write_bytes(data)
    h=hashlib.sha256(data).hexdigest(); manifest.append((code,url,len(data),h))
    obj=json.loads(data)
    for result in obj.get("results",[]):
        for d in result.get("detalle",[]): records.append((code,d.get("fecha"),d.get("valor")))
    time.sleep(0.15)
with open(OUT/"MONTHLY_SUBACCOUNT_VALUES_2023_FETCHED.csv","w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f); w.writerow(["series_code","date","value"]); w.writerows(records)
with open(OUT/"FETCH_MANIFEST.csv","w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f); w.writerow(["series_code","url","bytes","sha256"]); w.writerows(manifest)
print(f"Fetched {len(records)} observations across {len(manifest)} series")
