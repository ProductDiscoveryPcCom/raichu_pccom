"""
Content Generator - PcComponentes
Versión 2.2 con mejoras:
- Más arquetipos disponibles (incluyendo noticias)
- Campos dinámicos específicos por arquetipo
- Inputs contextuales según tipo de contenido
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
# ARQUETIPOS COMPLETOS CON CAMPOS ESPECÍFICOS
# ============================================================================

ARQUETIPOS = {
    "ARQ-1": {
        "code": "ARQ-1",
        "name": "📰 Noticia / Actualidad",
        "description": "Noticia sobre lanzamiento, actualización o evento relevante",
        "funnel": "Top",
        "default_length": 1200,
        "use_case": "Lanzamientos, actualizaciones, eventos, anuncios oficiales",
        "campos_especificos": {
            "noticia_principal": {
                "label": "¿Qué ha pasado? (noticia principal)",
                "type": "textarea",
                "placeholder": "Ej: Xiaomi lanza nuevo robot aspirador E5 Pro con mapeo láser y autovaciado por 199€",
                "help": "Resumen de la noticia en 1-2 frases"
            },
            "fecha_evento": {
                "label": "Fecha del evento/lanzamiento",
                "type": "text",
                "placeholder": "Ej: 25 de noviembre de 2025",
                "help": "Fecha exacta si está disponible"
            },
            "fuente_oficial": {
                "label": "Fuente oficial",
                "type": "text",
                "placeholder": "Ej: Comunicado oficial de Xiaomi, evento de prensa",
                "help": "De dónde viene la información"
            },
            "contexto_previo": {
                "label": "Contexto previo relevante",
                "type": "textarea",
                "placeholder": "Ej: El modelo anterior E5 fue bestseller en 2024 con más de 50.000 unidades vendidas",
                "help": "Información de fondo que da contexto"
            },
            "impacto_usuario": {
                "label": "Impacto para el usuario",
                "type": "textarea",
                "placeholder": "Ej: Los usuarios actuales del E5 podrán actualizar el firmware para activar nuevas funciones",
                "help": "Qué significa esto para los lectores"
            }
        }
    },
    "ARQ-2": {
        "code": "ARQ-2",
        "name": "📖 Guía Paso a Paso",
        "description": "Tutorial detallado para realizar una tarea o configuración",
        "funnel": "Middle",
        "default_length": 1800,
        "use_case": "Configuraciones, instalaciones, resolución de problemas",
        "campos_especificos": {
            "tarea_objetivo": {
                "label": "¿Qué tarea se va a explicar?",
                "type": "text",
                "placeholder": "Ej: Configurar el robot aspirador Xiaomi E5 para limpieza programada",
                "help": "Objetivo claro que el usuario quiere conseguir"
            },
            "requisitos_previos": {
                "label": "Requisitos previos",
                "type": "textarea",
                "placeholder": "Ej: Tener la app Xiaomi Home instalada, WiFi 2.4GHz configurado, robot cargado al 100%",
                "help": "Qué necesita el usuario antes de empezar"
            },
            "tiempo_estimado": {
                "label": "Tiempo estimado",
                "type": "text",
                "placeholder": "Ej: 10-15 minutos",
                "help": "Cuánto tardará el proceso"
            },
            "dificultad": {
                "label": "Nivel de dificultad",
                "type": "text",
                "placeholder": "Ej: Principiante / Intermedio / Avanzado",
                "help": "Para qué nivel de usuario está pensado"
            },
            "puntos_criticos": {
                "label": "Puntos críticos o errores comunes",
                "type": "textarea",
                "placeholder": "Ej: Asegúrate de conectar al WiFi 2.4GHz y NO 5GHz. Si no aparece el robot, reinicia la app",
                "help": "Problemas típicos y cómo evitarlos"
            }
        }
    },
    "ARQ-3": {
        "code": "ARQ-3",
        "name": "💡 Explicación / Educativo",
        "description": "Explica conceptos técnicos o funcionamiento de tecnología",
        "funnel": "Top",
        "default_length": 1600,
        "use_case": "Educar sobre tecnologías, conceptos, diferencias técnicas",
        "campos_especificos": {
            "concepto_principal": {
                "label": "Concepto a explicar",
                "type": "text",
                "placeholder": "Ej: Navegación láser vs giroscopio en robots aspiradores",
                "help": "Qué se va a explicar"
            },
            "nivel_tecnico": {
                "label": "Nivel técnico del público",
                "type": "text",
                "placeholder": "Ej: Usuario general sin conocimientos técnicos",
                "help": "Define cuánto tecnicismo usar"
            },
            "analogias_utiles": {
                "label": "Analogías o ejemplos útiles",
                "type": "textarea",
                "placeholder": "Ej: La navegación láser es como un GPS que mapea tu casa; el giroscopio es como conducir con brújula",
                "help": "Comparaciones que faciliten la comprensión"
            },
            "aplicacion_practica": {
                "label": "Aplicación práctica",
                "type": "textarea",
                "placeholder": "Ej: Con láser puedes limpiar solo la cocina; con giroscopio limpia toda la casa sin seleccionar",
                "help": "Por qué es importante este concepto en la práctica"
            }
        }
    },
    "ARQ-4": {
        "code": "ARQ-4",
        "name": "⭐ Review / Análisis",
        "description": "Análisis profundo de producto único con pros, contras y veredicto",
        "funnel": "Middle",
        "default_length": 1800,
        "use_case": "Producto único destacado - Black Friday, lanzamientos, ofertas especiales",
        "campos_especificos": {
            "tiempo_uso": {
                "label": "Tiempo de uso/prueba",
                "type": "text",
                "placeholder": "Ej: 2 semanas de uso intensivo",
                "help": "Cuánto tiempo se ha probado el producto"
            },
            "escenarios_prueba": {
                "label": "Escenarios de prueba",
                "type": "textarea",
                "placeholder": "Ej: Piso 75m², 2 adultos + perro, suelos de parquet y baldosa, limpieza diaria",
                "help": "En qué contexto se ha probado"
            },
            "competencia_directa": {
                "label": "Competencia directa",
                "type": "text",
                "placeholder": "Ej: Roborock Q7, Conga 3490, iRobot Roomba i3",
                "help": "Productos similares para comparar"
            },
            "punto_fuerte_principal": {
                "label": "Principal punto fuerte",
                "type": "text",
                "placeholder": "Ej: Relación calidad-precio imbatible en su rango",
                "help": "Lo que más destaca del producto"
            },
            "limitacion_principal": {
                "label": "Principal limitación",
                "type": "text",
                "placeholder": "Ej: No tiene mapeo por habitaciones",
                "help": "Limitación más importante a mencionar (en positivo)"
            }
        }
    },
    "ARQ-5": {
        "code": "ARQ-5",
        "name": "⚖️ Comparativa A vs B",
        "description": "Comparación directa entre 2-3 productos similares",
        "funnel": "Middle",
        "default_length": 1600,
        "use_case": "Ayudar a elegir entre alternativas directas",
        "campos_especificos": {
            "producto_a_nombre": {
                "label": "Producto A - Nombre",
                "type": "text",
                "placeholder": "Ej: Xiaomi Robot Vacuum E5",
                "help": "Primer producto a comparar"
            },
            "producto_a_caracteristicas": {
                "label": "Producto A - Características clave",
                "type": "textarea",
                "placeholder": "Ej: 2000Pa succión, 110 min autonomía, WiFi, fregado básico, 59€",
                "help": "Specs principales del producto A"
            },
            "producto_a_mejor_para": {
                "label": "Producto A - Mejor para casos de uso",
                "type": "textarea",
                "placeholder": "Ej: Presupuesto ajustado, pisos pequeños-medianos, mantenimiento diario básico",
                "help": "Cuándo elegir el producto A"
            },
            "producto_b_nombre": {
                "label": "Producto B - Nombre",
                "type": "text",
                "placeholder": "Ej: Roborock Q7",
                "help": "Segundo producto a comparar"
            },
            "producto_b_caracteristicas": {
                "label": "Producto B - Características clave",
                "type": "textarea",
                "placeholder": "Ej: 2700Pa succión, 180 min autonomía, mapeo láser, fregado inteligente, 99€",
                "help": "Specs principales del producto B"
            },
            "producto_b_mejor_para": {
                "label": "Producto B - Mejor para casos de uso",
                "type": "textarea",
                "placeholder": "Ej: Casas grandes, necesidad de mapeo por habitaciones, presupuesto medio",
                "help": "Cuándo elegir el producto B"
            },
            "criterios_comparacion": {
                "label": "Criterios principales de comparación",
                "type": "textarea",
                "placeholder": "Ej: Potencia de succión, autonomía, navegación, fregado, precio, app móvil",
                "help": "En qué aspectos se van a comparar"
            }
        }
    },
    "ARQ-6": {
        "code": "ARQ-6",
        "name": "🔥 Deal Alert / Chollo",
        "description": "Alerta de oferta destacada con urgencia",
        "funnel": "Bottom",
        "default_length": 1000,
        "use_case": "Ofertas flash, chollos limitados, precio histórico",
        "campos_especificos": {
            "precio_actual": {
                "label": "Precio actual",
                "type": "text",
                "placeholder": "Ej: 59€",
                "help": "Precio de la oferta"
            },
            "precio_habitual": {
                "label": "Precio habitual",
                "type": "text",
                "placeholder": "Ej: 89€",
                "help": "Precio normal sin oferta"
            },
            "ahorro_total": {
                "label": "Ahorro total",
                "type": "text",
                "placeholder": "Ej: 30€ (-34%)",
                "help": "Cuánto se ahorra"
            },
            "duracion_oferta": {
                "label": "Duración de la oferta",
                "type": "text",
                "placeholder": "Ej: Solo hasta medianoche / Mientras duren existencias / 72 horas",
                "help": "Cuánto tiempo estará disponible"
            },
            "stock_disponible": {
                "label": "Stock o unidades disponibles",
                "type": "text",
                "placeholder": "Ej: Quedan menos de 20 unidades / Stock limitado",
                "help": "Información de disponibilidad para urgencia"
            },
            "precio_historico": {
                "label": "¿Es precio mínimo histórico?",
                "type": "text",
                "placeholder": "Ej: Sí, primera vez por debajo de 60€ / No, pero mejor precio del mes",
                "help": "Contexto histórico del precio"
            },
            "por_que_oferta": {
                "label": "¿Por qué está en oferta?",
                "type": "text",
                "placeholder": "Ej: Black Friday / Nuevo modelo próximo a salir / Liquidación stock",
                "help": "Razón de la oferta (si se conoce)"
            }
        }
    },
    "ARQ-7": {
        "code": "ARQ-7",
        "name": "🏆 Roundup / Mejores X",
        "description": "Top X productos en una categoría",
        "funnel": "Middle",
        "default_length": 2200,
        "use_case": "Lista categoría - Black Friday, guías de compra",
        "campos_especificos": {
            "numero_productos": {
                "label": "Número de productos en el top",
                "type": "text",
                "placeholder": "Ej: 5",
                "help": "Cuántos productos incluir (3-10 recomendado)"
            },
            "criterios_seleccion": {
                "label": "Criterios de selección",
                "type": "textarea",
                "placeholder": "Ej: Probados personalmente, más vendidos del año, mejor valorados, diferentes rangos de precio",
                "help": "Por qué estos productos y no otros"
            },
            "rango_precios": {
                "label": "Rango de precios",
                "type": "text",
                "placeholder": "Ej: De 59€ a 299€",
                "help": "Desde el más barato al más caro"
            },
            "categoria_especifica": {
                "label": "Categoría específica",
                "type": "text",
                "placeholder": "Ej: Robots aspiradores con fregado / Monitores gaming 1440p / Portátiles <600€",
                "help": "Define bien la categoría para el título"
            },
            "ganador_absoluto": {
                "label": "Ganador absoluto (si lo hay)",
                "type": "text",
                "placeholder": "Ej: Roborock S7+ es nuestra elección premium / Xiaomi E5 mejor calidad-precio",
                "help": "Producto destacado del top (opcional)"
            }
        }
    },
    "ARQ-8": {
        "code": "ARQ-8",
        "name": "💰 Por presupuesto",
        "description": "Mejores productos por menos de X€",
        "funnel": "Bottom",
        "default_length": 1600,
        "use_case": "Chollos en rango de precio específico",
        "campos_especificos": {
            "presupuesto_limite": {
                "label": "Presupuesto límite",
                "type": "text",
                "placeholder": "Ej: 100€ / 500€ / 1000€",
                "help": "Precio máximo del rango"
            },
            "que_esperar": {
                "label": "Qué se puede esperar en este rango",
                "type": "textarea",
                "placeholder": "Ej: Por menos de 100€ puedes conseguir robots básicos sin mapeo pero con buena succión y app móvil",
                "help": "Expectativas realistas del presupuesto"
            },
            "que_sacrificas": {
                "label": "Qué características se sacrifican",
                "type": "textarea",
                "placeholder": "Ej: No tendrás mapeo láser ni autovaciado, pero la limpieza básica es efectiva",
                "help": "Qué no esperar en este rango (en positivo)"
            },
            "mejor_opcion": {
                "label": "Mejor opción en el rango",
                "type": "text",
                "placeholder": "Ej: Xiaomi E5 a 59€ es imbatible en calidad-precio",
                "help": "Producto destacado del presupuesto"
            }
        }
    },
    "ARQ-9": {
        "code": "ARQ-9",
        "name": "🥊 Versus Detallado",
        "description": "Enfrentamiento profundo producto a producto con ganador claro",
        "funnel": "Bottom",
        "default_length": 2000,
        "use_case": "Decisión de compra entre dos modelos muy similares",
        "campos_especificos": {
            "producto_1": {
                "label": "Producto 1",
                "type": "text",
                "placeholder": "Ej: Xiaomi Robot Vacuum E5",
                "help": "Primer contendiente"
            },
            "producto_2": {
                "label": "Producto 2",
                "type": "text",
                "placeholder": "Ej: Roborock Q7",
                "help": "Segundo contendiente"
            },
            "categorias_versus": {
                "label": "Categorías de enfrentamiento",
                "type": "textarea",
                "placeholder": "Ej: Potencia de succión, Autonomía, Navegación, Fregado, App móvil, Precio, Ruido",
                "help": "Aspectos específicos a comparar (separa por comas o líneas)"
            },
            "ganador_categorias": {
                "label": "Ganadores por categoría",
                "type": "textarea",
                "placeholder": "Ej: Succión: Roborock +700Pa | Autonomía: Roborock +70min | Precio: Xiaomi -40€",
                "help": "Quién gana en cada categoría"
            },
            "ganador_global": {
                "label": "Ganador global y por qué",
                "type": "textarea",
                "placeholder": "Ej: Xiaomi gana por precio y suficiencia; Roborock solo vale la pena si necesitas mapeo láser",
                "help": "Veredicto final del versus"
            }
        }
    },
    "ARQ-10": {
        "code": "ARQ-10",
        "name": "👤 Por perfil de usuario",
        "description": "Productos perfectos para un tipo específico de usuario",
        "funnel": "Middle",
        "default_length": 1800,
        "use_case": "Segmentación por audiencia (gamers, estudiantes, profesionales)",
        "campos_especificos": {
            "perfil_usuario": {
                "label": "Perfil de usuario",
                "type": "text",
                "placeholder": "Ej: Estudiante universitario / Gamer competitivo / Profesional teletrabajo",
                "help": "Define el tipo de usuario objetivo"
            },
            "necesidades_especificas": {
                "label": "Necesidades específicas del perfil",
                "type": "textarea",
                "placeholder": "Ej: Portabilidad, batería larga, presupuesto <600€, Office y navegación",
                "help": "Qué necesita este usuario específicamente"
            },
            "prioridades": {
                "label": "Prioridades del perfil",
                "type": "textarea",
                "placeholder": "Ej: 1. Precio, 2. Batería, 3. Peso, 4. Pantalla de calidad",
                "help": "Orden de importancia de características"
            },
            "no_necesita": {
                "label": "Qué NO necesita este perfil",
                "type": "textarea",
                "placeholder": "Ej: No necesita GPU dedicada, ni pantalla 4K, ni más de 16GB RAM",
                "help": "Características por las que no vale pagar más"
            }
        }
    },
    "ARQ-11": {
        "code": "ARQ-11",
        "name": "🔮 Tendencias / Predicciones",
        "description": "Análisis de tendencias del mercado o predicciones",
        "funnel": "Top",
        "default_length": 1400,
        "use_case": "Contenido de autoridad, análisis de mercado, tendencias tech",
        "campos_especificos": {
            "tendencia_principal": {
                "label": "Tendencia principal",
                "type": "text",
                "placeholder": "Ej: Robots aspiradores con IA y autovaciado se están volviendo accesibles",
                "help": "Qué tendencia se está observando"
            },
            "datos_soporte": {
                "label": "Datos que soportan la tendencia",
                "type": "textarea",
                "placeholder": "Ej: Ventas de modelos con autovaciado +150% vs 2023, precios han bajado 40% en 2 años",
                "help": "Números, stats, datos concretos"
            },
            "prediccion": {
                "label": "Predicción o evolución futura",
                "type": "textarea",
                "placeholder": "Ej: En 2026, los modelos básicos incluirán mapeo láser como estándar",
                "help": "Hacia dónde va el mercado"
            },
            "impacto_consumidor": {
                "label": "Impacto para el consumidor",
                "type": "textarea",
                "placeholder": "Ej: Mejor momento para comprar - más funciones por menos dinero que nunca",
                "help": "Qué significa para el usuario final"
            }
        }
    },
    "ARQ-12": {
        "code": "ARQ-12",
        "name": "📦 Unboxing / Primera impresión",
        "description": "Experiencia de unboxing y primeras horas con el producto",
        "funnel": "Top/Middle",
        "default_length": 1200,
        "use_case": "Lanzamientos, primeras impresiones, experiencia inicial",
        "campos_especificos": {
            "contenido_caja": {
                "label": "Contenido de la caja",
                "type": "textarea",
                "placeholder": "Ej: Robot, base de carga, mopa x2, cepillo extra, filtro adicional, manual",
                "help": "Qué viene incluido"
            },
            "primera_impresion_build": {
                "label": "Primera impresión - Construcción",
                "type": "textarea",
                "placeholder": "Ej: Plástico de calidad media-alta, peso 3kg, acabados limpios, botones físicos táctiles",
                "help": "Calidad de construcción al tacto"
            },
            "sorpresas_positivas": {
                "label": "Sorpresas positivas",
                "type": "textarea",
                "placeholder": "Ej: Incluye 2 mopas de repuesto y filtro extra, embalaje sostenible",
                "help": "Qué ha superado expectativas"
            },
            "sorpresas_negativas": {
                "label": "Decepciones o sorpresas negativas",
                "type": "textarea",
                "placeholder": "Ej: Manual solo en inglés, depósito de agua más pequeño de lo esperado",
                "help": "Qué ha decepcionado (en tono neutral)"
            },
            "setup_inicial": {
                "label": "Configuración inicial",
                "type": "text",
                "placeholder": "Ej: 5 minutos, muy sencillo, app intuitiva",
                "help": "Experiencia del primer uso"
            }
        }
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
- ❌ SOLO en comparativas técnicas (no para disuadir)
"""

# ============================================================================
# EJEMPLOS DE REFERENCIA CSS
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
# FUNCIÓN PARA RENDERIZAR CAMPOS ESPECÍFICOS
# ============================================================================

def render_campos_especificos(arquetipo_data):
    """
    Renderiza campos de input específicos según el arquetipo seleccionado
    Devuelve diccionario con los valores capturados
    """
    campos_especificos = arquetipo_data.get('campos_especificos', {})
    
    if not campos_especificos:
        return {}
    
    st.markdown("### 📝 Información Específica del Arquetipo")
    st.caption(f"Completa estos campos para optimizar el contenido tipo '{arquetipo_data['name']}'")
    
    valores = {}
    
    for campo_key, campo_config in campos_especificos.items():
        label = campo_config['label']
        tipo = campo_config['type']
        placeholder = campo_config.get('placeholder', '')
        help_text = campo_config.get('help', '')
        
        if tipo == 'text':
            valores[campo_key] = st.text_input(
                label,
                placeholder=placeholder,
                help=help_text,
                key=f"campo_{campo_key}"
            )
        elif tipo == 'textarea':
            valores[campo_key] = st.text_area(
                label,
                placeholder=placeholder,
                help=help_text,
                height=100,
                key=f"campo_{campo_key}"
            )
    
    return valores

# ============================================================================
# PROMPT BUILDER
# ============================================================================

def build_arquetipo_context(arquetipo_code, campos_valores):
    """
    Construye contexto específico del arquetipo para incluir en el prompt
    """
    if not campos_valores:
        return ""
    
    # Filtrar campos vacíos
    campos_llenos = {k: v for k, v in campos_valores.items() if v and v.strip()}
    
    if not campos_llenos:
        return ""
    
    context = f"\n# INFORMACIÓN ESPECÍFICA DEL ARQUETIPO {arquetipo_code}:\n\n"
    
    for campo_key, valor in campos_llenos.items():
        # Convertir snake_case a Title Case para etiquetas
        label = campo_key.replace('_', ' ').title()
        context += f"**{label}:**\n{valor}\n\n"
    
    context += "Usa esta información específica para crear un contenido altamente relevante y personalizado.\n"
    
    return context

def build_generation_prompt(pdp_data, arquetipo, length, keywords, context, links, modules, objetivo, producto_alternativo, casos_uso, campos_arquetipo):
    """Construye prompt para generación inicial"""
    
    keywords_str = ", ".join(keywords) if keywords else "No especificadas"
    
    # Contexto específico del arquetipo
    arquetipo_context = build_arquetipo_context(arquetipo['code'], campos_arquetipo)
    
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

{arquetipo_context}

# DATOS DEL PRODUCTO (si aplica):
{json.dumps(pdp_data, indent=2, ensure_ascii=False) if pdp_data else "N/A - Contenido no centrado en producto específico"}

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
<h2>[Título optimizado según arquetipo]</h2>

<div class="badges">
<span class="badge">[Info clave 1]</span>
<span class="badge">[Info clave 2]</span>
</div>

[CONTENIDO ADAPTADO AL ARQUETIPO {arquetipo['code']}]

[Si aplica: veredicto, callouts, tablas, módulos según tipo de contenido]

<h2 id="faqs">Preguntas frecuentes</h2>
[FAQs relevantes con H3 para cada pregunta]

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [...]
}}
</script>
</article>

## 2. ADAPTACIÓN AL ARQUETIPO {arquetipo['code']}:

Sigue estas directrices específicas para {arquetipo['name']}:

{get_arquetipo_guidelines(arquetipo['code'])}

## 3. TONO ASPIRACIONAL (CRÍTICO):

✅ SIEMPRE enfoca en beneficios y soluciones
✅ Usa "Perfecto si..." 
✅ Si hay producto alternativo: usa "Considera alternativas si..." con enlace
✅ Si NO hay alternativo: desarrolla extensamente "Perfecto si" con múltiples casos de uso

❌ PROHIBIDO lenguaje negativo que desanime
❌ PROHIBIDO "evita", "no compres", "no recomendado"
❌ PROHIBIDO tecnicismos sin explicar

## 4. EMOJIS (SOLO ESTOS):

✅ Para ventajas y puntos positivos
⚡ Para urgencia, velocidad, destacar
❌ SOLO en tablas comparativas técnicas (no para disuadir)

## 5. ELEMENTOS OBLIGATORIOS:

✅ Kicker con categoría
✅ Título H2 (NO H1) con beneficio claro
✅ Estructura adaptada al arquetipo
✅ TOC navegable si contenido >1500 palabras
✅ Callouts estratégicos
✅ CTAs claros
✅ FAQs al final
✅ Schema JSON-LD válido
✅ MÓDULOS de productos si están configurados

Genera AHORA el contenido completo del artículo.
"""
    
    return prompt

def get_arquetipo_guidelines(arquetipo_code):
    """Devuelve directrices específicas de estructura para cada arquetipo"""
    
    guidelines = {
        "ARQ-1": """
**Estructura Noticia:**
1. Lead con las 5W (qué, quién, cuándo, dónde, por qué)
2. Contexto y antecedentes
3. Detalles específicos de la noticia
4. Implicaciones para usuarios
5. Fuentes y referencias
6. Conclusión con proyección futura

**Tono:** Informativo, urgente si procede, neutral pero atractivo.
""",
        "ARQ-2": """
**Estructura Guía Paso a Paso:**
1. Introducción: qué se va a conseguir
2. Requisitos previos claramente listados
3. Pasos numerados (3-10 pasos típicamente)
4. Screenshots o descripciones detalladas de cada paso
5. Avisos de puntos críticos en callouts
6. Verificación final
7. Troubleshooting común

**Tono:** Instructivo, claro, paciente, sin asumir conocimientos.
""",
        "ARQ-3": """
**Estructura Explicación:**
1. Hook: por qué importa este concepto
2. Definición simple primero
3. Explicación técnica progresiva
4. Analogías y ejemplos prácticos
5. Aplicaciones reales
6. Comparaciones si aplica
7. Conclusión con takeaway clave

**Tono:** Educativo pero accesible, experto sin pedantería.
""",
        "ARQ-4": """
**Estructura Review:**
1. Veredicto rápido
2. Contexto (precio, competencia, momento)
3. Diseño y construcción
4. Rendimiento con datos reales
5. Experiencia de uso diario
6. Comparativa con competencia
7. FAQs
8. Veredicto final

**Tono:** Experto, honesto, equilibrado.
""",
        "ARQ-5": """
**Estructura Comparativa A vs B:**
1. Intro: por qué comparar estos dos
2. Tabla comparativa visual al inicio
3. Análisis Producto A
4. Análisis Producto B
5. Comparación directa por categorías
6. Veredicto: cuál elegir según perfil
7. Conclusión con recomendación clara

**Tono:** Imparcial, analítico, útil para decisión.
""",
        "ARQ-6": """
**Estructura Deal Alert:**
1. Hook con precio y ahorro EN MAYÚSCULAS o negrita
2. Por qué es chollo (precio histórico, etc.)
3. Características clave del producto
4. Para quién es perfecto
5. Duración de oferta y stock
6. CTA urgente y directo
7. Alternativas si se agota

**Tono:** Urgente, directo, sin rodeos, enfocado en valor.
""",
        "ARQ-7": """
**Estructura Roundup:**
1. Criterios de selección
2. Ganador absoluto (si lo hay) destacado
3. Producto #1 con análisis
4. Producto #2-N con análisis
5. Tabla comparativa completa
6. Guía de compra: cómo elegir
7. Conclusión y recomendación por perfil

**Tono:** Autoridad, comprehensivo, útil para comparar.
""",
        "ARQ-8": """
**Estructura Por Presupuesto:**
1. Qué esperar en este rango de precio
2. Mejor opción del rango (destacada)
3. Alternativas en el rango
4. Qué sacrificas vs rangos superiores (en positivo)
5. Tabla comparativa rápida
6. Consejos para maximizar presupuesto
7. Conclusión: merece la pena o esperar

**Tono:** Realista, honesto, optimista dentro del presupuesto.
""",
        "ARQ-9": """
**Estructura Versus:**
1. Presentación de contendientes
2. Round 1: Categoría A (ganador + razón)
3. Round 2: Categoría B (ganador + razón)
4. Round N: Categoría N (ganador + razón)
5. Tabla puntuación final
6. Ganador absoluto y por qué
7. Cuándo elegir al perdedor

**Tono:** Deportivo, entretenido, riguroso en datos.
""",
        "ARQ-10": """
**Estructura Por Perfil:**
1. Definición del perfil de usuario
2. Necesidades específicas del perfil
3. Producto recomendado y por qué encaja
4. Características clave para este perfil
5. Qué NO necesita este perfil (ahorro)
6. Alternativas si perfil varía ligeramente
7. Conclusión personalizada

**Tono:** Empático, personalizado, consultivo.
""",
        "ARQ-11": """
**Estructura Tendencias:**
1. Contexto: situación actual del mercado
2. Tendencia observada con datos
3. Causas de la tendencia
4. Predicción de evolución
5. Impacto para consumidores
6. Recomendaciones prácticas
7. Conclusión: qué hacer ahora

**Tono:** Analítico, con autoridad, prospectivo.
""",
        "ARQ-12": """
**Estructura Unboxing:**
1. Primera impresión de la caja/packaging
2. Contenido completo listado
3. Construcción y materiales al tacto
4. Sorpresas positivas
5. Decepciones (si las hay, en tono neutro)
6. Setup inicial: facilidad y tiempo
7. Primeras horas de uso
8. Veredicto preliminar

**Tono:** Entusiasta, descriptivo, honesto, cercano.
"""
    }
    
    return guidelines.get(arquetipo_code, "Sigue las mejores prácticas del arquetipo seleccionado.")

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

## 2. Adaptación al arquetipo:
- ¿Sigue la estructura específica del arquetipo?
- ¿Usa el tono apropiado?
- ¿Los elementos clave del arquetipo están presentes?

## 3. Información específica del arquetipo:
- ¿Se han usado los datos específicos proporcionados?
- ¿Están bien integrados en el contenido?
- ¿Falta alguna información clave solicitada?

## 4. Tono aspiracional (CRÍTICO):
- ¿Se usa lenguaje negativo o disuasorio?
- ¿Las limitaciones tienen contexto útil?
- ¿Se enfoca en soluciones y beneficios?

## 5. Emojis:
- ¿Solo usa ✅ ⚡ ❌?
- ¿Están bien utilizados según las reglas?

## 6. Enlaces:
- ¿Enlace principal en primeros párrafos?
- ¿Enlaces secundarios bien integrados?
- ¿Producto alternativo presente si configurado?
- ¿Anchor text descriptivo?

## 7. Módulos de productos:
- ¿Aparecen TODOS los módulos configurados?
- ¿Formato EXACTO correcto?
- ¿Ubicación estratégica?

## 8. Estructura técnica:
- ¿CSS correcto con paleta PcComponentes?
- ¿TOC con anchors si aplica?
- ¿Schema JSON-LD válido?

## 9. Optimización Discover:
- ¿Título atractivo?
- ¿Hook emocional?
- ¿Elementos visuales?
- ¿Datos específicos?

# PROPORCIONA:

## Resumen ejecutivo:
[3-4 líneas sobre estado general]

## Correcciones CRÍTICAS (obligatorias):
[Lista numerada de cambios NECESARIOS]

## Sugerencias de mejora (opcionales):
[Optimizaciones adicionales]

## Alineación con objetivo:
[¿Cumple? ¿Ajustes necesarios?]

## Verificación arquetipo:
[¿Estructura y tono correctos?]

## Verificación de módulos:
[¿Presentes todos? ¿Formato correcto?]

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
6. Asegura que la estructura del arquetipo se mantiene correcta
7. Optimiza para máximo impacto y conversión

IMPORTANTE: El output debe ser el artículo completo corregido, listo para publicar.

Genera el artículo final AHORA.
"""
    
    return prompt

# ============================================================================
# GENERADOR
# ============================================================================

class ContentGenerator:
    """Generador con corrección crítica"""
    
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
        
        st.markdown("### 🆕 V2.2 Features")
        st.markdown("✅ 12 arquetipos disponibles")
        st.markdown("✅ Campos dinámicos por tipo")
        st.markdown("✅ Arquetipos Noticias, Guías, Deal Alerts, Versus...")
        st.markdown("---")
        
        st.markdown("### Recursos")
        st.markdown("[Guía arquetipos](#)")
        st.markdown("[Manual tono](#)")
        st.markdown("---")
        st.markdown("### Info")
        st.markdown("Versión 2.2")
        st.markdown("© 2025")

def main():
    """App principal"""
    
    render_sidebar()
    
    # Header
    st.title("Content Generator V2.2")
    st.markdown("Genera contenido optimizado para Google Discover con 12 arquetipos especializados")
    st.markdown("---")
    
    # Verificar API key
    if 'ANTHROPIC_API_KEY' not in st.secrets:
        st.error("Configura ANTHROPIC_API_KEY en secrets")
        st.stop()
    
    # SECCIÓN 1: Producto (opcional para algunos arquetipos)
    st.header("1. Producto (Opcional para algunos arquetipos)")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        product_id = st.text_input(
            "ID del producto",
            placeholder="10848823 (dejar vacío si arquetipo no requiere producto específico)",
            help="ID numérico del producto en PcComponentes"
        )
    
    with col2:
        use_mock = st.checkbox("Datos ejemplo", value=True, help="Testing sin VPN")
    
    # SECCIÓN 2: Arquetipo y configuración
    st.header("2. Tipo de Contenido")
    
    col1, col2 = st.columns(2)
    
    with col1:
        arquetipo_code = st.selectbox(
            "Arquetipo",
            options=list(ARQUETIPOS.keys()),
            format_func=lambda x: f"{ARQUETIPOS[x]['name']}"
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
        placeholder="Ej: Convertir usuarios indecisos en compradores destacando el precio histórico y urgencia Black Friday.",
        help="Describe qué quieres lograr. La IA usará esto para corrección crítica",
        height=100
    )
    
    if not objetivo:
        st.warning("⚠️ El objetivo del contenido es obligatorio")
    
    # CAMPOS ESPECÍFICOS DEL ARQUETIPO (DINÁMICOS)
    st.markdown("---")
    campos_arquetipo = render_campos_especificos(arquetipo)
    
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
        
        # Producto Alternativo (OPCIONAL)
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
        
        # Casos de uso (OPCIONAL)
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
        
        # Módulos de productos (DINÁMICO)
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
            disabled=not objetivo
        )
    
    # Proceso de generación
    if generate:
        
        # Obtener datos PDP (si se requiere producto)
        pdp_data = None
        if product_id:
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
        status.write(f"📝 Paso 1/3: Generando contenido tipo '{arquetipo['name']}'...")
        prompt_gen = build_generation_prompt(
            pdp_data, arquetipo, content_length,
            keywords_list, context, links, modules, objetivo,
            producto_alternativo, casos_uso, campos_arquetipo
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
                'product_id': product_id or "N/A",
                'arquetipo': arquetipo_code,
                'objetivo': objetivo,
                'campos_arquetipo': campos_arquetipo,
                'producto_alternativo': producto_alternativo,
                'casos_uso': casos_uso,
                'modulos': modules,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Mostrar resultados
        st.markdown("---")
        st.success(f"✅ Contenido tipo '{arquetipo['name']}' generado exitosamente")
        
        # Mostrar resumen de configuración
        with st.expander("📋 Configuración aplicada", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Arquetipo:** {arquetipo['name']}")
                st.markdown(f"**Producto ID:** {product_id or 'N/A'}")
            with col2:
                st.markdown(f"**Alternativo:** {'✅' if producto_alternativo else '❌'}")
                st.markdown(f"**Casos de uso:** {len(casos_uso)}")
            with col3:
                st.markdown(f"**Módulos:** {len(modules)}")
                st.markdown(f"**Campos específicos:** {len([v for v in campos_arquetipo.values() if v])}")
        
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
                file_name=f"inicial_{arquetipo_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
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
                    file_name=f"final_{arquetipo_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    use_container_width=True
                )
            with col2:
                st.download_button(
                    "⬇️ Descargar JSON completo",
                    data=json.dumps(st.session_state.results, indent=2, ensure_ascii=False),
                    file_name=f"generacion_{arquetipo_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

if __name__ == "__main__":
    main()
