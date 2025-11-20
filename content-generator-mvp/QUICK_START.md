# 🎯 GUÍA DE INICIO RÁPIDO - MVP

## 📂 Archivos del proyecto

```
content-generator-mvp/
│
├── app.py                      ← App principal (ejecutar este)
├── requirements.txt            ← Dependencias Python
├── setup.sh                    ← Script de instalación rápida
├── README.md                   ← Documentación completa
├── .gitignore                  ← Archivos a ignorar en Git
├── secrets.toml.example        ← Plantilla de configuración
│
└── .streamlit/
    └── config.toml             ← Configuración tema PcComponentes
```

## ⚡ Setup en 3 pasos

### Opción A: Setup automático (Linux/Mac)

```bash
# 1. Entrar al directorio
cd content-generator-mvp

# 2. Ejecutar script de setup
chmod +x setup.sh
./setup.sh

# 3. Configurar API key
nano .streamlit/secrets.toml
# Añadir: ANTHROPIC_API_KEY = "sk-ant-api03-..."

# 4. Lanzar app
streamlit run app.py
```

### Opción B: Setup manual (Todas las plataformas)

```bash
# 1. Instalar dependencias
pip install streamlit anthropic --break-system-packages

# 2. Crear archivo de secrets
mkdir -p .streamlit
cp secrets.toml.example .streamlit/secrets.toml

# 3. Editar y añadir tu API key
# Archivo: .streamlit/secrets.toml
# Línea: ANTHROPIC_API_KEY = "tu-key-aqui"

# 4. Ejecutar
streamlit run app.py
```

## 🔑 Conseguir API Key de Claude

1. Ve a: https://console.anthropic.com/
2. Crea cuenta / Inicia sesión
3. Settings → API Keys
4. "Create Key"
5. Copia la key (empieza con `sk-ant-api03-...`)
6. Pégala en `.streamlit/secrets.toml`

## 🎬 Primera ejecución

1. La app se abrirá en `http://localhost:8501`
2. Verás la interfaz con el logo de PcComponentes
3. Activa "Usar datos de ejemplo" para probar
4. Introduce cualquier URL (se usarán datos mock)
5. Selecciona arquetipo (prueba ARQ-4 primero)
6. Click "🚀 Generar Contenido"
7. Espera 1-2 minutos (3 llamadas a Claude API)
8. ¡Verás los 3 outputs!

## 📊 Qué hace el MVP

### INPUT del usuario:
- URL producto (mock disponible)
- Arquetipo (ARQ-4, ARQ-7, ARQ-8)
- Longitud (800-3000 palabras)
- [Opcional] Keywords SEO
- [Opcional] Contexto BF
- [Opcional] Comparativa competidores

### PROCESO (3 pasos):
1. **Generación inicial** → HTML completo con estructura
2. **Análisis** → Identifica mejoras necesarias
3. **Versión final** → Aplica correcciones

### OUTPUT:
- ✅ HTML con CSS inline
- ✅ Optimizado Google Discover
- ✅ Tono PcComponentes
- ✅ Estructura arquetipo
- ✅ Schema JSON-LD
- ✅ CTAs directos
- ✅ Descargable

## 🎨 Arquetipos disponibles

### ARQ-4: Review/Análisis
**Mejor para:** Producto único en oferta destacada  
**Estructura:** Veredicto → Specs → Rendimiento → Opiniones → Comparativa → FAQs  
**Ejemplo:** "Robot Xiaomi E5 a 59€: análisis completo"

### ARQ-7: Roundup
**Mejor para:** Top X productos de una categoría  
**Estructura:** Intro → Producto 1 → Producto 2 → Producto N → Tabla → Guía  
**Ejemplo:** "Los 5 mejores robots aspiradores Black Friday 2025"

### ARQ-8: Por presupuesto
**Mejor para:** Chollos en rango de precio específico  
**Estructura:** Justificación precio → Mejor calidad-precio → Alternativas → Cómo elegir  
**Ejemplo:** "Mejores monitores gaming por menos de 100€"

## 💡 Tips para mejores resultados

### ✅ HACER:
- Usar "datos de ejemplo" para probar
- Probar los 3 arquetipos
- Añadir keywords específicas
- Incluir contexto BF (fechas, stock)
- Descargar las 3 versiones para comparar

### ❌ EVITAR:
- Ejecutar sin API key configurada
- URLs de productos no existentes (sin mock)
- Longitud < 800 o > 3000 palabras
- Generar múltiples veces muy rápido (rate limits)

## 🐛 Problemas comunes

### "Error: ANTHROPIC_API_KEY not found"
**Solución:** Crea `.streamlit/secrets.toml` con la key

### "Rate limit exceeded"
**Solución:** Espera 1 minuto entre generaciones

### "Module not found: anthropic"
**Solución:** `pip install anthropic`

### La app no se abre
**Solución:** Verifica que el puerto 8501 está libre

## 📈 Próximos pasos

Una vez funcione el MVP:

1. **Integrar scraping real:**
   - Endpoint n8n para PDP
   - Zenrows para PLP

2. **Añadir funcionalidades:**
   - Más arquetipos
   - Historial de generaciones
   - Exportar a CMS
   - Sistema de validación

3. **Deploy en Streamlit Cloud:**
   - Push a GitHub
   - Conectar en streamlit.io
   - Configurar secrets online
   - URL pública

## 🎯 Testing recomendado

### Caso 1: Review básico
- Arquetipo: ARQ-4
- Longitud: 1800 palabras
- Mock: activado
- Resultado esperado: ~2 min, HTML completo

### Caso 2: Con keywords
- Arquetipo: ARQ-4
- Keywords: "robot aspirador barato, xiaomi oferta"
- Resultado: Keywords integradas naturalmente

### Caso 3: Con contexto BF
- Arquetipo: ARQ-4
- Contexto: "Stock: 20 unidades, válido hasta 30/11"
- Resultado: Urgencia visible en callouts

## 📞 Soporte

- README completo: `README.md`
- Errores: Revisa consola de Streamlit
- Dudas: Documentación Anthropic

---

**¡Listo para generar contenido!** 🚀
