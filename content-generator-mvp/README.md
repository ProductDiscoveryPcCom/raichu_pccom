# 🛒 Content Generator Black Friday - MVP

Generador de contenido optimizado para Google Discover durante Black Friday de PcComponentes.

## 🚀 Quick Start

### 1. Instalar dependencias

```bash
pip install -r requirements.txt --break-system-packages
```

### 2. Configurar API Key de Claude

Crea el archivo `.streamlit/secrets.toml` con tu API key:

```bash
mkdir -p .streamlit
cp secrets.toml.example .streamlit/secrets.toml
```

Edita `.streamlit/secrets.toml` y añade tu API key de Anthropic:

```toml
ANTHROPIC_API_KEY = "sk-ant-api03-tu-key-aqui"
```

**¿Cómo conseguir la API key?**
1. Ve a https://console.anthropic.com/
2. Crea una cuenta o inicia sesión
3. Ve a "API Keys"
4. Crea una nueva key

### 3. Ejecutar la aplicación

```bash
streamlit run app.py
```

Se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📋 Cómo usar

### Flujo básico:

1. **Introduce URL del producto** (o usa datos de ejemplo)
2. **Selecciona arquetipo de contenido:**
   - ARQ-4: Review/Análisis (producto único)
   - ARQ-7: Roundup (top X productos)
   - ARQ-8: Por presupuesto (mejores por X€)
3. **Ajusta longitud** del contenido (800-3000 palabras)
4. **[Opcional] Añade configuración avanzada:**
   - Keywords SEO específicas
   - Contexto Black Friday (fechas, stock)
   - Comparativa con competidores
5. **Genera contenido** → Obtendrás 3 versiones:
   - Inicial
   - Correcciones
   - Final optimizada

### Datos de ejemplo:

Para probar sin configurar scraping:
- Activa "Usar datos de ejemplo"
- Usa cualquier URL de PcComponentes
- Los datos mock simulan un robot aspirador Xiaomi

## 🏗️ Arquitectura MVP

```
app.py              # Todo-en-uno: UI + lógica + prompts
├── Datos mock      # Simula scraping (reemplazar luego)
├── Arquetipos      # ARQ-4, ARQ-7, ARQ-8
├── Tono de marca   # Manual PcComponentes
├── Prompt builder  # Construcción de prompts
└── Generator       # Llamadas a Claude API
```

## 📦 Estructura de salida

El contenido generado incluye:

### HTML con:
- ✅ CSS inline (paleta PcComponentes)
- ✅ Estructura responsive
- ✅ Badges y callouts
- ✅ Tablas comparativas
- ✅ FAQs con schema JSON-LD
- ✅ CTAs optimizados
- ✅ Links directos al producto

### Versiones:
1. **Inicial**: Primera generación
2. **Correcciones**: Análisis y mejoras
3. **Final**: Versión optimizada aplicando correcciones

## 🎯 Arquetipos disponibles

| Código | Nombre | Descripción | Ideal para |
|--------|--------|-------------|-----------|
| ARQ-4 | Review/Análisis | Análisis profundo producto | Producto único destacado |
| ARQ-7 | Roundup | Top X productos | Lista categoría BF |
| ARQ-8 | Por presupuesto | Mejores por X€ | Chollos específicos |

## 🔧 Próximos pasos (post-MVP)

- [ ] Integrar endpoint n8n para scraping real PDP
- [ ] Implementar Zenrows para scraping PLP
- [ ] Añadir más arquetipos (5, 10, 12, 13)
- [ ] Sistema de historial de generaciones
- [ ] Exportar a CMS directo
- [ ] A/B testing de títulos
- [ ] Métricas de calidad automáticas

## 🐛 Troubleshooting

### Error: "ANTHROPIC_API_KEY no configurada"
- Verifica que `.streamlit/secrets.toml` existe
- Comprueba que la key es válida y no ha expirado

### Error: "Rate limit exceeded"
- Espera unos minutos
- Verifica tu plan de Anthropic (límites por minuto)

### El contenido no se genera
- Revisa la consola para ver errores de API
- Verifica conexión a internet
- Comprueba que la API key tiene créditos

## 📄 Licencia

PcComponentes © 2025 - Uso interno

## 🤝 Soporte

Para dudas o problemas:
- Documentación: [Link interno]
- Slack: #content-discovery
- Email: discovery-team@pccomponentes.com

---

**Versión:** MVP 1.0  
**Fecha:** Noviembre 2025  
**Status:** ✅ Funcional para testing
