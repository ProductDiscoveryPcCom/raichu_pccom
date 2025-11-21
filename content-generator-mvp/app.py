"""
Content Generator - PcComponentes
Versión 3.1 + GSC Integration
- 12 arquetipos completos con todos sus campos específicos
- Sistema Dual de Módulos (Producto + Carrusel)
- Búsqueda incremental de categorías
- Integración completa con CSV
- Verificación GSC antes de generar contenido ← NUEVO
"""

import streamlit as st
import anthropic
import requests
import json
import time
import pandas as pd
import os
from datetime import datetime
from gsc_checker import GSCChecker, render_gsc_auth_ui, render_gsc_check_results

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
# CONFIGURACIÓN GSC
# ============================================================================

GSC_CLIENT_CONFIG = None
if 'GSC_CLIENT_CONFIG' in st.secrets:
    try:
        GSC_CLIENT_CONFIG = json.loads(st.secrets['GSC_CLIENT_CONFIG'])
    except:
        st.warning("⚠️ GSC_CLIENT_CONFIG en secrets no es JSON válido")

# ============================================================================
# CARGA DE DATOS DE CATEGORÍAS - MEJORADA CON DEBUG
# ============================================================================

@st.cache_data
def load_categories_data():
    """Carga el CSV de categorías con debug mejorado"""
    
    # Lista de posibles ubicaciones del CSV
    possible_paths = [
        'data/categories.csv',
        os.path.join(os.path.dirname(__file__), 'data', 'categories.csv'),
    ]
    
    debug_info = []
    
    for csv_path in possible_paths:
        try:
            debug_info.append(f"Probando: {csv_path} - Existe: {os.path.exists(csv_path)}")
            
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path, sep=';', encoding='utf-8-sig')
                st.success(f"✅ {len(df)} categorías cargadas desde: {csv_path}")
                return df
        except Exception as e:
            debug_info.append(f"Error en {csv_path}: {str(e)}")
            continue
    
    # Error con información de debug
    st.error("❌ No se encontró el archivo categories.csv")
    
    with st.expander("🔍 Debug - Click para ver detalles"):
        st.write("**Rutas probadas:**")
        for info in debug_info:
            st.code(info)
        
        st.write("\n**Directorio actual:**")
        st.code(os.getcwd())
        
        st.write("\n**Contenido del directorio raíz:**")
        try:
            files = os.listdir('.')
            for f in files:
                st.text(f"  - {f}")
            
            if 'data' in files:
                st.write("\n**Contenido de data/:**")
                data_files = os.listdir('data')
                for f in data_files:
                    st.text(f"  - {f}")
        except Exception as e:
            st.error(f"Error listando archivos: {e}")
    
    st.warning("""
    💡 **Pasos para solucionar:**
    
    1. Verifica que la carpeta `data/` está en GitHub
    2. Verifica que `categories.csv` está dentro de `data/`
    3. Haz push y reinicia la app en Streamlit Cloud
    """)
    
    return None

def get_categories_by_locale(df, locale):
    """Obtiene categorías filtradas por idioma"""
    if df is None:
        return []
    filtered = df[df['locale'] == locale]
    return filtered.to_dict('records')

def search_category(categories, search_term):
    """Búsqueda incremental en categorías"""
    if not search_term:
        return categories
    search_term = search_term.lower()
    return [cat for cat in categories if search_term in cat['name'].lower()]

# ============================================================================
# SCRAPING N8N
# ============================================================================

def scrape_pdp_n8n(product_id):
    """Scrapea PDP usando webhook n8n"""
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
# EJEMPLOS CSS
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
# GENERADORES DE SHORTCODES
# ============================================================================

def generate_product_module(article_id, nombre=""):
    """Genera shortcode de producto destacado"""
    return f'#MODULE_START#|{{"type":"article","params":{{"articleId":"{article_id}"}}}}|#MODULE_END#'

def generate_carousel_module(slug, category_id, order, navigation, loop, article_amount):
    """Genera shortcode de carrusel de categoría"""
    shortcode = {
        "type": "carouselArticle",
        "params": {
            "articlesIds": [],
            "slug": slug,
            "slugUuids": {
                "categoryId": category_id
            },
            "order": order,
            "articleAmount": article_amount,
            "activityName": "",
            "title": "",
            "collection": {
                "name": "",
                "id": ""
            },
            "navigation": navigation == "true",
            "loop": loop == "true"
        }
    }
    return f"#MODULE_START#|{json.dumps(shortcode)}|#MODULE_END#"

# ============================================================================
# UI - RENDERIZADO DE CAMPOS ESPECÍFICOS Y MÓDULOS
# ============================================================================

def render_campos_especificos(arquetipo_data):
    """
    Renderiza campos de input específicos según el arquetipo seleccionado
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

def render_module_configurator():
    """
    Renderiza la interfaz de configuración de módulos - VERSIÓN MEJORADA
    Con botones visuales para seleccionar tipo de módulo
    """
    st.markdown("### 📦 Módulos de Contenido")
    
    if 'modules_config' not in st.session_state:
        st.session_state.modules_config = []
    
    # Instrucción si está vacío
    if len(st.session_state.modules_config) == 0:
        st.info("👉 Click en **'➕ Nuevo Módulo'** para añadir productos destacados o carruseles de categoría al contenido.")
    
    categories_df = load_categories_data()
    
    # Botón para añadir
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("➕ Nuevo Módulo", key="add_module_btn", type="primary"):
            st.session_state.modules_config.append({
                'type': 'product',
                'id': len(st.session_state.modules_config)
            })
            st.rerun()
    
    with col2:
        if len(st.session_state.modules_config) > 0:
            if st.button("🗑️ Borrar Todos", key="clear_all_btn"):
                st.session_state.modules_config = []
                st.rerun()
    
    with col3:
        if len(st.session_state.modules_config) > 0:
            st.caption(f"📊 {len(st.session_state.modules_config)} módulo(s)")
    
    modules_data = []
    
    # Renderizar cada módulo
    for idx, module in enumerate(st.session_state.modules_config):
        st.markdown("---")
        
        # Header del módulo
        col_title, col_delete = st.columns([4, 1])
        with col_title:
            st.markdown(f"### 🔧 Módulo {idx + 1}")
        with col_delete:
            if st.button("❌", key=f"delete_{idx}", help="Eliminar este módulo"):
                st.session_state.modules_config.pop(idx)
                st.rerun()
        
        # SELECTOR DE TIPO CON BOTONES GRANDES Y VISUALES
        st.markdown("**Selecciona el tipo de módulo:**")
        
        col1, col2 = st.columns(2)
        
        current_type = module.get('type', 'product')
        
        with col1:
            # Botón Producto
            producto_selected = current_type == 'product'
            if st.button(
                "🎯 **Producto Destacado**",
                key=f"type_product_{idx}",
                use_container_width=True,
                type="primary" if producto_selected else "secondary"
            ):
                if current_type != 'product':
                    module['type'] = 'product'
                    st.rerun()
            
            if producto_selected:
                st.success("✅ Seleccionado")
            st.caption("Destaca un producto por su ID")
        
        with col2:
            # Botón Carrusel
            carousel_selected = current_type == 'carousel'
            if st.button(
                "🎠 **Carrusel de Categoría**",
                key=f"type_carousel_{idx}",
                use_container_width=True,
                type="primary" if carousel_selected else "secondary"
            ):
                if current_type != 'carousel':
                    module['type'] = 'carousel'
                    st.rerun()
            
            if carousel_selected:
                st.success("✅ Seleccionado")
            st.caption("Muestra productos de una categoría")
        
        module_data = {'type': current_type}
        
        st.markdown("---")
        
        # Configuración según tipo
        if current_type == 'product':
            st.markdown("#### ⚙️ Configuración del Producto Destacado")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                article_id = st.text_input(
                    "ID del producto (articleId)",
                    key=f"product_id_{idx}",
                    placeholder="10848823",
                    help="ID numérico del producto en PcComponentes"
                )
            with col2:
                nombre = st.text_input(
                    "Nombre (opcional)",
                    key=f"product_nombre_{idx}",
                    placeholder="Ej: Xiaomi E5"
                )
            
            if article_id:
                module_data['article_id'] = article_id
                module_data['nombre'] = nombre if nombre else f"Producto {idx + 1}"
                module_data['shortcode'] = generate_product_module(article_id, nombre)
                modules_data.append(module_data)
                
                st.success(f"✅ Configurado: {module_data['nombre']}")
                
                with st.expander("👁️ Vista previa del shortcode"):
                    st.code(module_data['shortcode'], language='text')
            else:
                st.warning("⚠️ Introduce el ID del producto")
        
        elif current_type == 'carousel':
            st.markdown("#### ⚙️ Configuración del Carrusel de Categoría")
            
            # Paso 1: Idioma
            locale = st.selectbox(
                "1️⃣ Idioma del catálogo",
                options=['es_ES', 'pt_PT', 'de_DE', 'fr_FR', 'it_IT'],
                format_func=lambda x: {
                    'es_ES': '🇪🇸 Español',
                    'pt_PT': '🇵🇹 Portugués',
                    'de_DE': '🇩🇪 Alemán',
                    'fr_FR': '🇫🇷 Francés',
                    'it_IT': '🇮🇹 Italiano'
                }[x],
                key=f"carousel_locale_{idx}"
            )
            
            if categories_df is not None:
                categories = get_categories_by_locale(categories_df, locale)
                
                # Paso 2: Búsqueda
                search_term = st.text_input(
                    "2️⃣ Buscar categoría",
                    key=f"carousel_search_{idx}",
                    placeholder="Ej: robot, monitor, teclado...",
                    help="Escribe para filtrar"
                )
                
                filtered_categories = search_category(categories, search_term)
                
                if len(filtered_categories) > 0:
                    category_names = [cat['name'] for cat in filtered_categories]
                    
                    selected_name = st.selectbox(
                        f"3️⃣ Seleccionar ({len(filtered_categories)} categorías)",
                        options=category_names,
                        key=f"carousel_category_{idx}"
                    )
                    
                    selected_category = next((cat for cat in filtered_categories if cat['name'] == selected_name), None)
                    
                    if selected_category:
                        st.info(f"📂 {selected_name}")
                        
                        st.markdown("**4️⃣ Parámetros del carrusel:**")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            order = st.radio(
                                "Ordenar por",
                                options=['relevance', 'price'],
                                format_func=lambda x: "⭐ Relevancia" if x == 'relevance' else "💰 Precio",
                                key=f"carousel_order_{idx}",
                                horizontal=True
                            )
                            
                            navigation = st.radio(
                                "Navegación",
                                options=['true', 'false'],
                                format_func=lambda x: "✅ Sí" if x == 'true' else "❌ No",
                                key=f"carousel_nav_{idx}",
                                horizontal=True
                            )
                        
                        with col2:
                            loop = st.radio(
                                "Bucle",
                                options=['true', 'false'],
                                format_func=lambda x: "🔄 Sí" if x == 'true' else "⏸️ No",
                                key=f"carousel_loop_{idx}",
                                horizontal=True
                            )
                            
                            article_amount = st.slider(
                                "Cantidad",
                                min_value=3,
                                max_value=50,
                                value=12,
                                key=f"carousel_amount_{idx}"
                            )
                        
                        module_data['category_name'] = selected_name
                        module_data['slug'] = selected_category['name_slug']
                        module_data['category_id'] = selected_category['category_id']
                        module_data['order'] = order
                        module_data['navigation'] = navigation
                        module_data['loop'] = loop
                        module_data['article_amount'] = article_amount
                        module_data['locale'] = locale
                        module_data['shortcode'] = generate_carousel_module(
                            selected_category['name_slug'],
                            selected_category['category_id'],
                            order,
                            navigation,
                            loop,
                            article_amount
                        )
                        
                        modules_data.append(module_data)
                        
                        st.success(f"✅ Configurado: {selected_name} ({article_amount} productos)")
                        
                        with st.expander("👁️ Vista previa del shortcode"):
                            st.code(module_data['shortcode'], language='text')
                else:
                    if search_term:
                        st.warning(f"No se encontraron categorías para '{search_term}'")
                    else:
                        st.info("👆 Escribe para buscar categorías")
            else:
                st.error("❌ No se pudo cargar categorías")
    
    # Resumen
    if len(modules_data) > 0:
        st.markdown("---")
        st.success(f"🎉 {len(modules_data)} módulo(s) listo(s)")
        
        with st.expander("📋 Resumen", expanded=True):
            for idx, mod in enumerate(modules_data):
                if mod['type'] == 'product':
                    st.markdown(f"**{idx + 1}.** 🎯 {mod['nombre']} (ID: {mod['article_id']})")
                else:
                    st.markdown(f"**{idx + 1}.** 🎠 {mod['category_name']} ({mod['article_amount']} productos)")
    
    return modules_data


def build_arquetipo_context(arquetipo_code, campos_valores):
    """Construye contexto específico del arquetipo"""
    if not campos_valores:
        return ""
    
    campos_llenos = {k: v for k, v in campos_valores.items() if v and v.strip()}
    
    if not campos_llenos:
        return ""
    
    context = f"\n# INFORMACIÓN ESPECÍFICA DEL ARQUETIPO {arquetipo_code}:\n\n"
    
    for campo_key, valor in campos_llenos.items():
        label = campo_key.replace('_', ' ').title()
        context += f"**{label}:**\n{valor}\n\n"
    
    context += "Usa esta información específica para crear contenido relevante.\n"
    
    return context

def get_arquetipo_guidelines(arquetipo_code):
    """Devuelve directrices específicas de estructura para cada arquetipo"""
    
    guidelines = {
        "ARQ-1": """
**Estructura Noticia:**
1. Lead con las 5W (qué, quién, cuándo, dónde, por qué)
2. Contexto y antecedentes
3. Detalles específicos
4. Implicaciones para usuarios
5. Fuentes y referencias
6. Conclusión con proyección futura

**Tono:** Informativo, urgente si procede.
""",
        "ARQ-2": """
**Estructura Guía:**
1. Introducción: qué se va a conseguir
2. Requisitos previos listados
3. Pasos numerados (3-10 típicamente)
4. Avisos de puntos críticos en callouts
5. Verificación final
6. Troubleshooting común

**Tono:** Instructivo, claro, paciente.
""",
        "ARQ-3": """
**Estructura Explicación:**
1. Hook: por qué importa
2. Definición simple primero
3. Explicación técnica progresiva
4. Analogías y ejemplos
5. Aplicaciones reales
6. Comparaciones si aplica
7. Takeaway clave

**Tono:** Educativo pero accesible.
""",
        "ARQ-4": """
**Estructura Review:**
1. Veredicto rápido
2. Contexto (precio, competencia)
3. Diseño y construcción
4. Rendimiento con datos reales
5. Experiencia de uso
6. Comparativa con competencia
7. FAQs
8. Veredicto final

**Tono:** Experto, honesto, equilibrado.
""",
        "ARQ-5": """
**Estructura Comparativa:**
1. Intro: por qué comparar
2. Tabla comparativa visual
3. Análisis Producto A
4. Análisis Producto B
5. Comparación por categorías
6. Veredicto: cuál elegir
7. Conclusión con recomendación

**Tono:** Imparcial, analítico.
""",
        "ARQ-6": """
**Estructura Deal Alert:**
1. Hook con precio en negrita
2. Por qué es chollo
3. Características clave
4. Para quién es perfecto
5. Duración y stock
6. CTA urgente
7. Alternativas si se agota

**Tono:** Urgente, directo.
""",
        "ARQ-7": """
**Estructura Roundup:**
1. Criterios de selección
2. Ganador destacado si lo hay
3. Producto #1-N con análisis
4. Tabla comparativa completa
5. Guía de compra
6. Conclusión por perfil

**Tono:** Autoridad, comprehensivo.
""",
        "ARQ-8": """
**Estructura Por Presupuesto:**
1. Qué esperar en este rango
2. Mejor opción destacada
3. Alternativas en el rango
4. Qué sacrificas vs superiores (positivo)
5. Tabla comparativa
6. Consejos para maximizar
7. Conclusión

**Tono:** Realista, honesto, optimista.
""",
        "ARQ-9": """
**Estructura Versus:**
1. Presentación de contendientes
2. Round 1-N por categoría
3. Tabla puntuación final
4. Ganador absoluto y por qué
5. Cuándo elegir al perdedor

**Tono:** Deportivo, entretenido, riguroso.
""",
        "ARQ-10": """
**Estructura Por Perfil:**
1. Definición del perfil
2. Necesidades específicas
3. Producto recomendado y por qué
4. Características clave
5. Qué NO necesita (ahorro)
6. Alternativas si varía
7. Conclusión personalizada

**Tono:** Empático, consultivo.
""",
        "ARQ-11": """
**Estructura Tendencias:**
1. Contexto: situación actual
2. Tendencia con datos
3. Causas
4. Predicción de evolución
5. Impacto para consumidores
6. Recomendaciones prácticas
7. Qué hacer ahora

**Tono:** Analítico, con autoridad.
""",
        "ARQ-12": """
**Estructura Unboxing:**
1. Primera impresión caja/packaging
2. Contenido completo
3. Construcción y materiales
4. Sorpresas positivas
5. Decepciones (neutral)
6. Setup inicial
7. Primeras horas de uso
8. Veredicto preliminar

**Tono:** Entusiasta, descriptivo, honesto.
"""
    }
    
    return guidelines.get(arquetipo_code, "Sigue mejores prácticas del arquetipo.")

def build_generation_prompt_with_modules(pdp_data, arquetipo, length, keywords, context, 
                                          links, modules, objetivo, producto_alternativo, casos_uso, campos_arquetipo):
    """Construye prompt completo para generación incluyendo módulos"""
    
    keywords_str = ", ".join(keywords) if keywords else "No especificadas"
    
    # Contexto del arquetipo
    arquetipo_context = build_arquetipo_context(arquetipo['code'], campos_arquetipo)
    
    # Enlaces
    link_principal = links.get('principal', {})
    links_secundarios = links.get('secundarios', [])
    
    link_info = ""
    if link_principal.get('url'):
        link_info = f"""
# ENLACES A INCLUIR:
## Enlace Principal (OBLIGATORIO):
URL: {link_principal.get('url')}
Texto anchor: {link_principal.get('text')}
Ubicación: Primeros 2-3 párrafos
"""
    
    if links_secundarios:
        link_info += f"""
## Enlaces Secundarios:
{chr(10).join([f"- URL: {link.get('url')} | Texto: {link.get('text')}" for link in links_secundarios])}
"""

    # Producto alternativo
    alternativo_info = ""
    if producto_alternativo.get('url'):
        alternativo_info = f"""
# PRODUCTO ALTERNATIVO:
URL: {producto_alternativo.get('url')}
Texto: {producto_alternativo.get('text', 'producto alternativo')}
IMPORTANTE: Incluir en "Considera alternativas si:" con enlace.
"""
    else:
        casos_uso_str = ""
        if casos_uso:
            casos_uso_str = f"\nCasos de uso:\n" + "\n".join([f"- {caso}" for caso in casos_uso])
        alternativo_info = f"""
# PRODUCTO ALTERNATIVO: NO CONFIGURADO
Box veredicto solo con "✅ Perfecto si:" desarrollado extensamente.{casos_uso_str}
"""

    # Módulos
    module_info = ""
    if modules and len(modules) > 0:
        module_info = f"""
# MÓDULOS DE CONTENIDO (CRÍTICO - DEBEN APARECER TODOS):

{len(modules)} módulo(s) configurado(s) que DEBEN incluirse.

"""
        
        for idx, mod in enumerate(modules):
            module_info += f"\n## Módulo {idx + 1}:\n"
            
            if mod['type'] == 'product':
                module_info += f"""
**Tipo:** Producto Destacado
**ID:** {mod['article_id']}
**Nombre:** {mod['nombre']}
**Shortcode EXACTO:**
```
{mod['shortcode']}
```
**Ubicación:** Después de mencionar el producto o en análisis.
"""
            
            elif mod['type'] == 'carousel':
                module_info += f"""
**Tipo:** Carrusel de Categoría
**Categoría:** {mod['category_name']}
**Idioma:** {mod['locale']}
**Cantidad:** {mod['article_amount']} productos
**Orden:** {"Por relevancia" if mod['order'] == 'relevance' else "Por precio"}

**Shortcode EXACTO:**
```
{mod['shortcode']}
```
**Ubicación:** Secciones de alternativas, exploración o al final antes de FAQs.
**Contexto:** Muestra automáticamente {mod['article_amount']} productos de "{mod['category_name']}" ordenados por {mod['order']}.
"""
        
        module_info += """

**CRÍTICO SOBRE MÓDULOS:**
1. TODOS deben aparecer en el contenido
2. Usa shortcode EXACTO (no modificar JSON)
3. Cada módulo en su propia línea
4. Decide ubicación óptima por contexto
5. Añade 1-2 frases antes del módulo explicando qué verá el usuario
6. NO uses marcadores - usa shortcodes reales

**Ejemplo de integración:**
```
Si buscas alternativas, aquí tienes más opciones:

#MODULE_START#|{"type":"carouselArticle",...}|#MODULE_END#

Todos comparten características similares.
```
"""

    prompt = f"""
Eres experto redactor de PcComponentes para contenido optimizado Google Discover.

# OBJETIVO DEL CONTENIDO:
{objetivo}

# TONO DE MARCA:
{BRAND_TONE}

# ARQUETIPO:
{arquetipo['code']} - {arquetipo['name']}
{arquetipo['description']}
Caso de uso: {arquetipo['use_case']}

{arquetipo_context}

# DATOS PRODUCTO (si aplica):
{json.dumps(pdp_data, indent=2, ensure_ascii=False) if pdp_data else "N/A"}

# CONTEXTO:
{context if context else "Condiciones estándar PcComponentes"}

# KEYWORDS SEO:
{keywords_str}

# LONGITUD:
{length} palabras aproximadamente

{link_info}

{alternativo_info}

{module_info}

# FORMATO OUTPUT:

Genera SOLO el artículo (desde <style> hasta </article>).

{EJEMPLOS_CSS}

<article>
[CONTENIDO COMPLETO]
</article>

# ADAPTACIÓN AL ARQUETIPO {arquetipo['code']}:

{get_arquetipo_guidelines(arquetipo['code'])}

# ELEMENTOS OBLIGATORIOS:

✅ Kicker con categoría
✅ Título H2 optimizado
✅ Estructura arquetipo {arquetipo['code']}
✅ Enlaces integrados
✅ TODOS los módulos con shortcodes exactos
✅ Tono aspiracional
✅ Emojis: solo ✅ ⚡ ❌
✅ FAQs con schema JSON-LD

Genera AHORA el contenido completo.
"""
    
    return prompt

# ============================================================================
# GENERATOR CLASS
# ============================================================================

class ContentGenerator:
    """Generador con Claude API"""
    
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
# FUNCIÓN DE VERIFICACIÓN GSC
# ============================================================================

def render_gsc_verification_section(keywords_input):
    """
    Renderiza sección de verificación GSC
    Args:
        keywords_input: String con keywords separadas por comas
    Returns:
        bool: True si debe bloquear generación por alertas críticas
    """
    if not keywords_input or not GSC_CLIENT_CONFIG:
        if keywords_input and not GSC_CLIENT_CONFIG:
            st.info("💡 Configura GSC_CLIENT_CONFIG en secrets para verificar contenido existente")
        return False
    
    st.markdown("### 🔍 Verificación de Contenido Existente")
    
    # Autenticación GSC
    with st.expander("🔐 Conectar con Google Search Console", expanded=False):
        gsc_credentials = render_gsc_auth_ui(GSC_CLIENT_CONFIG)
    
    # Si está autenticado, mostrar botón de verificación
    if 'gsc_credentials' in st.session_state and st.session_state.gsc_credentials:
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            check_gsc = st.button(
                "🔍 Verificar si existe contenido para estas keywords",
                type="secondary",
                use_container_width=True
            )
        
        with col2:
            auto_check = st.checkbox(
                "Auto-verificar", 
                value=False, 
                help="Verificar automáticamente al cambiar keywords"
            )
        
        # Realizar verificación
        should_check = check_gsc or (auto_check and keywords_input and 'last_checked_keyword' not in st.session_state)
        
        if should_check:
            # Tomar primera keyword como principal
            main_keyword = keywords_input.split(',')[0].strip()
            st.session_state['last_checked_keyword'] = main_keyword
            
            with st.spinner(f"🔍 Consultando Google Search Console para '{main_keyword}'..."):
                try:
                    # Inicializar checker
                    site_url = st.secrets.get('GSC_SITE_URL', 'https://www.pccomponentes.com/')
                    checker = GSCChecker(site_url=site_url)
                    
                    # Autenticar
                    if checker.authenticate_with_credentials(st.session_state.gsc_credentials):
                        
                        # Verificar keyword con variaciones
                        results = checker.check_keyword_comprehensive(
                            keyword=main_keyword,
                            periods=[1, 7, 28],
                            position_threshold=30,
                            impressions_threshold=50
                        )
                        
                        # Guardar resultados
                        st.session_state['gsc_check_results'] = results
                    
                    else:
                        st.error("Error autenticando con GSC")
                
                except Exception as e:
                    st.error(f"Error verificando GSC: {str(e)}")
        
        # Mostrar resultados si existen
        if 'gsc_check_results' in st.session_state:
            render_gsc_check_results(st.session_state.gsc_check_results)
            
            # Si hay alertas críticas, mostrar confirmación
            alerts = st.session_state.gsc_check_results.get('alerts', [])
            critical_alerts = [a for a in alerts if a['level'] == 'critical']
            
            if critical_alerts:
                st.markdown("---")
                st.session_state['confirm_new_content'] = st.checkbox(
                    "⚠️ Confirmo que quiero crear NUEVO contenido (no actualizar existente)",
                    value=False,
                    help="Activa esto solo si estás seguro de que quieres crear contenido nuevo a pesar de las alertas"
                )
                
                if not st.session_state.get('confirm_new_content', False):
                    st.warning("⏸️ Debes confirmar para continuar con la generación de contenido nuevo")
                    return True  # Bloquear generación
            
            return False  # No bloquear
    
    elif not keywords_input:
        st.info("💡 Introduce keywords para verificar si ya existe contenido rankeando")
    
    return False  # No bloquear si no hay verificación

# ============================================================================
# UI PRINCIPAL
# ============================================================================

def render_sidebar():
    """Sidebar con info"""
    with st.sidebar:
        st.markdown("## Content Generator")
        st.markdown("**PcComponentes**")
        st.markdown("---")
        
        st.markdown("### 🆕 V3.1 + GSC")
        st.markdown("✅ 12 arquetipos completos")
        st.markdown("✅ Sistema dual de módulos")
        st.markdown("✅ Campos específicos por arquetipo")
        st.markdown("✅ Búsqueda de categorías")
        st.markdown("✅ Verificación GSC")
        st.markdown("---")
        
        st.markdown("### Info")
        st.markdown("Versión 3.1 + GSC")
        st.markdown("© 2025 PcComponentes")

def main():
    """App principal"""
    
    render_sidebar()
    
    st.title("Content Generator V3.1 + GSC")
    st.markdown("12 Arquetipos + Sistema Dual de Módulos + Verificación GSC")
    st.markdown("---")
    
    if 'ANTHROPIC_API_KEY' not in st.secrets:
        st.error("Configura ANTHROPIC_API_KEY en secrets")
        st.stop()
    
    # SECCIÓN 1: Producto
    st.header("1. Producto Principal (Opcional)")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        product_id = st.text_input(
            "ID del producto",
            placeholder="10848823 (opcional según arquetipo)",
            help="ID numérico del producto"
        )
    
    with col2:
        use_mock = st.checkbox("Datos ejemplo", value=True, help="Testing sin VPN")
    
    # SECCIÓN 2: Arquetipo
    st.header("2. Tipo de Contenido")
    
    col1, col2 = st.columns(2)
    
    with col1:
        arquetipo_code = st.selectbox(
            "Arquetipo",
            options=list(ARQUETIPOS.keys()),
            format_func=lambda x: f"{ARQUETIPOS[x]['name']}"
        )
        arquetipo = ARQUETIPOS[arquetipo_code]
        
        st.info(f"**{arquetipo['name']}**\n\n{arquetipo['description']}\n\n*Uso:* {arquetipo['use_case']}")
    
    with col2:
        content_length = st.slider(
            "Longitud (palabras)",
            min_value=800,
            max_value=3000,
            value=arquetipo['default_length'],
            step=100
        )
    
    # Objetivo
    objetivo = st.text_area(
        "Objetivo del contenido (OBLIGATORIO)",
        placeholder="Ej: Convertir usuarios destacando precio histórico",
        help="Describe qué quieres lograr",
        height=100
    )
    
    if not objetivo:
        st.warning("⚠️ El objetivo es obligatorio")
    
    # Keywords (movidas aquí desde configuración avanzada)
    st.markdown("---")
    keywords = st.text_input(
        "Keywords SEO principales (separadas por comas)",
        placeholder="robot aspirador xiaomi, oferta black friday",
        help="Se verificará si ya existe contenido rankeando para estas keywords"
    )
    
    # Verificación GSC (NUEVA SECCIÓN)
    st.markdown("---")
    block_generation = render_gsc_verification_section(keywords)
    
    # Campos específicos del arquetipo
    st.markdown("---")
    campos_arquetipo = render_campos_especificos(arquetipo)
    
    # SECCIÓN 3: Módulos
    st.markdown("---")
    st.header("3. Módulos de Contenido")
    
    modules_data = render_module_configurator()
    
    # SECCIÓN 4: Enlaces (AHORA VISIBLE)
    st.markdown("---")
    st.header("4. Enlaces Internos")
    
    st.markdown("### 🔗 Enlace Principal")
    col1, col2 = st.columns(2)
    with col1:
        link_principal_url = st.text_input(
            "URL enlace principal",
            placeholder="https://www.pccomponentes.com/black-friday",
            help="URL de categoría Black Friday o PDP principal"
        )
    with col2:
        link_principal_text = st.text_input(
            "Texto anchor principal",
            placeholder="Ej: ofertas Black Friday",
            help="Texto del enlace"
        )
    
    st.markdown("### 🔗 Enlaces Secundarios (hasta 3)")
    links_secundarios = []
    for i in range(3):
        col1, col2 = st.columns(2)
        with col1:
            url = st.text_input(
                f"URL secundario {i+1}",
                key=f"sec_url_{i}",
                placeholder="https://www.pccomponentes.com/..."
            )
        with col2:
            text = st.text_input(
                f"Texto anchor {i+1}",
                key=f"sec_text_{i}",
                placeholder="Ej: nombre producto"
            )
        
        if url and text:
            links_secundarios.append({"url": url, "text": text})
    
    # SECCIÓN 5: Configuración avanzada
    st.markdown("---")
    with st.expander("⚙️ Configuración Avanzada", expanded=False):
        
        context = st.text_area(
            "Contexto adicional",
            placeholder="Stock limitado, válido hasta...",
            height=80
        )
        
        st.markdown("---")
        st.markdown("### 🔄 Producto Alternativo")
        
        col1, col2 = st.columns(2)
        with col1:
            alternativo_url = st.text_input("URL producto alternativo", key="alt_url")
        with col2:
            alternativo_text = st.text_input("Texto", placeholder="Ej: Roborock S7", key="alt_text")
        
        st.markdown("### 📋 Casos de Uso")
        casos_uso_text = st.text_area(
            "Casos de uso (uno por línea)",
            placeholder="Pisos pequeños\nMantenimiento diario",
            height=100
        )
        casos_uso = [caso.strip() for caso in casos_uso_text.split('\n') if caso.strip()] if casos_uso_text else []
    
    # Botón generar
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate = st.button(
            "🚀 Generar Contenido",
            type="primary",
            use_container_width=True,
            disabled=(not objetivo or block_generation)
        )
    
    # Proceso de generación
    if generate:
        
        # Limpiar resultados GSC previos para nueva generación
        if 'gsc_check_results' in st.session_state:
            del st.session_state['gsc_check_results']
        if 'last_checked_keyword' in st.session_state:
            del st.session_state['last_checked_keyword']
        if 'confirm_new_content' in st.session_state:
            del st.session_state['confirm_new_content']
        
        pdp_data = None
        if product_id:
            if use_mock:
                pdp_data = get_mock_pdp_data(product_id)
                st.info("ℹ️ Usando datos de ejemplo")
            else:
                with st.spinner("🔄 Conectando al webhook n8n..."):
                    pdp_data = scrape_pdp_n8n(product_id)
                
                if not pdp_data:
                    st.error("❌ Error obteniendo datos")
                    st.stop()
                
                st.success("✅ Datos obtenidos")
        
        keywords_list = [k.strip() for k in keywords.split(",")] if keywords else []
        
        links = {
            "principal": {"url": link_principal_url, "text": link_principal_text} if link_principal_url else {},
            "secundarios": links_secundarios
        }
        
        producto_alternativo = {
            "url": alternativo_url,
            "text": alternativo_text
        } if alternativo_url else {}
        
        generator = ContentGenerator(st.secrets['ANTHROPIC_API_KEY'])
        
        progress = st.progress(0)
        status = st.status("⏳ Generando contenido...", expanded=True)
        
        status.write(f"📝 Generando contenido tipo '{arquetipo['name']}'...")
        prompt_gen = build_generation_prompt_with_modules(
            pdp_data, arquetipo, content_length,
            keywords_list, context, links, modules_data, objetivo,
            producto_alternativo, casos_uso, campos_arquetipo
        )
        
        final_content = generator.generate(prompt_gen)
        if not final_content:
            st.error("❌ Error en generación")
            st.stop()
        
        progress.progress(100)
        status.update(label="✅ Completado", state="complete")
        
        st.session_state.results = {
            'final': final_content,
            'metadata': {
                'product_id': product_id or "N/A",
                'arquetipo': arquetipo_code,
                'objetivo': objetivo,
                'keywords': keywords_list,
                'campos_arquetipo': campos_arquetipo,
                'modulos': modules_data,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        st.markdown("---")
        st.success(f"✅ Contenido generado")
        
        with st.expander("📋 Configuración aplicada", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Arquetipo:** {arquetipo['name']}")
                st.markdown(f"**Producto:** {product_id or 'N/A'}")
            with col2:
                st.markdown(f"**Módulos:** {len(modules_data)}")
                if len(modules_data) > 0:
                    for mod in modules_data:
                        if mod['type'] == 'product':
                            st.markdown(f"- 🎯 {mod['nombre']}")
                        else:
                            st.markdown(f"- 🎠 {mod['category_name']}")
            with col3:
                st.markdown(f"**Alternativo:** {'✅' if producto_alternativo else '❌'}")
                st.markdown(f"**Casos uso:** {len(casos_uso)}")
                st.markdown(f"**Keywords:** {len(keywords_list)}")
        
        st.markdown("### 📄 Contenido Final")
        
        with st.expander("👁️ Vista previa renderizada", expanded=True):
            st.components.v1.html(final_content, height=800, scrolling=True)
        
        with st.expander("</> Código HTML"):
            st.code(final_content, language='html')
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "⬇️ Descargar HTML",
                data=final_content,
                file_name=f"contenido_{arquetipo_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                use_container_width=True
            )
        with col2:
            st.download_button(
                "⬇️ Descargar JSON",
                data=json.dumps(st.session_state.results, indent=2, ensure_ascii=False),
                file_name=f"generacion_{arquetipo_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

if __name__ == "__main__":
    main()
