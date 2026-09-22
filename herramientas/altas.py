# -*- coding: utf-8 -*-
import json, re, datetime, random, string

datos = json.load(open("datos-personal.json"))
P = datos["personal"]
def nd(s): return re.sub(r"\D","",str(s or ""))
HOY = datetime.date.today().isoformat()

# ---------- unificación del legajo duplicado de CARDOZO ----------
dup = [p for p in P if nd(p.get("dni")) == "40522447"]
if len(dup) > 1:
    conFoto = next((p for p in dup if p.get("foto")), dup[0])
    otro    = [p for p in dup if p is not conFoto]
    for o in otro:                       # nada se pierde: lo que el otro tenga y éste no, se conserva
        for k, v in o.items():
            if k in ("id","foto") : continue
            if isinstance(v,str) and v.strip() and not str(conFoto.get(k) or "").strip():
                conFoto[k] = v
    conFoto["grado"] = "Cbo"             # el Rol lo consigna como CB
    conFoto["armaNro"] = "7.102919"
    ob = (conFoto.get("observaciones") or "").strip()
    nota = "Legajo unificado: figuraba por duplicado; se conservó la fotografía y el grado que el Rol 22SEP26 establece."
    if nota not in ob: conFoto["observaciones"] = (ob + " · " if ob else "") + nota
    for o in otro: P.remove(o)
    print("Cardozo unificado; se suprimió %d legajo duplicado." % len(otro))

# ---------- altas ordenadas ----------
GRADO = {"SG":"Sgto", "CI":"Cbo 1ro"}
ESP   = {"I":"Infantería", "Conduc Mot":"Transporte"}
ALTAS = [
 {"ord":"175","grado":"SG","apellido":"FERNANDEZ","nombre":"Facundo",
  "listado":"FACUNDO FERNANDEZ","dni":"33297659","esp":"I","rol":"OA","destino":"RI Parac 2",
  "org":"pq-riparac2","elem":"de3-pqdt",
  "arma":"FAL 7,62 mm","armaNro":"1.000665","aux":"Pistola 9 mm","auxNro":"269391"},
 {"ord":"193","grado":"SG","apellido":"PAREDES","nombre":"Mario Leonardo",
  "listado":"MARIO LEONARDO PAREDES","dni":"33984606","esp":"I","rol":"J Eq","destino":"RI Parac 2",
  "org":"pq-riparac2","elem":"de3-pqdt",
  "arma":"FAL 7,62 mm","armaNro":"1.000076","aux":"Pistola 9 mm","auxNro":"269368"},
 {"ord":"368","grado":"CI","apellido":"LENCINA","nombre":"Hernán Tomás",
  "listado":"HERNÁN TOMAS LENCINA","dni":"35682439","esp":"Conduc Mot","rol":"Cond","destino":"B Transp 601",
  "org":"tr-btransp601","elem":"fdr-tr","arma":"","armaNro":"","aux":"","auxNro":""},
 {"ord":"379","grado":"SG","apellido":"GERARD","nombre":"José",
  "listado":"JOSE GERARD","dni":"30680838","esp":"Conduc Mot","rol":"Cond","destino":"Cdo Br Bl II (BAL PARANA)",
  "org":"tr-brbl2","elem":"fdr-tr","arma":"","armaNro":"","aux":"","auxNro":""},
]
modelo = P[0]
def nuevoId():
    return "p" + "".join(random.choice(string.ascii_lowercase+string.digits) for _ in range(13))

ya = {nd(p.get("dni")) for p in P}
sumados = []
for a in ALTAS:
    if a["dni"] in ya:
        print("ya estaba:", a["apellido"]); continue
    p = {k: ([] if isinstance(v,list) else (False if isinstance(v,bool) else "")) for k,v in modelo.items()}
    p.update({
      "id": nuevoId(), "apellido": a["apellido"], "nombre": a["nombre"],
      "nombreListado": a["listado"], "verificarNombre": True,
      "dni": a["dni"], "lista": "Titular", "grado": GRADO[a["grado"]],
      "especialidad": ESP[a["esp"]], "especialidadDetalle": a["esp"],
      "rolCombate": a["rol"], "destino": a["destino"],
      "orgId": a["org"], "elementoId": a["elem"],
      "nivel": "Sin determinar", "genero": "Sin declarar",
      "apto": "S", "sangre": "Sin registrar",
      "armamento": a["arma"] or "Sin asignar", "armaNro": a["armaNro"],
      "armaAux": a["aux"] or "Sin asignar", "armaAuxNro": a["auxNro"],
      "actualizado": HOY,
      "observaciones": ("Alta por orden del J Dpto Personal. Datos tomados del Apéndice 4 "
                        "(Rol de Combate) del 22 SEP 26, Nro de Orden %s. Resta relevar filiación, "
                        "fotografía y documentación." % a["ord"]),
    })
    P.append(p); sumados.append(p)

P.sort(key=lambda x: (x["apellido"], x["nombre"]))
datos["generado"] = datetime.datetime.now().isoformat()
json.dump(datos, open("datos-personal.json","w"), ensure_ascii=False, indent=1)

print("\nAltas practicadas: %d" % len(sumados))
for p in sumados:
    print("  %-8s %-30s %-10s %-10s %-26s %s %s" % (p["grado"], p["apellido"]+", "+p["nombre"], p["dni"],
          p["rolCombate"], p["destino"], p["armamento"], p["armaNro"]))
print("\nTotal de legajos: %d" % len(P))
print("Documentos únicos: %d" % len({nd(p["dni"]) for p in P}))
