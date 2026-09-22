# -*- coding: utf-8 -*-
"""Segunda pasada: donde el padron y el Rol 22SEP26 discrepan, prevalece el Rol,
   dejando constancia del valor anterior. Quedan afuera los casos en litigio."""
import json, re, datetime

datos = json.load(open("datos-personal.json"))
P = datos["personal"]
por = {}
for p in P: por.setdefault(re.sub(r"\D","",p.get("dni","")), []).append(p)

def anota(p, txt):
    o = (p.get("observaciones") or "").strip()
    if txt in o: return
    p["observaciones"] = (o + " · " if o else "") + txt

# ---- en litigio: no se tocan
LITIGIO = {"34184234", "27854293"}      # ZELAYA y ORELLANO: dos planillas de embarque frente al Rol
hecho = {"rolCombate": 0, "destino": 0, "vehiculo": 0}

for campo in ("rolCombate", "destino"):
    c = json.load(open("clas_%s.json" % campo))
    for grupo, anotar in (("ortog", False), ("difer", True)):
        for x in c[grupo]:
            for p in por.get(re.sub(r"\D","",x["dni"]), []):
                if (p.get(campo) or "") != x["padron"]: continue
                p[campo] = x["rol"]; hecho[campo] += 1
                if anotar:
                    anota(p, ("Rol 22SEP26: %s se consigna como «%s»; antes «%s»." %
                              ("el rol de combate" if campo == "rolCombate" else "el destino",
                               x["rol"], x["padron"])))

# ---- vehiculo: prevalece el organico del Rol; el de transporte pasa a observaciones
for x in json.load(open("conflictos.json"))["vehiculo"]:
    d = re.sub(r"\D","",x["dni"])
    if d in LITIGIO: continue
    for p in por.get(d, []):
        if (p.get("vehiculo") or "") != x["padron"]: continue
        p["vehiculo"] = x["rol"]; hecho["vehiculo"] += 1
        anota(p, "Embarque: %s. Vehículo orgánico según el Rol 22SEP26: %s." % (x["padron"], x["rol"]))

datos["generado"] = datetime.datetime.now().isoformat()
json.dump(datos, open("datos-personal.json","w"), ensure_ascii=False, indent=1)
print("=== EL ROL 22SEP26 PREVALECE ===")
for k,v in hecho.items(): print("  %-12s %d" % (k,v))
