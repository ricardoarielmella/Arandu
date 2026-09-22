# -*- coding: utf-8 -*-
import json, re, unicodedata, collections, datetime

VACIO = {"", "S/D", "SD", "N/C", "NC", "NO", "NINGUNO", "."}
def limpio(s):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    if re.fullmatch(r"[-—–_.\s]*", s): return ""      # guiones sueltos: la celda no consigna dato
    return "" if s.upper() in VACIO else s
def nd(s): return re.sub(r"\D", "", str(s or ""))
def sinac(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "").upper())
                   if unicodedata.category(c) != "Mn")
def clave(s):  # comparacion laxa de textos
    return re.sub(r"[^A-Z0-9]", "", sinac(s))
def nserie(s):
    s = limpio(s)
    s = re.sub(r"^\s*(NI|N°|Nº|NRO|NR|SERIE)\s*[:.\-]?\s*", "", s, flags=re.I)
    return re.sub(r"[^A-Z0-9]", "", sinac(s))
def mismaSerie(a, b):
    a, b = nserie(a), nserie(b)
    if not a or not b: return False
    if a == b: return True
    # "7102585" frente a "102585": el excel omite el grupo inicial del numero de serie
    return (len(a) != len(b) and (a.endswith(b) or b.endswith(a))
            and abs(len(a) - len(b)) <= 2 and min(len(a), len(b)) >= 5)

MAPA_ARMA = {
 "FUSIL FAL":"FAL 7,62 mm", "FUSIL 5,56 mm":"Fusil 5,56 mm",
 "Pistola 9 mm":"Pistola 9 mm", "Pistola Amet 9 mm":"Pistola Ametralladora 9 mm",
 "Fusil .50":"Fusil .50", "Fusil Tir Esp":"Fusil de Tirador Especial",
 "Amet 7,62 mm":"Ametralladora 7,62 mm", "Amet 5,56 mm":"Ametralladora 5,56 mm",
 "AT 4":"Lanzacohetes AT-4", "CARL GUSTAV":"Carl Gustav"}
LARGAS = ["FUSIL FAL","FUSIL 5,56 mm","Fusil .50","Fusil Tir Esp",
          "Amet 7,62 mm","Amet 5,56 mm","AT 4","CARL GUSTAV"]
CORTAS = ["Pistola 9 mm","Pistola Amet 9 mm"]
# denominaciones del padron equivalentes a las del rol
FAMILIA = {
 "FAL 7,62 mm":"FAL", "FAL Paracaidista 7,62 mm":"FAL",
 "Fusil 5,56 mm":"556", "FARA 83 5,56 mm":"556", "FAA 5,56 mm":"556",
 "Pistola 9 mm":"P9", "Pistola Browning HP 9 mm":"P9", "Pistola Bersa Thunder 9 mm":"P9",
 "Pistola Ametralladora 9 mm":"PA9", "FMK-3 9 mm":"PA9",
 "Fusil .50":"50", "Fusil de Tirador Especial":"TE", "Fusil de Precisión 7,62 mm":"TE",
 "Ametralladora 7,62 mm":"A762", "Ametralladora MAG 7,62 mm":"A762",
 "Ametralladora 5,56 mm":"A556", "Lanzacohetes AT-4":"AT4",
 "Lanzacohetes Instalaza C-90":"AT4", "Carl Gustav":"CG"}
def fam(n): return FAMILIA.get(limpio(n), clave(n))

ESP = {"I":"Infantería","C":"Caballería","A":"Artillería","ING":"Ingenieros","COM":"Comunicaciones",
 "ARS":"Arsenales","INT":"Intendencia","MED":"Sanidad — Médico","ENFPROF":"Sanidad — Enfermería"}
def especialidadDe(cod):
    c = limpio(cod)
    if not c: return ""
    base = c.split("/")[0].strip()
    k = clave(base)
    if k in ESP: return ESP[k]
    if re.match(r"^(conduc|cond|mec mot)", base, re.I): return "Transporte"
    if re.match(r"^(pil|mec av)", base, re.I) or "AV EJ" in sinac(c): return "Aviación de Ejército"
    if re.match(r"^mec", base, re.I): return "Arsenales"
    return ""

def fecha(v):
    v = str(v or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", v)
    if m: return "%s-%s-%s" % m.groups()
    m = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})$", v)
    if m:
        d, mth, y = m.groups(); y = int(y); y = y + 2000 if y < 100 else y
        return "%04d-%02d-%02d" % (y, int(mth), int(d))
    return ""

# ---------- fuentes ----------
filas = json.load(open("rol_filas.json"))
datos = json.load(open("datos-personal.json"))
P = datos["personal"]

# numeros de serie tal como los consigna el packing list (con su punto)
packing = {}
try:
    for f in json.load(open("packing_val.json")):
        s = limpio(f.get("serie"))
        if s: packing[nserie(s)] = s
except Exception as e:
    print("packing no disponible:", e)

reg = {}
for f in filas:
    d = nd(f["dni"])
    if not d: continue
    r = reg.setdefault(d, {"armas":{}, "veh":"", "lic":"", "licVto":"", "rol":"",
                           "destino":"", "grado":"", "esp":"", "filas":[]})
    r["filas"].append("%s!%d" % (f["hoja"], f["fila"]))
    for k, v in f["armas"].items():
        v = limpio(v)
        if v: r["armas"].setdefault(k, v)
    for c, o in (("veh","veh"),("lic","lic"),("rol","rol"),("destino","destino"),
                 ("grado","grado"),("esp","arma")):
        v = limpio(f.get(o, ""))
        if v and not r[c]: r[c] = v
    v = fecha(f.get("licVto",""))
    if v and not r["licVto"]: r["licVto"] = v

porDni = collections.defaultdict(list)
for p in P: porDni[nd(p.get("dni",""))].append(p)

HOY = datetime.date.today().isoformat()
compl = collections.Counter()
conf = collections.defaultdict(list)
nota = []

def anota(p, txt):
    o = limpio(p.get("observaciones", ""))
    if clave(txt) in clave(o): return
    p["observaciones"] = (o + " · " if o else "") + txt

for d, r in reg.items():
    for p in porDni.get(d, []):
        quien = p["apellido"] + ", " + p["nombre"]

        # ---- rol de combate y destino
        for campo, val in (("rolCombate", r["rol"]), ("destino", r["destino"])):
            if not val: continue
            act = limpio(p.get(campo, ""))
            if not act:
                p[campo] = val; compl[campo] += 1
            elif clave(act) != clave(val):
                conf[campo].append({"quien": quien, "dni": p["dni"], "padron": act, "rol": val})

        # ---- especialidad y su detalle
        if r["esp"]:
            if not limpio(p.get("especialidad", "")):
                e = especialidadDe(r["esp"])
                if e: p["especialidad"] = e; compl["especialidad"] += 1
            if not limpio(p.get("especialidadDetalle", "")):
                p["especialidadDetalle"] = r["esp"]; compl["especialidadDetalle"] += 1

        # ---- armamento
        exc = ([(MAPA_ARMA[k], r["armas"][k]) for k in LARGAS if k in r["armas"]] +
               [(MAPA_ARMA[k], r["armas"][k]) for k in CORTAS if k in r["armas"]])
        if exc:
            pad = []
            if limpio(p.get("armamento","")) and p["armamento"] != "Sin asignar":
                pad.append(["armamento", "armaNro", p["armamento"], limpio(p.get("armaNro",""))])
            if limpio(p.get("armaAux","")) and p["armaAux"] != "Sin asignar":
                pad.append(["armaAux", "armaAuxNro", p["armaAux"], limpio(p.get("armaAuxNro",""))])
            nuevas = []
            for tipo, serie in exc:
                m = re.match(r"^\s*FAP\s*[:.\-]\s*(.+)$", serie, re.I)
                if m:                      # el rol distingue el FAL Paracaidista
                    tipo, serie = "FAL Paracaidista 7,62 mm", m.group(1).strip()
                igual = [q for q in pad if fam(q[2]) == fam(tipo)]
                if igual:
                    q = igual[0]
                    if q[3] and not mismaSerie(q[3], serie):
                        conf["armaNro"].append({"quien": quien, "dni": p["dni"],
                            "padron": q[2] + " " + q[3], "rol": tipo + " " + serie})
                    elif not q[3]:
                        p[q[1]] = serie; compl["armaNro"] += 1
                    elif mismaSerie(q[3], serie) and nserie(q[3]) in packing and packing[nserie(q[3])] != q[3]:
                        p[q[1]] = packing[nserie(q[3])]; compl["serie con punto"] += 1
                else:
                    nuevas.append((tipo, serie))
            for tipo, serie in nuevas:
                if not limpio(p.get("armamento","")) or p.get("armamento") == "Sin asignar":
                    p["armamento"] = tipo; p["armaNro"] = serie; compl["armamento"] += 1
                    pad.append(["armamento","armaNro",tipo,serie])
                elif not limpio(p.get("armaAux","")) or p.get("armaAux") == "Sin asignar":
                    p["armaAux"] = tipo; p["armaAuxNro"] = serie; compl["armaAux"] += 1
                    pad.append(["armaAux","armaAuxNro",tipo,serie])
                else:
                    anota(p, "Tercer armamento según el Rol 22SEP26: " + tipo + " NI " + serie)
                    compl["tercer arma en observaciones"] += 1

        # ---- el arma larga es la principal y la pistola la auxiliar
        CORTA = ("P9", "PA9")
        aux = limpio(p.get("armaAux",""))
        if (fam(p.get("armamento","")) in CORTA and aux and aux != "Sin asignar"
            and fam(aux) not in CORTA):
            p["armamento"], p["armaAux"] = p["armaAux"], p["armamento"]
            p["armaNro"], p["armaAuxNro"] = p.get("armaAuxNro",""), p.get("armaNro","")
            compl["arma larga como principal"] += 1

        # ---- vehiculo
        if r["veh"]:
            act = limpio(p.get("vehiculo", ""))
            if not act:
                p["vehiculo"] = r["veh"]; compl["vehiculo"] += 1
            else:
                ka, kb = clave(act), clave(r["veh"])
                a = set(re.findall(r"[A-Z0-9]{5,}", ka))
                b = set(re.findall(r"[A-Z0-9]{5,}", kb))
                if kb in ka or ka in kb: pass          # el padron ya lo consigna, con mas detalle
                elif a and b and not (a & b):
                    conf["vehiculo"].append({"quien": quien, "dni": p["dni"],
                                             "padron": act, "rol": r["veh"]})

        # ---- licencia de conducir
        if r["lic"] and not limpio(p.get("licCat", "")):
            p["licCat"] = r["lic"]; compl["licCat"] += 1
        if r["licVto"] and not limpio(p.get("licVence", "")):
            p["licVence"] = r["licVto"]; compl["licVence"] += 1

        p["actualizado"] = HOY

datos["generado"] = datetime.datetime.now().isoformat()
json.dump(datos, open("datos-personal.json", "w"), ensure_ascii=False, indent=1)
json.dump({k: v for k, v in conf.items()}, open("conflictos.json", "w"), ensure_ascii=False, indent=1)

print("=== COMPLETADO ===")
for k, v in compl.most_common(): print("  %-28s %d" % (k, v))
print("\n=== A RESOLVER (el padron ya tenia otro valor) ===")
for k, v in conf.items(): print("  %-14s %d" % (k, len(v)))
