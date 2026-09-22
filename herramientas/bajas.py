# -*- coding: utf-8 -*-
import json, re, datetime
BAJAS = {"44437067":"VENTURA SOLIS, Alfredo Luis",
         "33685920":"CHANAMPA, Martín",
         "32271212":"ROLÓN, Nadia Solange"}
datos = json.load(open("datos-personal.json")); P = datos["personal"]
def nd(s): return re.sub(r"\D","",str(s or ""))
fuera = [p for p in P if nd(p.get("dni")) in BAJAS]
for p in fuera:
    print("  baja: %-34s %-11s %-11s %s" % (p["apellido"]+", "+p["nombre"], p["dni"],
          p.get("rolCombate"), p.get("destino")))
    P.remove(p)
datos["generado"] = datetime.datetime.now().isoformat()
json.dump(datos, open("datos-personal.json","w"), ensure_ascii=False, indent=1)
print("\nlegajos: %d | documentos únicos: %d" % (len(P), len({nd(p['dni']) for p in P})))
