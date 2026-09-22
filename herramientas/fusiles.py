# -*- coding: utf-8 -*-
import json, re, datetime
datos = json.load(open("datos-personal.json")); P = datos["personal"]
ix = {p["dni"]: p for p in P}
def anota(p, t):
    o = (p.get("observaciones") or "").strip()
    if t in o: return
    p["observaciones"] = (o + " · " if o else "") + t

# 1. QUIROGA: el Rol 22SEP26 le asigna el 100973; el 101253 es de ALARCON
q = ix["40515740"]
print("QUIROGA  antes: %s %s" % (q["armamento"], q["armaNro"]))
q["armaNro"] = "100973"
anota(q, "Rol 22SEP26: FAL 7,62 mm NI 100973. El NI 101253 que antes figuraba "
         "corresponde a ALARCÓN, Benito, y en el packing list a JIRA CASTRO, Renzo Sharbel "
         "(DNI 38.210.028), ajeno al padrón vigente.")
print("QUIROGA ahora: %s %s" % (q["armamento"], q["armaNro"]))

# 2. SOUTO: la pistola AEKX898 es de MAYORQUIN segun el packing list y el Rol
s = ix["25961685"]
print("\nSOUTO    antes: %s %s | %s %s" % (s["armamento"], s["armaNro"], s["armaAux"], s["armaAuxNro"]))
s["armaAux"] = "Sin asignar"; s["armaAuxNro"] = ""
anota(s, "Se retiró la Pistola 9 mm NI AEKX898: el packing list y el Rol 22SEP26 la "
         "adjudican a MAYORQUIN, Cristian Gabriel (DNI 40.175.863). Sin armamento asignado.")
print("SOUTO    ahora: %s %s | %s %s" % (s["armamento"], s["armaNro"], s["armaAux"], s["armaAuxNro"]))

# 3. rastro de ruta de archivo colado en las observaciones
RUTA = re.compile(r"\b[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/[0-9a-f]{8}-")
n = 0
for p in P:
    o = p.get("observaciones") or ""
    if RUTA.search(o):
        p["observaciones"] = RUTA.sub("", o); n += 1
print("\nobservaciones depuradas de rastros de ruta: %d" % n)

datos["generado"] = datetime.datetime.now().isoformat()
json.dump(datos, open("datos-personal.json","w"), ensure_ascii=False, indent=1)
