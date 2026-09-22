# -*- coding: utf-8 -*-
"""Genera la version de CONSULTA (solo lectura) a partir del board de trabajo."""
import json, sys, io, re

MAESTRO = "/home/user/Arandu/board/board-administracion-personal.html"

def main(json_path, salida):
    h = io.open(MAESTRO, encoding="utf-8").read()
    datos = json.load(io.open(json_path, encoding="utf-8"))
    P = datos.get("personal", [])
    n = len(P)
    sello = (datos.get("generado") or "") + "#" + str(n)

    cambios = []
    def rep(viejo, nuevo, etiqueta, veces=1):
        assert h.count(viejo) == veces, "NO ENCONTRADO (%d): %s" % (h.count(viejo), etiqueta)
        cambios.append(etiqueta)
        return h.replace(viejo, nuevo)

    # ---- 1. clave de almacenamiento propia (no colisiona con el board de trabajo)
    h = rep('const CLAVE = "board_personal_fdr_v1";',
            'const CLAVE = "board_personal_fdr_consulta";',
            "clave de almacenamiento")

    # ---- 2. titulo de la pestana
    h = rep('<title>FDR Departamento Personal “Ejercicio Arandú” Año 2026</title>',
            '<title>FDR Departamento Personal “Ejercicio Arandú” Año 2026 — Vista de consulta</title>',
            "titulo")

    # ---- 3. distintivo SOLO CONSULTA en el encabezado
    h = rep('<span id="subtitulo">TC MELLA Ricardo Ariel — J Dpto Personal</span>',
            '<span id="subtitulo">TC MELLA Ricardo Ariel — J Dpto Personal</span>\n'
            '    <span class="solo-lectura">Vista de consulta · solo lectura</span>',
            "distintivo")

    # ---- 4. estilo del distintivo
    h = rep('  .ficha{break-inside:avoid}\n}\n</style>',
            '  .ficha{break-inside:avoid}\n}\n'
            '.solo-lectura{display:inline-block;margin-top:4px;padding:2px 9px;border-radius:999px;\n'
            '  border:1px solid var(--warn);color:var(--warn);background:color-mix(in srgb,var(--warn) 12%,transparent);\n'
            '  font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase}\n'
            '@media print{.solo-lectura{display:none}}\n'
            '.id .solo-lectura{align-self:flex-start;width:fit-content}\n'
            '/* La ficha se presenta como documento: los campos se leen, no se completan. */\n'
            '#mCuerpo input,#mCuerpo select,#mCuerpo textarea{background:transparent;border-color:var(--linea);\n'
            '  color:var(--texto);opacity:1;cursor:default}\n'
            '#mCuerpo input::placeholder,#mCuerpo textarea::placeholder{color:transparent}\n'
            '#mCuerpo button,#mCuerpo .ayuda{display:none}\n'
            '</style>', "estilo distintivo")

    # ---- 5. fuera el boton + Alta
    h = rep('    <button class="btn sm pri" id="btnNuevo">+ Alta</button>\n', "", "boton Alta")

    # ---- 6. fuera Guardar y Eliminar del pie de la ficha
    h = rep('    <button class="btn danger" id="btnEliminar">Eliminar legajo</button>\n', "", "boton Eliminar")
    h = rep('      <button class="btn pri" id="btnGuardar">Guardar</button>\n', "", "boton Guardar")
    h = rep('      <button class="btn" data-cerrar>Cancelar</button>',
            '      <button class="btn" data-cerrar>Cerrar</button>', "boton Cancelar")

    # ---- 7. fuera las exportaciones a CSV de Personal y Planillas
    h = rep('    <button class="btn sm" id="btnCsvFiltro">Exportar CSV (filtrado)</button>\n', "", "CSV personal")
    h = rep('    <button class="btn sm" id="btnCsvPlanilla">Exportar CSV</button>\n', "", "CSV planillas")

    # ---- 8. fuera el cuadro "Senalados en amarillo" del tablero
    h = rep('    {n:noRol+suplentes, t:"Señalados en amarillo", '
            'd:noRol+" fuera del Rol 22SEP26 · "+suplentes+" suplentes", c:(noRol+suplentes)?"warn":"ok"},\n',
            "", "cuadro amarillo")

    # ---- 9. solapa DATOS reducida
    ini = h.index('<!-- =================== DATOS =================== -->')
    fin = h.index('</div><!-- /wrap -->')
    nueva = (
      '<!-- =================== DATOS =================== -->\n'
      '<section class="vista" id="v-datos">\n'
      '  <div class="sec-tit"><h2>Datos del ejercicio</h2>'
      '<p>El padrón viaja dentro de este mismo archivo</p></div>\n'
      '  <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">\n'
      '    <div class="card"><div class="hd"><h3>Padrón incorporado</h3></div><div class="bd">\n'
      '      <p class="ayuda" style="margin-top:0">Este documento es una <b>vista de consulta</b>. '
      'Los %d legajos —con fotografías, organigrama y planillas— están incorporados al propio archivo HTML: '
      'no requiere archivos externos, instalación ni conexión a internet.</p>\n'
      '      <p class="ayuda">No admite altas, bajas ni modificaciones. La versión de trabajo, única habilitada '
      'para actualizar los datos, queda en poder del Departamento Personal del Cdo FDR.</p>\n'
      '      <div class="row" style="margin-top:10px">\n'
      '        <button class="btn pri" id="btnDemo">Cargar %d legajos</button>\n'
      '      </div>\n'
      '      <p class="ayuda" style="margin-top:10px">Restaura la vista al padrón original '
      'incorporado en este archivo.</p>\n'
      '    </div></div>\n\n'
      '    <div class="card" style="grid-column:1/-1"><div class="hd"><h3>Composici\u00f3n del padr\u00f3n</h3></div>\n'
      '      <div class="bd" id="estadoAlmacen"></div></div>\n'
      '  </div>\n'
      '</section>\n\n'
    ) % (n, n)
    h = h[:ini] + nueva + h[fin:]
    cambios.append("solapa Datos")

    # ---- 10. selector tolerante con los elementos suprimidos
    h = rep('const $  = (s,e=document)=>e.querySelector(s);',
            '/* Vista de consulta: los controles de edición fueron suprimidos del documento;\n'
            '   el selector devuelve un elemento inerte para que el cableado original no falle. */\n'
            'const SUPRIMIDOS = new Set(["#btnNuevo","#btnGuardar","#btnEliminar","#btnBorrar",\n'
            '  "#btnAbrir","#btnVincular","#btnGuardarArch","#estadoArchivo","#btnExpJson","#btnExpCsv",\n'
            '  "#btnImpJson","#btnImpJsonMerge","#btnImpCsv","#archivoImp","#btnCsvFiltro","#btnCsvPlanilla"]);\n'
            'const $  = (s,e=document)=>e.querySelector(s) || (SUPRIMIDOS.has(s)? document.createElement("input") : null);',
            "selector tolerante")

    # ---- 11. el padron siempre sale del archivo; del navegador solo el tema
    h = rep("""    const raw = localStorage.getItem(CLAVE);
    if(raw){
      const d = JSON.parse(raw);
      ESTADO.personal = Array.isArray(d.personal)? d.personal : [];
      ESTADO.org      = d.org || clonar(ORG_SEMILLA);
      ESTADO.tema     = d.tema || "claro";
    }else{
      ESTADO.org = clonar(ORG_SEMILLA);
    }""",
            """    const raw = localStorage.getItem(CLAVE);
    if(raw) ESTADO.tema = (JSON.parse(raw).tema) || "claro";
    semillaIncorporada();""", "carga del padron")

    h = rep('function cargar(){',
            'function semillaIncorporada(){\n'
            '  try{\n'
            '    const d = JSON.parse(document.getElementById("datosIncorporados").textContent);\n'
            '    ESTADO.personal = Array.isArray(d.personal)? d.personal : [];\n'
            '    ESTADO.org      = d.org || clonar(ORG_SEMILLA);\n'
            '  }catch(e){\n'
            '    ESTADO.personal = []; ESTADO.org = clonar(ORG_SEMILLA);\n'
            '    console.warn("No se pudo leer el padr\u00f3n incorporado:", e);\n'
            '  }\n'
            '}\n\n'
            'function cargar(){', "funcion semillaIncorporada")

    # ---- 12. el navegador solo conserva la preferencia de tema (inmune al cupo)
    ini_g = h.index("let avisoCupo = false;\nfunction guardar(){")
    fin_g = h.index("async function escribirArchivo(paquete){")
    h = h[:ini_g] + (
      '/* Vista de consulta: el padr\u00f3n vive en el archivo, de modo que en el navegador\n'
      '   s\u00f3lo se conserva la preferencia de tema. As\u00ed ning\u00fan cupo puede recortar las fotograf\u00edas. */\n'
      'function guardar(){\n'
      '  try{ localStorage.setItem(CLAVE, JSON.stringify({v:1, tema:ESTADO.tema})); }catch(e){}\n'
      '}\n\n') + h[fin_g:]
    cambios.append("persistencia solo del tema")

    # ---- 13. el boton de carga restaura el padron incorporado
    ini = h.index('function cargarDemo(){')
    fin = h.index('  guardar(); pintarTodo(); toast("24 legajos de ejemplo cargados.");\n}\n')
    fin += len('  guardar(); pintarTodo(); toast("24 legajos de ejemplo cargados.");\n}\n')
    h = h[:ini] + (
      'function cargarDemo(){\n'
      '  semillaIncorporada();\n'
      '  ESTADO.nodoSel = null;\n'
      '  guardar(); pintarTodo();\n'
      '  toast(ESTADO.personal.length + " legajos cargados.");\n'
      '}\n') + h[fin:]
    cambios.append("cargarDemo")

    h = rep("""  $("#btnDemo").onclick = ()=>confirmar("Cargar datos de ejemplo",
    "Se reemplazarán todos los legajos actuales por 24 legajos ficticios de demostración.", cargarDemo);
  $("#btnBorrar").onclick = ()=>confirmar("Borrar todo",
    "Se eliminarán todos los legajos y se restaurará el organigrama. Exporte antes una copia de seguridad.", ()=>{
      ESTADO.personal=[]; ESTADO.org=clonar(ORG_SEMILLA); ESTADO.nodoSel=null;
      guardar(); pintarTodo(); toast("Datos borrados.");
    });""",
            '  $("#btnDemo").onclick = ()=>confirmar("Restaurar el padrón",\n'
            '    "La vista volverá a mostrar los %d legajos incorporados a este archivo.", cargarDemo);' % n,
            "boton del padron")

    # ---- 14. aviso de tablero sin datos
    h = rep("""    `<div class="aviso" style="margin-bottom:16px">Sin datos cargados. Se deberá ingresar a la solapa
     <b>Datos</b> y abrir el archivo <span class="mono">datos-personal.json</span> que acompaña a este board.
     En los navegadores que no admiten apertura directa de archivos se empleará <b>Importar JSON</b>.</div>`;""",
            '    `<div class="aviso" style="margin-bottom:16px">Sin datos a la vista. Se deberá ingresar a la solapa\n'
            '     <b>Datos</b> y presionar <b>Cargar %d legajos</b> para restaurar el padrón incorporado.</div>`;' % n,
            "aviso de inicio")

    # ---- 15. la ficha se abre en modo consulta
    h = rep('document.addEventListener("DOMContentLoaded", iniciar);',
            '/* ============================================================\n'
            '   14. MODO CONSULTA\n'
            '   ============================================================ */\n'
            'const abrirFichaOriginal = abrirLegajo;\n'
            'abrirLegajo = function(id){\n'
            '  if(!id) return;                       /* no hay altas en la vista de consulta */\n'
            '  abrirFichaOriginal(id);\n'
            '  $("#mTitulo").textContent = "Ficha — " + $("#mTitulo").textContent.replace(/^Legajo — /,"");\n'
            '  $$("#mCuerpo input, #mCuerpo select, #mCuerpo textarea, #mCuerpo button").forEach(c=>{\n'
            '    if(c.tagName==="BUTTON" || c.tagName==="SELECT" || c.type==="checkbox" ||\n'
            '       c.type==="radio" || c.type==="file" || c.type==="color") c.disabled = true;\n'
            '    else c.readOnly = true;\n'
            '  });\n'
            '};\n\n'
            'document.addEventListener("DOMContentLoaded", iniciar);', "modo consulta")

    # ---- 15 bis. resumen del padron en lugar del estado del almacenamiento
    ini_a = h.index("function pintarAlmacen(){")
    cierre = '    : ""}</p>`;\n}'
    fin_a = h.index(cierre, ini_a) + len(cierre)
    fecha = (datos.get("generado") or "")[:10] or "\u2014"
    h = h[:ini_a] + (
      'function pintarAlmacen(){\n'
      '  const fotos = ESTADO.personal.filter(p=>p.foto).length;\n'
      '  const conQr = ESTADO.personal.filter(p=>(p.qr||"").trim()).length;\n'
      '  $("#estadoAlmacen").innerHTML = `<dl class="dl">\n'
      '    <dt>Legajos incorporados</dt><dd>${ESTADO.personal.length}</dd>\n'
      '    <dt>Con fotograf\u00eda</dt><dd>${fotos}</dd>\n'
      '    <dt>Con QR de migraciones</dt><dd>${conQr}</dd>\n'
      '    <dt>Dependencias en el organigrama</dt><dd>${orgPlano().length}</dd>\n'
      '    <dt>Padr\u00f3n actualizado al</dt><dd>' + fecha + '</dd>\n'
      '  </dl>`;\n'
      '}') + h[fin_a:]
    cambios.append("resumen del padron")

    # ---- 16. padron incorporado al documento
    crudo = json.dumps({"v":1, "generado":datos.get("generado",""), "personal":P, "org":datos.get("org")},
                       ensure_ascii=False, separators=(",",":")).replace("</", "<\\/")
    h = rep('<script>',
            '<script id="datosIncorporados" type="application/json">' + crudo + '</script>\n<script>',
            "padron incorporado")

    io.open(salida, "w", encoding="utf-8").write(h)
    print("Generado:", salida)
    print("Legajos:", n, "| Sello:", sello)
    print("Cambios:", ", ".join(cambios))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
