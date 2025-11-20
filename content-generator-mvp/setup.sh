#!/bin/bash

# Script de setup rápido para Content Generator MVP

echo "🚀 Configurando Content Generator Black Friday..."
echo ""

# 1. Crear directorio .streamlit si no existe
echo "📁 Creando estructura de directorios..."
mkdir -p .streamlit

# 2. Copiar secrets example si no existe secrets.toml
if [ ! -f .streamlit/secrets.toml ]; then
    echo "📋 Creando archivo de secrets..."
    cp secrets.toml.example .streamlit/secrets.toml
    echo "⚠️  IMPORTANTE: Edita .streamlit/secrets.toml con tu ANTHROPIC_API_KEY"
    echo ""
else
    echo "✅ secrets.toml ya existe"
fi

# 3. Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt --break-system-packages --quiet

echo ""
echo "✅ Setup completado!"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Edita .streamlit/secrets.toml con tu API key de Anthropic"
echo "   2. Ejecuta: streamlit run app.py"
echo ""
echo "💡 Consigue tu API key en: https://console.anthropic.com/"
echo ""
