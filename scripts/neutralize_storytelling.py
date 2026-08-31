from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def replace_once(text: str, old: str, new: str) -> str:
    if new in text:
        return text
    assert text.count(old) == 1, f"Ancla inesperada: {old[:90]}"
    return text.replace(old, new, 1)


text = INDEX.read_text(encoding="utf-8")

text = replace_once(
    text,
    "/* v170 · relato editorial navegable sobre el origen y los hallazgos del dashboard */",
    "/* v171 · relato editorial con hipótesis de partida y preguntas analíticas abiertas */",
)

css_anchor = "#tab-story .story-source-note{margin-top:0!important}"
css_addition = """#tab-story .story-source-note{margin-top:0!important}
#tab-story .story-hypothesis-journal{padding:24px;border:1px solid #ddcfe7;border-radius:22px;background:linear-gradient(145deg,rgba(255,255,255,.96),rgba(249,246,255,.94))}
#tab-story .story-hypothesis-head{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:18px;align-items:start;margin-bottom:14px}
#tab-story .story-hypothesis-head h2{margin:8px 0 6px;color:#60376f}.story-hypothesis-head p{max-width:820px;margin:0;color:#705b78;line-height:1.55}
#tab-story .story-hypothesis-rule{max-width:260px;padding:11px 13px;border:1px solid #d8c8e2;border-radius:14px;background:#fff;color:#735c7b;font-size:10px;line-height:1.5}
#tab-story .story-hypothesis-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
#tab-story .story-hypothesis-card{min-width:0;padding:15px;border:1px solid #e2d6e8;border-radius:16px;background:#fff}
#tab-story .story-hypothesis-card.caputo{grid-column:1/-1;border-color:#cfc2e8;background:linear-gradient(135deg,#fff,#f7f4ff)}
#tab-story .story-hypothesis-card small{display:block;color:#94769a;font-size:8px;font-weight:950;letter-spacing:.045em;text-transform:uppercase}
#tab-story .story-hypothesis-card h3{margin:5px 0 8px;color:#62416f;font-size:14px}
#tab-story .story-hypothesis-card p{margin:0 0 8px;color:#715e78;font-size:10px;line-height:1.5}
#tab-story .story-hypothesis-card .story-analysis-question{margin:0;padding:9px 10px;border-left:3px solid #9a73b4;border-radius:10px;background:#faf7fd;color:#604c68}
#tab-story .story-hypothesis-card.caputo .story-analysis-question{border-left-color:#67559a;background:#f3f0ff}
@media(max-width:900px){#tab-story .story-hypothesis-head{grid-template-columns:1fr}#tab-story .story-hypothesis-rule{max-width:none}}
@media(max-width:720px){#tab-story .story-hypothesis-journal{padding:17px 14px}#tab-story .story-hypothesis-grid{grid-template-columns:1fr}#tab-story .story-hypothesis-card.caputo{grid-column:auto}}"""
if 'id="story-hypotheses"' not in text:
    text = replace_once(text, css_anchor, css_addition)

text = replace_once(
    text,
    '        <a href="#story-origin">El origen</a>',
    '        <a href="#story-origin">El origen</a>\n        <a href="#story-hypotheses">Hipótesis de partida</a>',
)

hypothesis_html = """
      <section id="story-hypotheses" class="story-hypothesis-journal" aria-labelledby="story-hypotheses-title">
        <header class="story-hypothesis-head"><div><span class="story-eyebrow">Cuaderno de origen · no son resultados</span><h2 id="story-hypotheses-title">Las hipótesis e intuiciones que pusieron en marcha la épica</h2><p>Las dejamos registradas porque forman parte de la historia intelectual del dashboard. En los tabs analíticos se traducen a preguntas más amplias: la evidencia puede matizar una intuición, hacerla compatible con varias explicaciones o dejarla abierta.</p></div><aside class="story-hypothesis-rule"><b>Regla editorial</b><br>Storytelling = punto de partida de la autora.<br>Análisis = preguntas, mediciones, alternativas y límites.</aside></header>
        <div class="story-hypothesis-grid">
          <article class="story-hypothesis-card"><small>Intuición de partida · bienestar</small><h3>La estabilización podía convivir con fragilidad cotidiana</h3><p>La baja de inflación o pobreza no necesariamente implicaba que los hogares hubieran dejado de usar ahorro, deuda, cuotas o venta de patrimonio.</p><p class="story-analysis-question"><b>Pregunta analítica:</b> ¿cómo evolucionan ingreso, estrategias de sostenimiento, deuda, mora y pobreza para distintos hogares?</p></article>
          <article class="story-hypothesis-card"><small>Intuición de partida · distribución</small><h3>El costo del ajuste podía estar repartido de manera desigual</h3><p>El equilibrio fiscal agregado podía coexistir con transferencias de costo entre trabajadores, jubilados, usuarios, empresas, bancos y distintos niveles del Estado.</p><p class="story-analysis-question"><b>Pregunta analítica:</b> ¿qué flujos, stocks y servicios cambiaron, y sobre qué grupos incidió cada movimiento?</p></article>
          <article class="story-hypothesis-card"><small>Intuición de partida · frente externo</small><h3>Los dólares visibles podían no equivaler a liquidez utilizable</h3><p>Reservas brutas, reservas propias, superávit de bienes, cuenta corriente y vencimientos podían contar partes distintas de la misma restricción.</p><p class="story-analysis-question"><b>Pregunta analítica:</b> ¿qué stocks y flujos componen la posición externa y bajo qué condiciones están disponibles?</p></article>
          <article class="story-hypothesis-card"><small>Intuición de partida · desarrollo</small><h3>Anuncios, inversión ejecutada y empleo podían no avanzar juntos</h3><p>Una reforma o aprobación podía ser un input relevante sin constituir todavía producción, infraestructura o trabajo permanente.</p><p class="story-analysis-question"><b>Pregunta analítica:</b> ¿qué etapa alcanzó cada proyecto y qué resultados observables aparecen después?</p></article>
          <article class="story-hypothesis-card"><small>Intuición de partida · fiscalidad</small><h3>Bajar impuestos podía cambiar quién financia al Estado sin autofinanciarse por completo</h3><p>La expansión de la base, la formalización y la recaudación podían responder de manera distinta según impuesto, sujeto y ciclo económico.</p><p class="story-analysis-question"><b>Pregunta analítica:</b> ¿qué tributos cambian, quiénes quedan alcanzados y cómo evolucionan base, alícuota y recaudación real?</p></article>
          <article class="story-hypothesis-card"><small>Intuición de partida · crédito</small><h3>Más crédito podía ser inclusión y también una fuente de estrés</h3><p>La experiencia dependía de ingreso, tasa, plazo, selección, destino y posición financiera; ahorristas y deudores no eran intercambiables.</p><p class="story-analysis-question"><b>Pregunta analítica:</b> ¿cómo se relacionan acceso, precio, capacidad de pago, exposición y mora sin confundir costo con utilidad?</p></article>
          <article class="story-hypothesis-card caputo"><small>Hipótesis de Miyu · Caputo y los dólares del colchón</small><h3>La insistencia oficial podía no coincidir con el incentivo privado del ahorrista</h3><p>Mi intuición inicial fue que no todos “los argentinos” tienen dólares invertibles; que una cuenta comitente y activos externos seguros podían resultar más atractivos que el banco local; y que la insistencia del Gobierno podía responder a necesidades macroeconómicas más urgentes que la frase pública dejaba ver.</p><p class="story-analysis-question"><b>Traducción neutral en el análisis:</b> ¿cómo se distribuye la capacidad de ahorro?, ¿qué atributos y costos tiene cada canal?, ¿qué objetivos declara la política?, ¿qué mecanismos, beneficiarios y restricciones aparecen?</p><div class="story-links"><button class="story-link" type="button" onclick="activateTab('tab-epica-caputo-colchon')">Explorar dólares del colchón →</button></div></article>
        </div>
      </section>

"""
if '<section id="story-hypotheses"' not in text:
    text = replace_once(text, '      <div class="story-timeline">', hypothesis_html + '      <div class="story-timeline">')

neutral_replacements = {
    "Un dato que contradice una frase anterior no se esconde: cambia la frase.": "Un dato que cambia una lectura anterior no se esconde: obliga a reformularla.",
    "Cruzar dos trabajos no sirve si el otro sólo confirma lo que ya pensábamos. Sirve cuando también nos obliga a corregirnos.": "Cruzar dos trabajos no sirve si uno sólo repite la lectura inicial. Sirve cuando amplía las preguntas y vuelve visibles los límites de ambos.",
    "El dato que contradijo mis expectativas": "El dato que cambió mi lectura inicial",
    "apareció un dato que realmente contradecía mis expectativas": "apareció un dato que no coincidía con mi lectura inicial",
    "Si contradecía mi hipótesis, también.": "Si no coincidía con mi expectativa, también.",
    "Cada gráfico agregaba una pieza y, en algunos casos, obligaba a corregir conclusiones anteriores.": "Cada gráfico agregaba una pieza y, en algunos casos, obligaba a afinar lecturas anteriores.",
    "<b>Mostrar la contradicción</b>No borrar el dato que complica la propia interpretación.": "<b>Mostrar la complejidad</b>No borrar el dato que amplía o complica la interpretación inicial.",
    "auditoría empírica · causal · adversarial": "análisis empírico · causal · comparativo",
    "La pregunta no es elegir una narrativa cómoda. Intentamos refutar y defender por igual tres familias de explicación:": "La pregunta es qué información aporta y qué límites tiene cada una de tres familias de explicación:",
    "VEREDICTO MÁS DEFENDIBLE": "LECTURA INTEGRADA MÁS COMPATIBLE",
    "Matriz adversarial · qué sobrevive al intento de refutación": "Matriz comparativa · evidencia y límites de cada explicación",
    "veredictos sobre frases fuertes": "alcance de afirmaciones fuertes",
    "⚖️ Ciclo del ajuste · veredicto V70": "⚖️ Ciclo del ajuste · síntesis V70",
}
for old, new in neutral_replacements.items():
    text = replace_once(text, old, new)

INDEX.write_text(text, encoding="utf-8", newline="\n")
print("OK: storytelling registra hipótesis y los análisis usan preguntas neutrales")
