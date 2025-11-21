"""
Content Generator - PcComponentes
Versión 2.1 con mejoras:
- Producto alternativo opcional
- Casos de uso configurables
- Módulos dinámicos con garantía de aparición
"""

import streamlit as st
import anthropic
import requests
import json
import time
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

st.set_page_config(
    page_title="Content Generator | PcComponentes",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SCRAPING N8N
# ============================================================================

def scrape_pdp_n8n(product_id):
    """
    Scrapea PDP usando webhook n8n
    IMPORTANTE: Requiere estar conectado a VPN
    """
    try:
        webhook_url = "https://n8n.prod.pccomponentes.com/webhook/extract-product-data"
        
        response = requests.post(
            webhook_url,
            json={"productId": product_id},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error en webhook: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("No se puede conectar al webhook. Conecta a la VPN")
        return None
    except Exception as e:
        st.error(f"Error scrapeando PDP: {str(e)}")
        return None

def get_mock_pdp_data(product_id):
    """Datos mock para testing sin VPN"""
    return {
        "productId": product_id,
        "nombre": "Xiaomi Robot Vacuum E5 Robot con Función de Aspiración y Fregado",
        "precio_actual": "59.99",
        "precio_anterior": "64.99",
        "descuento": "-7%",
        "valoracion": "4.1",
        "num_opiniones": "112",
        "badges": ["Precio mínimo histórico"],
        "url_producto": f"https://www.pccomponentes.com/producto/{product_id}",
        "especificaciones": {
            "potencia_succion": "2000Pa",
            "navegacion": "Giroscopio + sensores IR",
            "bateria": "2600 mAh",
            "autonomia": "110 minutos",
            "deposito_polvo": "400 ml",
            "deposito_agua": "90 ml",
            "altura": "70 mm",
            "conectividad": "WiFi 2.4GHz",
            "control_voz": "Alexa, Google Assistant",
            "fregado": "Sí (mopa incluida)"
        },
        "descripcion": "Olvida la limpieza manual: aspira y friega con eficiencia, gestión desde tu móvil y acabado impecable en todo tipo de suelos.",
        "opiniones_resumen": [
            "Calidad-precio de 10. Es ligero, hace poco ruido y la app es muy sencilla de ejecutar.",
            "Aspira muy bien en suelos duros. El fregado es perfecto para mantenimiento diario.",
            "El perfil bajo de 70mm es genial para limpiar debajo de muebles.",
            "No mapea por habitaciones pero limpia toda la superficie eficientemente."
        ]
    }

# ============================================================================
# ARQUETIPOS COMPLETOS
# ============================================================================

ARQUETIPOS = {
    "ARQ-4": {
        "code": "ARQ-4",
        "name": "Review / Análisis",
        "description": "Análisis profundo de producto único con pros, contras y veredicto",
        "funnel": "Middle",
        "default_length": 1800,
        "use_case": "Producto único destacado - Black Friday, lanzamientos, ofertas especiales"
    },
    "ARQ-5": {
        "code": "ARQ-5",
        "name": "Comparativa A vs B",
        "description": "Comparación directa entre 2-3 productos similares",
        "funnel": "Middle",
        "default_length": 1600,
        "use_case": "Ayudar a elegir entre alternativas directas"
    },
    "ARQ-7": {
        "code": "ARQ-7",
        "name": "Roundup / Mejores X",
        "description": "Top X productos en una categoría",
        "funnel": "Middle",
        "default_length": 2200,
        "use_case": "Lista categoría - Black Friday, guías de compra"
    },
    "ARQ-8": {
        "code": "ARQ-8",
        "name": "Por presupuesto",
        "description": "Mejores productos por menos de X€",
        "funnel": "Bottom",
        "default_length": 1600,
        "use_case": "Chollos en rango de precio específico"
    },
    "ARQ-10": {
        "code": "ARQ-10",
        "name": "Por perfil de usuario",
        "description": "Productos perfectos para un tipo específico de usuario",
        "funnel": "Middle",
        "default_length": 1800,
        "use_case": "Segmentación por audiencia (gamers, estudiantes, profesionales)"
    }
}

# ============================================================================
# TONO DE MARCA
# ============================================================================

BRAND_TONE = """
# Manual de Tono - PcComponentes

## TONO ASPIRACIONAL (NO NEGATIVO)

### HACER:
- Enfoca en beneficios y soluciones
- "Perfecto si..." en lugar de "Evita si..."
- "Considera alternativas si..." SOLO si hay producto alternativo configurado
- Honestidad aspiracional: refuerza lo positivo sin mentir
- Traduce limitaciones en contexto útil

### Ejemplos de tono correcto:
INCORRECTO: "Este producto no tiene mapeo por habitaciones"
CORRECTO: "Limpia toda tu casa con navegación inteligente; si necesitas control por habitaciones, hay modelos con láser"

INCORRECTO: "No recomendado para perros grandes"
CORRECTO: "Perfecto con mascotas estándar; con razas grandes de pelo largo, funciona bien pero el cepillo necesitará limpieza más frecuente"

## PERSONALIDAD:
- Expertos sin pedantería
- Frikis sin vergüenza
- Honestos pero no aburridos
- Cercanos pero profesionales

## EMOJIS PERMITIDOS:
- ✅ Para puntos positivos
- ⚡ Para destacar urgencia o velocidad
- ❌ SOLO en tablas comparativas técnicas (no para disuadir)
"""

# ============================================================================
# EJEMPLOS DE REFERENCIA
# ============================================================================

EJEMPLOS_CSS = """
Usa ESTOS estilos como referencia (paleta PcComponentes):

<style>
body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #090029;
  background-color: #FFFFFF;
  line-height: 1.6;
}
h1, h2, h3 {
  color: #170453;
  margin-top: 1.2em;
  margin-bottom: 0.6em;
  font-weight: 800;
}
h1 { font-size: 2em; }
h2 { font-size: 1.5em; }
h3 { font-size: 1.25em; }

.kicker {
  display: inline-block;
  background-color: #C5C0D4;
  color: #170453;
  border: 1px solid #170453;
  padding: 0.25em 0.6em;
  margin-bottom: 0.8em;
  font-size: 0.75em;
  font-weight: 700;
  border-radius: 999px;
}

.badges {
  margin: 0.8em 0;
  display: flex;
  gap: 0.5em;
  flex-wrap: wrap;
}
.badge {
  display: inline-block;
  background-color: #FFFFFF;
  color: #62697A;
  border: 1px solid #E6E6E6;
  padding: 0.25em 0.6em;
  font-size: 0.75em;
  border-radius: 999px;
}

.callout {
  border-left: 4px solid #FF8640;
  background-color: #F4F4F4;
  padding: 0.8em 1em;
  margin: 1.2em 0;
}
.callout strong { color: #170453; }

.callout-accent {
  border-left: 4px solid #FF6000;
  background-color: #FFAE80;
  padding: 0.8em 1em;
  margin: 1.2em 0;
}

.toc {
  border: 1px dashed #E6E6E6;
  background-color: #FFFFFF;
  padding: 1em;
  margin: 1.2em 0;
  border-radius: 6px;
}
.toc h2 { margin-top: 0; font-size: 1em; font-weight: 800; }
.toc ul { list-style: none; padding-left: 0; margin: 0; }
.toc li { padding: 0.4em 0; border-bottom: 1px dashed #E6E6E6; }
.toc li:last-child { border-bottom: none; }
.toc a { color: #62697A; text-decoration: none; }
.toc a:hover { color: #170453; }

.verdict {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #FFFFFF;
  padding: 1.2em;
  margin: 1.2em 0;
  border-radius: 10px;
}
.verdict h3 { color: #FFFFFF; margin-top: 0; }
.verdict-grid { display: grid; gap: 1em; margin-top: 1em; }
@media(min-width:768px){ .verdict-grid { grid-template-columns: 1fr 1fr; }}
.verdict-item {
  background-color: rgba(255,255,255,0.1);
  padding: 0.8em;
  border-radius: 6px;
}

.grid { display: grid; gap: 1em; margin: 1.2em 0; }
@media(min-width:768px){
  .grid.cols-2 { grid-template-columns: 1fr 1fr; }
  .grid.cols-3 { grid-template-columns: repeat(3, 1fr); }
}
.card {
  border: 1px solid #D9D9D9;
  padding: 1em;
  background-color: #FFFFFF;
  border-radius: 6px;
}
.card h4 { margin-top: 0; color: #170453; }
.card .why { color: #62697A; font-size: 0.875em; margin: 0; }

.lt {
  border: 1px solid #E6E6E6;
  border-radius: 0;
  overflow: hidden;
  background-color: #FFFFFF;
  margin: 1em 0;
}
.lt .r { display: grid; border-top: 1px solid #E6E6E6; }
.lt .r:first-child { border-top: none; background-color: #F4F4F4; font-weight: 800; }
.lt .c { padding: 0.6em; }
.lt.zebra .r:nth-child(odd):not(:first-child) { background-color: #FCFCFD; }
.lt.cols-2 .r { grid-template-columns: 1.4fr 0.6fr; }
.lt.cols-3 .r { grid-template-columns: 1fr 1fr 1fr; }

.btns { display: flex; gap: 0.6em; flex-wrap: wrap; margin: 1.2em 0; }
.btn {
  display: inline-block;
  text-decoration: none;
  color: #FFFFFF;
  background-color: #FF6000;
  padding: 0.6em 1.2em;
  border-radius: 6px;
  font-weight: 700;
  border: 1px solid #FF6000;
}
.btn:hover { transform: translateY(-1px); }
.btn.ghost {
  background-color: #FFFFFF;
  color: #090029;
  border: 1px solid #E6E6E6;
}

.hr { height: 1px; background-color: #E6E6E6; margin: 1.5em 0; border: none; }
.note { color: #62697A; font-size: 0.875em; }
</style>
"""

# ============================================================================
# PROMPT BUILDER
# ============================================================================

def build_generation_prompt(pdp_data, arquetipo, length, keywords, context, links, modules, objetivo, producto_alternativo, casos_uso):
    """Construye prompt para generación inicial"""
    
    keywords_str = ", ".join(keywords) if keywords else "No especificadas"
    
    # Preparar información de enlaces
    link_principal = links.get('principal', {})
    links_secundarios = links.get('secundarios', [])
    
    link_info = ""
    if link_principal.get('url'):
        link_info = f"""
# ENLACES A INCLUIR:

## Enlace Principal (OBLIGATORIO):
URL: {link_principal.get('url')}
Texto anchor: {link_principal.get('text')}
Ubicación: Debe aparecer en los primeros 2-3 párrafos del contenido, integrado naturalmente
"""
    
    if links_secundarios:
        link_info += f"""
## Enlaces Secundarios Contextuales:
{chr(10).join([f"- URL: {link.get('url')} | Texto: {link.get('text')}" for link in links_secundarios])}
Ubicación: Integra naturalmente donde mejor encajen en el texto
"""

    # Preparar información de producto alternativo
    alternativo_info = ""
    if producto_alternativo.get('url'):
        alternativo_info = f"""
# PRODUCTO ALTERNATIVO (CONFIGURADO):

URL Alternativa: {producto_alternativo.get('url')}
Texto del producto: {producto_alternativo.get('text', 'producto alternativo')}

IMPORTANTE: Dado que hay un producto alternativo configurado, el box de veredicto DEBE incluir:

<div class="verdict-grid">
<div class="verdict-item">
<strong>✅ Perfecto si:</strong>
<p class="why">[Beneficios clave del producto principal]</p>
</div>
<div class="verdict-item">
<strong>Considera alternativas si:</strong>
<p class="why">[Situaciones donde el producto alternativo puede ser mejor. Incluye enlace: <a href="{producto_alternativo.get('url')}" style="color: #FFFFFF; text-decoration: underline;">{producto_alternativo.get('text')}</a>]</p>
</div>
</div>
"""
    else:
        # Si NO hay producto alternativo, solo "Perfecto si" expandido
        casos_uso_str = ""
        if casos_uso:
            casos_uso_str = f"\nCasos de uso a mencionar:\n" + "\n".join([f"- {caso}" for caso in casos_uso])
        
        alternativo_info = f"""
# PRODUCTO ALTERNATIVO (NO CONFIGURADO):

IMPORTANTE: NO hay producto alternativo configurado, por lo tanto el box de veredicto DEBE ser:

<div class="verdict-grid">
<div class="verdict-item" style="grid-column: 1 / -1;">
<strong>✅ Perfecto si:</strong>
<p class="why">[Desarrolla EXTENSAMENTE los beneficios y casos de uso del producto. Debe ser detallado con múltiples escenarios donde el producto brilla.{casos_uso_str}]</p>
</div>
</div>

NO incluyas sección "Considera alternativas si" ya que no hay producto alternativo configurado.
"""

    # Preparar información de módulos
    module_info = ""
    if modules:
        module_info = f"""
# MÓDULOS DE PRODUCTOS (OBLIGATORIOS SI CONFIGURADOS):

Productos a destacar con módulos:
{chr(10).join([f"- ID: {m['id']} (Nombre: {m.get('nombre', 'Sin nombre')})" for m in modules])}

Formato EXACTO del módulo:
#MODULE_START#|{{"type":"article","params":{{"articleId":"{modules[0]['id']}"}}}}|#MODULE_END#

CRÍTICO sobre módulos:
- Estos módulos DEBEN aparecer en el contenido final
- Usa el formato EXACTO mostrado arriba
- Ubicación típica: después de mencionar el producto o en secciones de análisis/comparativa
- Cada módulo debe estar en su propia línea
- NO modifiques el formato JSON del módulo
- Si hay múltiples módulos, inclúyelos todos en ubicaciones estratégicas

Ejemplo de cómo integrar un módulo en el texto:

<p>El Xiaomi Robot Vacuum E5 ofrece una excelente relación calidad-precio...</p>

#MODULE_START#|{{"type":"article","params":{{"articleId":"10869987"}}}}|#MODULE_END#

<p>Con su potencia de succión de 2000Pa...</p>
"""

    prompt = f"""
Eres un experto redactor de PcComponentes especializado en crear contenido optimizado para Google Discover.

# OBJETIVO PRINCIPAL DEL CONTENIDO:
{objetivo}

# TONO DE MARCA PCCOMPONENTES:
{BRAND_TONE}

# ARQUETIPO SELECCIONADO:
{arquetipo['code']} - {arquetipo['name']}
Descripción: {arquetipo['description']}
Caso de uso: {arquetipo['use_case']}

# DATOS DEL PRODUCTO:
{json.dumps(pdp_data, indent=2, ensure_ascii=False)}

# CONTEXTO ADICIONAL:
{context if context else "Condiciones estándar PcComponentes: envío gratis +50€, devoluciones extendidas"}

# KEYWORDS SEO OBJETIVO:
{keywords_str}

# LONGITUD OBJETIVO:
{length} palabras aproximadamente

{link_info}

{alternativo_info}

{module_info}

# INSTRUCCIONES CRÍTICAS DE REDACCIÓN:

## 1. FORMATO DEL OUTPUT:

Genera SOLO el artículo (desde <style> hasta </article>). 
NO incluyas <html>, <head>, <body> ni nada externo al artículo.

Estructura:

{EJEMPLOS_CSS}

<article>
<span class="kicker">[Categoría]</span>
<h2>[Título optimizado]</h2>

<div class="badges">
<span class="badge">[Spec clave 1]</span>
<span class="badge">[Spec clave 2]</span>
</div>

<div class="verdict">
<h3><strong>⚡ Veredicto rápido</strong></h3>
[Aquí va el verdict-grid según configuración de producto alternativo]
</div>

<div class="toc">
<strong>Índice</strong>
<ul>
<li><a href="#seccion1">[Sección 1]</a></li>
<li><a href="#seccion2">[Sección 2]</a></li>
</ul>
</div>

[CONTENIDO SEGÚN ARQUETIPO]

[MÓDULOS DE PRODUCTOS EN UBICACIONES ESTRATÉGICAS]

<h2 id="faqs">Preguntas frecuentes</h2>
[FAQs relevantes con H3 para cada pregunta]

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "[Pregunta]",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "[Respuesta]"
      }}
    }}
  ]
}}
</script>
</article>

## 2. TONO ASPIRACIONAL (CRÍTICO):

✅ SIEMPRE enfoca en beneficios y soluciones
✅ Usa "Perfecto si..." 
✅ Si hay producto alternativo: usa "Considera alternativas si..." con enlace
✅ Si NO hay alternativo: desarrolla extensamente "Perfecto si" con múltiples casos de uso

❌ PROHIBIDO lenguaje negativo que desanime
❌ PROHIBIDO "evita", "no compres", "no recomendado"
❌ PROHIBIDO tecnicismos sin explicar

## 3. EMOJIS (SOLO ESTOS):

✅ Para ventajas y puntos positivos
⚡ Para urgencia, velocidad, destacar
❌ SOLO en tablas comparativas técnicas (no para disuadir)

## 4. ENLACES:

- Enlace principal: intégralo NATURALMENTE en los primeros párrafos
- Enlaces secundarios: donde encajen mejor contextualmente
- Producto alternativo: DEBE aparecer en "Considera alternativas si" si está configurado
- Usa anchor text descriptivo (nunca "clic aquí" o "este enlace")

## 5. MÓDULOS DE PRODUCTOS (CRÍTICO):

Si hay módulos configurados:
- DEBEN aparecer en el contenido final
- Usa el formato EXACTO proporcionado
- NO modifiques el formato JSON
- Ubícalos estratégicamente donde aporten valor
- Cada módulo en su propia línea

## 6. ESTRUCTURA SEGÚN ARQUETIPO:

ARQ-4 (Review): 
- Veredicto rápido
- Contexto de la oferta
- Especificaciones técnicas explicadas
- Rendimiento real con datos
- Opiniones de usuarios reales
- Comparativa con competencia
- FAQs
- Veredicto final

ARQ-5 (Comparativa):
- Intro con criterios
- Producto A análisis
- Producto B análisis
- Tabla comparativa visual
- Veredicto: cuál elegir según perfil

ARQ-7 (Roundup):
- Criterios de selección
- Análisis producto 1
- Análisis producto 2-N
- Tabla comparativa
- Guía de compra
- Conclusión

ARQ-8 (Por presupuesto):
- Por qué este rango de precio
- Mejor calidad-precio
- Alternativas en el rango
- Comparativa rápida
- Cómo elegir

ARQ-10 (Por perfil):
- Perfil de usuario detallado
- Por qué este producto encaja
- Soluciones específicas
- Alternativas si perfil varía
- Recomendación final

## 7. ELEMENTOS OBLIGATORIOS:

✅ Kicker con categoría del producto
✅ Título H2 (NO H1) con beneficio claro
✅ Badges con specs clave
✅ Box de veredicto con gradiente morado (formato según alternativo)
✅ TOC navegable con anchors
✅ Callouts estratégicos (.callout, .callout-accent)
✅ Tablas con clase .lt para comparativas
✅ Botones CTA con clase .btn
✅ FAQs al final del contenido
✅ Schema JSON-LD FAQPage válido
✅ Links directos al producto (URL completa)
✅ MÓDULOS de productos si están configurados

## 8. CALIDAD DEL CONTENIDO:

- Datos específicos y verificables (no vaguedades)
- Ejemplos concretos y útiles
- Traduce tecnicismos ("2000Pa = aspira migas y pelos sin problema")
- CTAs claros y directos
- Comparativas justas con competencia
- Opiniones de usuarios integradas naturalmente

Genera AHORA el contenido completo del artículo.
"""
    
    return prompt

def build_correction_prompt(content, objetivo):
    """Construye prompt para corrección crítica"""
    
    prompt = f"""
Eres un editor senior de PcComponentes. Analiza este contenido con mirada crítica profesional.

# OBJETIVO DEL CONTENIDO:
{objetivo}

# CONTENIDO A REVISAR:
{content}

# CRITERIOS DE CORRECCIÓN CRÍTICA:

## 1. Alineación con objetivo:
- ¿Cumple el objetivo establecido?
- ¿Hay desviaciones innecesarias?
- ¿El enfoque es el correcto?

## 2. Tono aspiracional (CRÍTICO):
- ¿Se usa lenguaje negativo o disuasorio?
- ¿Las limitaciones tienen contexto útil?
- ¿Se enfoca en soluciones y beneficios?
- ¿Frases como "no compres", "evita", "no recomendado"?

## 3. Emojis:
- ¿Solo usa ✅ ⚡ ❌?
- ¿Están bien utilizados según las reglas?

## 4. Enlaces:
- ¿Enlace principal en primeros párrafos?
- ¿Enlaces secundarios bien integrados?
- ¿Producto alternativo presente si está configurado?
- ¿Anchor text descriptivo y natural?

## 5. Módulos de productos (CRÍTICO):
- ¿Aparecen TODOS los módulos configurados?
- ¿Formato EXACTO: #MODULE_START#|{{"type":"article",...}}|#MODULE_END#?
- ¿Ubicación estratégica?
- ¿Cada módulo en su propia línea?

## 6. Veredicto:
- Si hay alternativo: ¿dos columnas con enlace?
- Si NO hay alternativo: ¿una columna expandida con casos de uso?

## 7. Estructura técnica:
- ¿Todos los elementos obligatorios presentes?
- ¿CSS correcto con paleta PcComponentes?
- ¿TOC con anchors funcionando?
- ¿Schema JSON-LD válido?

## 8. Optimización Discover:
- ¿Título atractivo con beneficio claro?
- ¿Hook emocional en apertura?
- ¿Elementos visuales (tablas, boxes)?
- ¿Datos específicos y verificables?

## 9. Calidad contenido:
- ¿Tecnicismos explicados?
- ¿Ejemplos concretos?
- ¿CTAs claros?
- ¿Comparativas justas?

# PROPORCIONA:

## Resumen ejecutivo:
[3-4 líneas sobre estado general del contenido]

## Correcciones CRÍTICAS (obligatorias):
[Lista numerada de cambios que DEBEN aplicarse]

## Sugerencias de mejora (opcionales):
[Optimizaciones que elevarían calidad]

## Alineación con objetivo:
[¿Cumple el objetivo? ¿Qué ajustar?]

## Verificación de módulos:
[¿Están presentes todos los módulos configurados? ¿Formato correcto?]

## Nota sobre tono:
[Evalúa específicamente si el tono es aspiracional o hay lenguaje negativo]

Sé específico, directo y enfócate en mejoras de alto impacto.
"""
    
    return prompt

def build_final_prompt(initial_content, corrections):
    """Construye prompt para versión final"""
    
    prompt = f"""
Genera la versión FINAL del contenido aplicando TODAS las correcciones críticas.

# CONTENIDO INICIAL:
{initial_content}

# CORRECCIONES CRÍTICAS A APLICAR:
{corrections}

# INSTRUCCIONES:

1. Aplica TODAS las correcciones mencionadas como críticas
2. Mantén la estructura completa del artículo (desde <style> hasta </article>)
3. Asegura tono aspiracional en todo el contenido
4. Verifica que TODOS los elementos obligatorios están presentes
5. CRÍTICO: Verifica que TODOS los módulos configurados aparecen con formato EXACTO
6. Optimiza para máximo impacto y conversión

IMPORTANTE: El output debe ser el artículo completo corregido, listo para publicar.

Genera el artículo final AHORA.
"""
    
    return prompt

# ============================================================================
# GENERADOR
# ============================================================================

class ContentGenerator:
    """Generador con corrección crítica en 2 pasos"""
    
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate(self, prompt, max_tokens=8000):
        """Llama a Claude API"""
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            st.error(f"Error en Claude API: {str(e)}")
            return None

# ============================================================================
# UI
# ============================================================================

def render_sidebar():
    """Sidebar con info"""
    with st.sidebar:
        st.markdown("## Content Generator")
        st.markdown("**PcComponentes**")
        st.markdown("---")
        
        st.markdown("### Recursos")
        st.markdown("[Guía arquetipos](#)")
        st.markdown("[Manual tono](#)")
        st.markdown("---")
        st.markdown("### Info")
        st.markdown("Versión 2.1 Mejorada")
        st.markdown("© 2025")

def main():
    """App principal"""
    
    render_sidebar()
    
    # Header
    st.title("Content Generator")
    st.markdown("Genera contenido optimizado para Google Discover")
    st.markdown("---")
    
    # Verificar API key
    if 'ANTHROPIC_API_KEY' not in st.secrets:
        st.error("Configura ANTHROPIC_API_KEY en secrets")
        st.stop()
    
    # SECCIÓN 1: Producto
    st.header("1. Producto")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        product_id = st.text_input(
            "ID del producto",
            placeholder="10848823",
            help="ID numérico del producto en PcComponentes"
        )
    
    with col2:
        use_mock = st.checkbox("Datos ejemplo", value=True, help="Testing sin VPN")
    
    # SECCIÓN 2: Arquetipo y objetivo
    st.header("2. Configuración")
    
    col1, col2 = st.columns(2)
    
    with col1:
        arquetipo_code = st.selectbox(
            "Arquetipo",
            options=list(ARQUETIPOS.keys()),
            format_func=lambda x: f"{ARQUETIPOS[x]['code']} - {ARQUETIPOS[x]['name']}"
        )
        arquetipo = ARQUETIPOS[arquetipo_code]
        
        st.info(f"**{arquetipo['name']}**\n\n{arquetipo['description']}\n\n*Caso de uso:* {arquetipo['use_case']}")
    
    with col2:
        content_length = st.slider(
            "Longitud (palabras)",
            min_value=800,
            max_value=3000,
            value=arquetipo['default_length'],
            step=100
        )
    
    # Objetivo del contenido (CRÍTICO)
    objetivo = st.text_area(
        "Objetivo del contenido (OBLIGATORIO)",
        placeholder="Ej: Convertir usuarios indecisos en compradores destacando el precio histórico y urgencia Black Friday. El contenido debe resolver dudas sobre calidad-precio y comparar con competencia.",
        help="Describe qué quieres lograr. La IA usará esto para corrección crítica",
        height=100
    )
    
    if not objetivo:
        st.warning("⚠️ El objetivo del contenido es obligatorio para la corrección crítica")
    
    # SECCIÓN 3: Configuración avanzada
    with st.expander("⚙️ Configuración Avanzada", expanded=False):
        
        # Keywords
        keywords = st.text_input(
            "Keywords SEO (separadas por comas)",
            placeholder="robot aspirador xiaomi, oferta black friday"
        )
        
        # Contexto
        context = st.text_area(
            "Contexto adicional",
            placeholder="Stock limitado 50 unidades, válido hasta 30/11, envío express gratis...",
            height=80
        )
        
        st.markdown("---")
        
        # Producto Alternativo (NUEVO)
        st.markdown("### 🔄 Producto Alternativo (Opcional)")
        st.caption("Si configuras un producto alternativo, aparecerá en 'Considera alternativas si...'")
        
        col1, col2 = st.columns(2)
        with col1:
            alternativo_url = st.text_input(
                "URL producto alternativo",
                help="Aparecerá en 'Considera alternativas si...'"
            )
        with col2:
            alternativo_text = st.text_input(
                "Texto del producto alternativo",
                placeholder="Ej: Roborock S7",
                help="Nombre descriptivo del producto"
            )
        
        # Casos de uso (NUEVO)
        st.markdown("### 📋 Casos de Uso (Opcional)")
        st.caption("Define casos de uso específicos para 'Perfecto si...' (uno por línea)")
        
        casos_uso_text = st.text_area(
            "Casos de uso",
            placeholder="Tienes un piso pequeño-mediano (hasta 80m²)\nBuscas limpieza diaria de mantenimiento\nTienes mascotas que sueltan pelo\nQuieres control desde el móvil",
            help="Cada línea será un caso de uso diferente",
            height=100
        )
        
        casos_uso = [caso.strip() for caso in casos_uso_text.split('\n') if caso.strip()] if casos_uso_text else []
        
        st.markdown("---")
        
        # Enlaces
        st.markdown("### 🔗 Enlaces")
        
        col1, col2 = st.columns(2)
        with col1:
            link_principal_url = st.text_input("URL enlace principal", help="Aparecerá en primeros párrafos")
        with col2:
            link_principal_text = st.text_input("Texto enlace principal", help="Anchor text descriptivo")
        
        st.markdown("**Enlaces secundarios** (hasta 3)")
        links_secundarios = []
        for i in range(3):
            col1, col2 = st.columns(2)
            with col1:
                url = st.text_input(f"URL secundario {i+1}", key=f"sec_url_{i}")
            with col2:
                text = st.text_input(f"Texto secundario {i+1}", key=f"sec_text_{i}")
            
            if url and text:
                links_secundarios.append({"url": url, "text": text})
        
        st.markdown("---")
        
        # Módulos de productos (MEJORADO - DINÁMICO)
        st.markdown("### 📦 Añadir Productos Destacados")
        st.caption("Los módulos aparecerán SIEMPRE en el contenido si completas el ID")
        
        # Inicializar estado para módulos si no existe
        if 'num_modules' not in st.session_state:
            st.session_state.num_modules = 1
        
        modules = []
        for i in range(st.session_state.num_modules):
            col1, col2 = st.columns([2, 1])
            with col1:
                module_id = st.text_input(
                    f"ID producto destacado {i+1}",
                    key=f"module_id_{i}",
                    help="articleId del producto"
                )
            with col2:
                module_nombre = st.text_input(
                    f"Nombre (opcional)",
                    key=f"module_nombre_{i}",
                    placeholder="Ej: Xiaomi E5"
                )
            
            if module_id:
                modules.append({
                    "id": module_id,
                    "nombre": module_nombre if module_nombre else f"Producto {i+1}"
                })
        
        # Botones para añadir/quitar módulos
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Añadir módulo", key="add_module"):
                st.session_state.num_modules += 1
                st.rerun()
        
        with col2:
            if st.session_state.num_modules > 1:
                if st.button("➖ Quitar último", key="remove_module"):
                    st.session_state.num_modules -= 1
                    st.rerun()
        
        if modules:
            st.success(f"✅ {len(modules)} módulo(s) configurado(s) - Aparecerán en el contenido")
    
    # Botón generar
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate = st.button(
            "🚀 Generar Contenido",
            type="primary",
            use_container_width=True,
            disabled=not product_id or not objetivo
        )
    
    # Proceso de generación
    if generate:
        
        # Obtener datos PDP
        if use_mock:
            pdp_data = get_mock_pdp_data(product_id)
            st.info("ℹ️ Usando datos de ejemplo (activa VPN para datos reales)")
        else:
            with st.spinner("🔄 Conectando al webhook n8n (requiere VPN)..."):
                pdp_data = scrape_pdp_n8n(product_id)
            
            if not pdp_data:
                st.error("❌ No se pudieron obtener datos del producto. Verifica VPN y product ID.")
                st.stop()
            
            st.success("✅ Datos del producto obtenidos correctamente")
        
        # Preparar datos
        keywords_list = [k.strip() for k in keywords.split(",")] if keywords else []
        
        links = {
            "principal": {"url": link_principal_url, "text": link_principal_text} if link_principal_url else {},
            "secundarios": links_secundarios
        }
        
        producto_alternativo = {
            "url": alternativo_url,
            "text": alternativo_text
        } if alternativo_url else {}
        
        # Inicializar generador
        generator = ContentGenerator(st.secrets['ANTHROPIC_API_KEY'])
        
        # Progress bar
        progress = st.progress(0)
        status = st.status("⏳ Generando contenido...", expanded=True)
        
        # PASO 1: Generación inicial
        status.write("📝 Paso 1/3: Generando contenido inicial...")
        prompt_gen = build_generation_prompt(
            pdp_data, arquetipo, content_length,
            keywords_list, context, links, modules, objetivo,
            producto_alternativo, casos_uso
        )
        
        initial_content = generator.generate(prompt_gen)
        if not initial_content:
            st.error("❌ Error en generación inicial")
            st.stop()
        
        progress.progress(40)
        time.sleep(0.5)
        
        # PASO 2: Corrección crítica
        status.write("🔍 Paso 2/3: Realizando corrección crítica...")
        prompt_corr = build_correction_prompt(initial_content, objetivo)
        
        corrections = generator.generate(prompt_corr, max_tokens=4000)
        if not corrections:
            st.error("❌ Error en corrección")
            st.stop()
        
        progress.progress(70)
        time.sleep(0.5)
        
        # PASO 3: Versión final
        status.write("✨ Paso 3/3: Aplicando correcciones y optimizando...")
        prompt_final = build_final_prompt(initial_content, corrections)
        
        final_content = generator.generate(prompt_final)
        if not final_content:
            st.error("❌ Error en versión final")
            st.stop()
        
        progress.progress(100)
        status.update(label="✅ Completado", state="complete")
        
        # Guardar resultados
        st.session_state.results = {
            'initial': initial_content,
            'corrections': corrections,
            'final': final_content,
            'metadata': {
                'product_id': product_id,
                'arquetipo': arquetipo_code,
                'objetivo': objetivo,
                'producto_alternativo': producto_alternativo,
                'casos_uso': casos_uso,
                'modulos': modules,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Mostrar resultados
        st.markdown("---")
        st.success("✅ Contenido generado exitosamente")
        
        # Mostrar resumen de configuración
        with st.expander("📋 Configuración aplicada", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Producto Alternativo:** {'✅ Configurado' if producto_alternativo else '❌ No configurado'}")
                if producto_alternativo:
                    st.caption(f"URL: {producto_alternativo.get('url', 'N/A')}")
            with col2:
                st.markdown(f"**Casos de Uso:** {len(casos_uso)} caso(s)")
                st.markdown(f"**Módulos:** {len(modules)} módulo(s)")
        
        tab1, tab2, tab3 = st.tabs([
            "📄 Versión Inicial",
            "🔍 Corrección Crítica",
            "✨ Versión Final"
        ])
        
        with tab1:
            st.markdown("### Contenido Inicial")
            with st.expander("Ver código HTML"):
                st.code(initial_content, language='html')
            st.download_button(
                "⬇️ Descargar HTML Inicial",
                data=initial_content,
                file_name=f"inicial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )
        
        with tab2:
            st.markdown("### Análisis y Correcciones Críticas")
            st.markdown(corrections)
        
        with tab3:
            st.markdown("### Contenido Final Optimizado")
            
            with st.expander("👁️ Vista previa renderizada", expanded=True):
                st.components.v1.html(final_content, height=800, scrolling=True)
            
            with st.expander("</> Código HTML final"):
                st.code(final_content, language='html')
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "⬇️ Descargar HTML Final",
                    data=final_content,
                    file_name=f"final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    use_container_width=True
                )
            with col2:
                st.download_button(
                    "⬇️ Descargar JSON completo",
                    data=json.dumps(st.session_state.results, indent=2, ensure_ascii=False),
                    file_name=f"generacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

if __name__ == "__main__":
    main()
