"""
Content Generator Black Friday - MVP
PcComponentes
"""

import streamlit as st
import anthropic
import json
import time
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN INICIAL
# ============================================================================

st.set_page_config(
    page_title="Content Generator BF | PcComponentes",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# DATOS MOCK PARA MVP (Reemplazar con scraping real)
# ============================================================================

def get_mock_pdp_data(url):
    """Mock de datos PDP - Reemplazar con endpoint n8n"""
    return {
        "url": url,
        "nombre": "Xiaomi Robot Vacuum E5 Robot con Función de Aspiración y Fregado",
        "precio_actual": "59.99",
        "precio_anterior": "64.99",
        "descuento": "-7%",
        "valoracion": "4.1",
        "num_opiniones": "112",
        "badges": ["Precio mínimo histórico"],
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

def get_mock_plp_data():
    """Mock de datos PLP - Reemplazar con Zenrows"""
    return [
        {
            "url": "https://www.pccomponentes.com/roborock-q10vf",
            "nombre": "Roborock Q10VF Robot Aspirador",
            "precio_actual": "229",
            "precio_anterior": "249",
            "descuento": "-8%",
            "valoracion": "4.6",
            "num_opiniones": "40"
        },
        {
            "url": "https://www.pccomponentes.com/xiaomi-robot-vacuum-e12",
            "nombre": "Xiaomi Robot Vacuum E12",
            "precio_actual": "78.49",
            "precio_anterior": "89.99",
            "descuento": "-12%",
            "valoracion": "4.2",
            "num_opiniones": "145"
        }
    ]

# ============================================================================
# ARQUETIPOS Y TONO DE MARCA
# ============================================================================

ARQUETIPOS = {
    "ARQ-4": {
        "code": "ARQ-4",
        "name": "Review / Análisis",
        "description": "Análisis profundo de producto único con pros, contras y veredicto",
        "funnel": "Middle",
        "default_length": 1800,
        "estructura": [
            "Veredicto rápido en box destacado",
            "Contexto de la oferta Black Friday",
            "Especificaciones técnicas",
            "Rendimiento real",
            "Lo que dicen usuarios reales",
            "Comparativa con competencia",
            "Preguntas frecuentes",
            "Veredicto final"
        ]
    },
    "ARQ-7": {
        "code": "ARQ-7",
        "name": "Roundup / Mejores X",
        "description": "Top X productos en una categoría",
        "funnel": "Middle",
        "default_length": 2200,
        "estructura": [
            "Introducción con criterios de selección",
            "Producto 1: Análisis",
            "Producto 2: Análisis",
            "Producto N: Análisis",
            "Tabla comparativa",
            "Guía de compra",
            "Conclusión"
        ]
    },
    "ARQ-8": {
        "code": "ARQ-8",
        "name": "Por presupuesto",
        "description": "Mejores productos por menos de X€",
        "funnel": "Bottom",
        "default_length": 1600,
        "estructura": [
            "Por qué este rango de precio",
            "Producto 1: Mejor calidad-precio",
            "Producto 2: Alternativa",
            "Producto 3: Opción económica",
            "Comparativa rápida",
            "Cómo elegir"
        ]
    }
}

BRAND_TONE = """
# Manual de Tono de Marca - PcComponentes

## Personalidad:
- Expertos sin ser pedantes
- Frikis sin vergüenza  
- Rápidos sin ser fríos
- Canallas con sentido común
- Honestos pero no aburridos
- Cercanos pero no falsamente coleguillas

## Principios:
- Hablamos claro: no adornamos lo que podemos explicar fácil
- No vendemos humo: preferimos ser honestos que sonar geniales
- Nos ponemos en su lugar: pensamos en qué espera la persona
- Sumamos valor: dejamos al cliente mejor de lo que llegó
- Humanizamos: cada mensaje tiene persona detrás

## Para Black Friday:
- Urgencia real sin alarmismo
- Honestidad aspiracional: reforzar positivo sin mentir
- Contexto de precio: "precio histórico", "stock bajando"
- Condiciones claras: envío gratis +50€, devolución hasta 15 enero
- CTAs directos al producto
"""

# ============================================================================
# PROMPT BUILDER
# ============================================================================

def build_initial_prompt(pdp_data, arquetipo, length, keywords, bf_context, plp_data):
    """Construye el prompt para generar contenido inicial"""
    
    keywords_str = ", ".join(keywords) if keywords else "No especificadas"
    plp_str = json.dumps(plp_data, indent=2) if plp_data else "No disponible"
    
    prompt = f"""
Eres un experto en redacción de contenidos para PcComponentes, especializado en crear artículos optimizados para Google Discover durante Black Friday.

# TONO DE MARCA PCCOMPONENTES:
{BRAND_TONE}

# ARQUETIPO SELECCIONADO:
- Nombre: {arquetipo['name']}
- Descripción: {arquetipo['description']}
- Estructura obligatoria:
{chr(10).join(f"  - {item}" for item in arquetipo['estructura'])}

# DATOS DEL PRODUCTO:
URL: {pdp_data['url']}
Nombre: {pdp_data['nombre']}
Precio actual: {pdp_data['precio_actual']}€
Precio anterior: {pdp_data['precio_anterior']}€
Descuento: {pdp_data['descuento']}
Valoración: {pdp_data['valoracion']}/5 ({pdp_data['num_opiniones']} opiniones)
Badges: {', '.join(pdp_data['badges'])}

Especificaciones:
{json.dumps(pdp_data['especificaciones'], indent=2, ensure_ascii=False)}

Descripción oficial:
{pdp_data['descripcion']}

Opiniones destacadas de usuarios:
{chr(10).join(f"- {op}" for op in pdp_data['opiniones_resumen'])}

# PRODUCTOS COMPETIDORES (para comparativa):
{plp_str}

# CONTEXTO BLACK FRIDAY:
{bf_context if bf_context else "Condiciones estándar: envío gratis +50€, devolución hasta 15 enero, entrega 24-48h península"}

# KEYWORDS SEO OBJETIVO:
{keywords_str}

# LONGITUD OBJETIVO:
{length} palabras aproximadamente

# INSTRUCCIONES:

1. Crea un artículo HTML completo con estilos CSS inline siguiendo exactamente la estructura del arquetipo {arquetipo['code']}.

2. TONO Y ESTILO:
   - Usa el tono aspiracional de PcComponentes: honesto, experto sin pedantería, con chispa
   - Enfoca en beneficios reales, no en limitaciones
   - Traduce tecnicismos a lenguaje útil ("2000Pa = aspira migas y pelos sin problema")
   - Urgencia Black Friday sin alarmismo

3. ESTRUCTURA OBLIGATORIA:
   - Incluye el CSS del ejemplo 1 (paleta PcComponentes)
   - Badge/kicker inicial con "Black Friday 2025 · [Categoría]"
   - Título H1 emocional + beneficio claro
   - Badges con specs clave
   - Box de veredicto rápido con gradiente morado
   - Índice con links anchor
   - Secciones según arquetipo
   - Tablas comparativas si hay datos PLP
   - FAQs con schema JSON-LD
   - CTAs con botones naranjas (#FF6000)

4. ELEMENTOS CRÍTICOS:
   - Menciona "precio mínimo histórico" si aplica
   - Incluye valoración y número de opiniones
   - Citas de opiniones reales (sin nombres de usuario)
   - Comparativa honesta con competencia si hay datos
   - Condiciones Black Friday en callout destacado
   - Links directos al producto (no categorías genéricas)

5. PROHIBIDO:
   - Lenguaje negativo o disuasivo
   - Datos inventados (solo usa info proporcionada)
   - Tecnicismos sin explicar
   - Superlativos sin respaldo ("el mejor del mundo")
   - CTAs genéricos ("ver más productos")

Genera el HTML completo ahora.
"""
    
    return prompt

def build_corrections_prompt(initial_content):
    """Construye el prompt para analizar y corregir"""
    
    prompt = f"""
Eres un editor experto de contenidos para PcComponentes. Analiza el siguiente contenido generado para Black Friday y proporciona correcciones específicas.

# CONTENIDO A ANALIZAR:
{initial_content}

# CRITERIOS DE EVALUACIÓN:

1. **Tono de marca PcComponentes:**
   - ¿Es honesto pero aspiracional?
   - ¿Evita lenguaje negativo innecesario?
   - ¿Suena experto sin pedantería?
   - ¿Tiene chispa y personalidad?

2. **Optimización Google Discover:**
   - ¿El título genera curiosidad + beneficio claro?
   - ¿Hook emocional en primeros párrafos?
   - ¿Elementos visuales (tablas, boxes destacados)?
   - ¿Ángulo único o dato sorprendente?

3. **Urgencia Black Friday:**
   - ¿Menciona precio mínimo histórico?
   - ¿Contexto de la oferta claro?
   - ¿Condiciones BF destacadas?
   - ¿CTAs directos al producto?

4. **Honestidad y credibilidad:**
   - ¿Datos verificables (opiniones, specs)?
   - ¿Comparativa justa con competencia?
   - ¿"Considera alternativas si..." en lugar de "no compres"?
   - ¿Transparente sobre lo que incluye/no incluye?

5. **Estructura y formato:**
   - ¿Todos los elementos del arquetipo presentes?
   - ¿CSS correcto con paleta PcComponentes?
   - ¿Schema JSON-LD implementado?
   - ¿Links funcionan correctamente?

# PROPORCIONA:

1. Lista de aspectos positivos (3-5 puntos)
2. Lista de correcciones necesarias con ejemplos específicos
3. Sugerencias de mejora para maximizar impacto

Sé específico y constructivo. Enfócate en mejoras que realmente impacten en la conversión y engagement.
"""
    
    return prompt

def build_final_prompt(initial_content, corrections):
    """Construye el prompt para versión final corregida"""
    
    prompt = f"""
Genera la versión final y optimizada del contenido aplicando las correcciones identificadas.

# CONTENIDO INICIAL:
{initial_content}

# CORRECCIONES A APLICAR:
{corrections}

# INSTRUCCIONES:

1. Aplica TODAS las correcciones mencionadas
2. Mantén la estructura HTML con estilos inline
3. Asegura que el tono sea aspiracional y positivo
4. Verifica que todos los elementos obligatorios estén presentes
5. Optimiza para conversión Black Friday

Genera el HTML completo corregido ahora.
"""
    
    return prompt

# ============================================================================
# GENERADOR DE CONTENIDO
# ============================================================================

class ContentGenerator:
    """Generador de contenido con Claude API"""
    
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
            st.error(f"Error llamando a Claude API: {str(e)}")
            return None

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_sidebar():
    """Renderiza sidebar con info y recursos"""
    with st.sidebar:
        st.markdown("## 🛒 Content Generator")
        st.markdown("**Black Friday 2025**")
        st.markdown("---")
        
        st.markdown("### 📚 Recursos")
        st.markdown("📄 [Plantilla CSV](#)")
        st.markdown("📖 [Guía arquetipos](#)")
        st.markdown("💡 [Mejores prácticas](#)")
        
        st.markdown("---")
        st.markdown("### ℹ️ Sobre")
        st.markdown("Versión MVP 1.0")
        st.markdown("PcComponentes © 2025")

def render_arquetipo_info(arquetipo):
    """Muestra info del arquetipo seleccionado"""
    st.info(f"""
    **📘 {arquetipo['name']}**
    
    {arquetipo['description']}
    
    **Funnel:** {arquetipo['funnel']}  
    **Longitud recomendada:** {arquetipo['default_length']} palabras
    
    **Estructura:**  
    {chr(10).join(f"✓ {item}" for item in arquetipo['estructura'])}
    """)

def display_results(results):
    """Muestra los resultados en tabs"""
    
    st.success("🎉 Contenido generado exitosamente")
    
    tab1, tab2, tab3 = st.tabs([
        "📄 Versión Inicial",
        "🔍 Correcciones",
        "✅ Versión Final"
    ])
    
    with tab1:
        st.markdown("### Contenido Inicial Generado")
        st.code(results['initial'], language='html')
        st.download_button(
            "💾 Descargar HTML",
            data=results['initial'],
            file_name=f"contenido_inicial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html"
        )
    
    with tab2:
        st.markdown("### Análisis y Correcciones")
        st.markdown(results['corrections'])
    
    with tab3:
        st.markdown("### Versión Final Optimizada")
        
        # Preview renderizado
        with st.expander("👁️ Vista previa", expanded=True):
            st.components.v1.html(results['final'], height=800, scrolling=True)
        
        # HTML crudo
        with st.expander("📝 Código HTML"):
            st.code(results['final'], language='html')
        
        # Botones descarga
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "💾 Descargar HTML Final",
                data=results['final'],
                file_name=f"contenido_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                use_container_width=True
            )
        with col2:
            st.download_button(
                "📊 Descargar Todo (JSON)",
                data=json.dumps(results, indent=2, ensure_ascii=False),
                file_name=f"generacion_completa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Aplicación principal"""
    
    render_sidebar()
    
    # Header
    st.title("🛒 Generador de Contenido Black Friday")
    st.markdown("Crea contenido optimizado para Google Discover en minutos")
    st.markdown("---")
    
    # Verificar API key
    if 'ANTHROPIC_API_KEY' not in st.secrets:
        st.error("⚠️ Falta configurar ANTHROPIC_API_KEY en secrets.toml")
        st.stop()
    
    # SECCIÓN 1: Producto
    st.header("📦 1. Producto en Oferta")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        product_url = st.text_input(
            "URL del producto",
            placeholder="https://www.pccomponentes.com/xiaomi-robot-vacuum-e5...",
            help="URL completa del producto en PcComponentes"
        )
    
    with col2:
        use_mock = st.checkbox("Usar datos de ejemplo", value=True, help="Para testing sin scraping")
    
    # SECCIÓN 2: Configuración
    st.header("📝 2. Configuración del Contenido")
    
    col1, col2 = st.columns(2)
    
    with col1:
        arquetipo_code = st.selectbox(
            "Arquetipo de contenido",
            options=list(ARQUETIPOS.keys()),
            format_func=lambda x: f"{ARQUETIPOS[x]['code']} - {ARQUETIPOS[x]['name']}"
        )
        arquetipo = ARQUETIPOS[arquetipo_code]
    
    with col2:
        content_length = st.slider(
            "Longitud (palabras)",
            min_value=800,
            max_value=3000,
            value=arquetipo['default_length'],
            step=100
        )
    
    # Mostrar info arquetipo
    render_arquetipo_info(arquetipo)
    
    # SECCIÓN 3: Opcionales
    with st.expander("🎯 Configuración Avanzada (Opcional)", expanded=False):
        
        keywords = st.text_input(
            "Keywords SEO (separadas por comas)",
            placeholder="robot aspirador xiaomi, oferta black friday, robot limpieza",
            help="Keywords principales que quieres optimizar"
        )
        
        bf_context = st.text_area(
            "Contexto Black Friday específico",
            placeholder="Stock limitado 50 unidades, oferta válida hasta 01/12/2025...",
            help="Info específica sobre fechas, stock, condiciones"
        )
        
        include_plp = st.checkbox("Incluir comparativa con competidores", value=True)
    
    # Botón generar
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate = st.button(
            "🚀 Generar Contenido",
            type="primary",
            use_container_width=True,
            disabled=not product_url
        )
    
    # Proceso de generación
    if generate:
        
        # Obtener datos
        if use_mock:
            pdp_data = get_mock_pdp_data(product_url)
            plp_data = get_mock_plp_data() if include_plp else None
        else:
            st.error("Scraping real no implementado en MVP. Activa 'Usar datos de ejemplo'")
            st.stop()
        
        # Procesar keywords
        keywords_list = [k.strip() for k in keywords.split(",")] if keywords else []
        
        # Inicializar generador
        generator = ContentGenerator(st.secrets['ANTHROPIC_API_KEY'])
        
        # Progress bar
        progress = st.progress(0)
        status = st.status("Generando contenido...", expanded=True)
        
        # PASO 1: Contenido inicial
        status.write("✨ Generando contenido inicial...")
        prompt_initial = build_initial_prompt(
            pdp_data, arquetipo, content_length, 
            keywords_list, bf_context, plp_data
        )
        
        initial_content = generator.generate(prompt_initial)
        if not initial_content:
            st.error("Error generando contenido inicial")
            st.stop()
        
        progress.progress(33)
        time.sleep(0.5)
        
        # PASO 2: Correcciones
        status.write("🔍 Analizando y generando correcciones...")
        prompt_corrections = build_corrections_prompt(initial_content)
        
        corrections = generator.generate(prompt_corrections, max_tokens=4000)
        if not corrections:
            st.error("Error generando correcciones")
            st.stop()
        
        progress.progress(66)
        time.sleep(0.5)
        
        # PASO 3: Versión final
        status.write("🎯 Generando versión final optimizada...")
        prompt_final = build_final_prompt(initial_content, corrections)
        
        final_content = generator.generate(prompt_final)
        if not final_content:
            st.error("Error generando versión final")
            st.stop()
        
        progress.progress(100)
        status.update(label="✅ Completado", state="complete")
        
        # Guardar en session state
        st.session_state.results = {
            'initial': initial_content,
            'corrections': corrections,
            'final': final_content,
            'metadata': {
                'product_url': product_url,
                'arquetipo': arquetipo_code,
                'length': content_length,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Mostrar resultados
        st.markdown("---")
        display_results(st.session_state.results)

if __name__ == "__main__":
    main()
