# CHANGELOG - Versión 2.0

## Cambios Implementados

### 🎨 Mejoras de Tono y Estilo

#### Emojis Restringidos
- **ANTES**: Uso libre de cualquier emoji
- **AHORA**: Solo permitidos ✅ ⚡ ❌
  - ✅ Para puntos positivos
  - ⚡ Para urgencia/velocidad
  - ❌ SOLO en comparativas técnicas

#### Tono Aspiracional (No Negativo)
- **ELIMINADO**: Frases como "Evita si...", "No compres si...", "No recomendado"
- **AÑADIDO**: Lenguaje positivo:
  - ❌ "Este producto no tiene mapeo"
  - ✅ "Limpia toda tu casa; si necesitas control por habitaciones, hay modelos con láser"
  
### 📄 Estructura de Output

#### Antes (V1.0)
```html
<html>
<head>
  <style>...</style>
</head>
<body>
  <article>...</article>
</body>
</html>
```

#### Ahora (V2.0)
```html
<style>...</style>
<article>...</article>
```

**Razón**: El CMS solo necesita el contenido del post, no la página completa.

### 🔗 Sistema de Enlaces

#### Nuevos Campos en Configuración
1. **Enlace Principal** (obligatorio):
   - URL y texto anchor
   - Se integra en primeros 2-3 párrafos
   
2. **Enlaces Secundarios** (hasta 3):
   - URL y texto anchor para cada uno
   - Se integran contextualmente donde mejor encajen

**Anchor Text**: Siempre descriptivo, nunca "clic aquí"

### 📦 Módulos de Productos

#### Nuevo Sistema Opcional
```html
#MODULE_START#|{"type":"article","params":{"articleId":"10869987"}}|#MODULE_END#
```

**Características**:
- Usuario proporciona IDs de productos (articleId)
- IA decide dónde incluirlos según flujo del contenido
- Opcional: si no aportan valor, no se incluyen
- Máximo 1-2 módulos por artículo
- Típicamente después de mencionar el producto

### 🔌 Integración con N8N

#### Scraping Real de PDP
- **Webhook**: `https://n8n.prod.pccomponentes.com/webhook/extract-product-data`
- **Método**: POST con `{"productId": "10848823"}`
- **Requisito**: Usuario debe estar conectado a VPN
- **Fallback**: Datos mock para testing sin VPN

**Input**: ID del producto (ej: 10848823)  
**Output**: Todos los datos de la PDP automáticamente

### 📚 Arquetipos Ampliados

#### ANTES (V1.0)
- ARQ-4: Review
- ARQ-7: Roundup
- ARQ-8: Por presupuesto

#### AHORA (V2.0)
- ARQ-4: Review / Análisis
- **ARQ-5: Comparativa A vs B** (NUEVO)
- ARQ-7: Roundup / Mejores X
- ARQ-8: Por presupuesto
- **ARQ-10: Por perfil de usuario** (NUEVO)

**Casos de uso**:
- No solo Black Friday
- Lanzamientos de productos
- Guías de compra
- Comparativas directas
- Segmentación por audiencia

### 🔄 Proceso de Generación Mejorado

#### ANTES (V1.0)
1. Generación inicial
2. Análisis de correcciones
3. Versión final

#### AHORA (V2.0)
1. **Generación inicial** con todos los datos
2. **Corrección crítica** basada en objetivo del usuario
3. **Versión final optimizada**

### 🎯 Campo Obligatorio: Objetivo del Contenido

**Nuevo campo OBLIGATORIO**:
```
Objetivo del contenido:
"Convertir usuarios indecisos en compradores destacando 
el precio histórico y urgencia Black Friday. El contenido 
debe resolver dudas sobre calidad-precio y comparar con competencia."
```

**Uso**:
- La IA lo usa para corrección crítica en paso 2
- Asegura alineación con objetivos de negocio
- Evalúa si el contenido cumple su propósito

### 📊 Ejemplos de CSS

**Integrados en el sistema**:
- Paleta completa de PcComponentes
- Clases: `.kicker`, `.badges`, `.verdict`, `.toc`, `.callout`, `.lt`, `.btn`, `.card`
- Estilos responsive
- Gradientes y efectos visuales

### ✅ Checklist de Elementos Obligatorios

El sistema ahora verifica:
- ✅ Kicker con categoría
- ✅ Título H2 (NO H1)
- ✅ Badges con specs clave
- ✅ Box veredicto con gradiente
- ✅ TOC navegable con anchors
- ✅ Callouts estratégicos
- ✅ Tablas comparativas (.lt)
- ✅ Botones CTA (.btn)
- ✅ FAQs al final
- ✅ Schema JSON-LD FAQPage
- ✅ Enlaces integrados correctamente
- ✅ Módulos (si aplicable)

## Flujo de Uso Actualizado

### 1. Configurar Producto
```
ID del producto: 10848823
☑ Datos ejemplo (para testing sin VPN)
```

### 2. Seleccionar Arquetipo
```
Arquetipo: ARQ-4 - Review / Análisis
Longitud: 1800 palabras
```

### 3. Definir Objetivo (OBLIGATORIO)
```
Objetivo: "Convertir usuarios destacando precio histórico..."
```

### 4. Configuración Avanzada (Opcional)
```
Keywords: robot aspirador xiaomi, oferta
Contexto: Stock limitado 50 unidades
Enlaces: 
  - Principal: URL + Texto
  - Secundarios: 3 opcionales
Módulos: IDs de productos para destacar
```

### 5. Generar
```
Paso 1/3: Generación inicial...
Paso 2/3: Corrección crítica...
Paso 3/3: Optimización final...
✅ Completado
```

### 6. Resultado
```
3 Tabs:
1. Versión Inicial
2. Corrección Crítica (análisis detallado)
3. Versión Final (HTML optimizado)
```

## Dependencias Actualizadas

```txt
streamlit==1.32.0
anthropic==0.21.0
httpx==0.27.0
requests==2.31.0  # NUEVO: para webhook n8n
```

## Notas de Migración V1.0 → V2.0

### Cambios Breaking
1. Campo "Objetivo" ahora OBLIGATORIO
2. Output cambia de página completa a solo artículo
3. Emojis restringidos

### Compatibilidad
✅ Secrets: Mismo formato  
✅ Streamlit Cloud: Compatible  
✅ GitHub: Push normalmente  

### Nuevas Funcionalidades Opcionales
- Enlaces configurables
- Módulos de productos
- Scraping n8n (requiere VPN)
- Más arquetipos

## Testing Recomendado

### Test 1: Con datos mock
```
ID: 10848823
Datos ejemplo: ☑
Arquetipo: ARQ-4
Objetivo: "Destacar precio histórico"
```

### Test 2: Con webhook (VPN)
```
ID: 10848823
Datos ejemplo: ☐
Arquetipo: ARQ-4
Objetivo: "Convertir indecisos"
Enlaces: Configurados
Módulos: 1 ID añadido
```

### Test 3: Otros arquetipos
```
ARQ-5: Comparativa
ARQ-10: Por perfil
```

## Próximos Pasos

### Post V2.0
- [ ] Integrar más arquetipos (11-14)
- [ ] Sistema de caché para PDPs
- [ ] Historial de generaciones
- [ ] Exportar directo a CMS
- [ ] A/B testing de títulos
- [ ] Métricas de calidad automáticas

---

**Versión:** 2.0  
**Fecha:** 21 Noviembre 2025  
**Cambios:** 12 mejoras mayores  
**Breaking Changes:** 3  
**Nuevas Features:** 9
