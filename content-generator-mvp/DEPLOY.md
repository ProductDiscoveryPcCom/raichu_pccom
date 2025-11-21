# 🚀 Desplegar en Streamlit Cloud

## Requisitos previos

- Cuenta en GitHub
- Cuenta en Streamlit Cloud (gratis)
- API Key de Anthropic

## Paso 1: Subir a GitHub

```bash
# 1. Crear repositorio en GitHub
# Ve a github.com → New repository
# Nombre: content-generator-bf
# Privado/Público según prefieras

# 2. Inicializar Git local
cd content-generator-mvp
git init
git add .
git commit -m "Initial commit - MVP funcional"

# 3. Conectar con GitHub
git remote add origin https://github.com/TU-USUARIO/content-generator-bf.git
git branch -M main
git push -u origin main
```

## Paso 2: Conectar con Streamlit Cloud

1. Ve a https://streamlit.io/cloud
2. "Sign up" o "Sign in" con GitHub
3. Click "New app"

### Configuración del deploy:

```
Repository: TU-USUARIO/content-generator-bf
Branch: main
Main file path: app.py
```

## Paso 3: Configurar Secrets

En la página de deploy, antes de lanzar:

1. Click en "Advanced settings"
2. En "Secrets", pega:

```toml
ANTHROPIC_API_KEY = "sk-ant-api03-tu-key-aqui"
```

3. Click "Deploy"

## Paso 4: ¡Listo!

- La app se desplegará automáticamente
- URL pública: `https://tu-usuario-content-generator-bf.streamlit.app`
- Actualizaciones: cada push a main redespliega automáticamente

## 🔧 Configuración opcional

### Custom subdomain

En Settings de tu app:
- "Custom subdomain" → `pccomponentes-bf-generator`
- URL final: `https://pccomponentes-bf-generator.streamlit.app`

### Variables adicionales (futuro)

Cuando integres n8n y Zenrows:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
N8N_ENDPOINT_URL = "https://..."
N8N_API_KEY = "..."
ZENROWS_API_KEY = "..."
```

## 📊 Monitoring

Streamlit Cloud incluye:
- Logs en tiempo real
- Uso de recursos
- Errores automáticos por email
- Analytics de uso

## 🔄 Actualizaciones

### Deploy automático:

```bash
# Haces cambios locales
git add .
git commit -m "Mejora X"
git push

# Streamlit Cloud detecta el push y redespliega automáticamente
```

### Rollback manual:

1. Ve a tu app en streamlit.io
2. Settings → Reboot
3. O redeploy desde commit anterior

## 🛡️ Seguridad

### Proteger secrets:

✅ NUNCA commits `secrets.toml` (está en .gitignore)  
✅ USA Streamlit Cloud secrets  
✅ Rota API keys si se exponen  
✅ Limita scope de API keys

### Hacer privada la app:

Streamlit Cloud gratis → Apps públicas  
Streamlit Cloud Teams → Apps privadas con SSO

## 💰 Costos

### Streamlit Cloud:
- Plan gratuito: 1 app pública, recursos limitados
- Plan Teams: $20/mes, apps privadas, más recursos

### Anthropic API:
- Pay-as-you-go
- ~$0.10 por generación (3 llamadas)
- Monitoriza uso en console.anthropic.com

## 🎯 Recomendaciones

### Para MVP:
- Plan gratuito de Streamlit OK
- Monitoriza costos API
- Limita acceso compartiendo URL solo internamente

### Para producción:
- Streamlit Cloud Teams (privacidad)
- Rate limiting en app
- Caché de generaciones
- Analytics propios

## 🐛 Troubleshooting

### App no arranca:
- Revisa logs en Streamlit Cloud
- Verifica secrets están configurados
- Chequea requirements.txt completo

### API key no funciona:
- Verifica formato en secrets (sin comillas extra)
- Confirma que tiene créditos
- Prueba regenerando la key

### Errores de módulos:
- Asegura versiones en requirements.txt
- Streamlit Cloud usa Python 3.9+

## 📞 Soporte

- Docs: https://docs.streamlit.io/streamlit-community-cloud
- Forum: https://discuss.streamlit.io
- Status: https://streamlit.io/status

---

**¡Tu app lista para el mundo!** 🌍
