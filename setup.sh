#!/bin/bash

# Script de setup inicial para o projeto SEO GitHub

echo "🚀 Configurando o projeto SEO GitHub..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.11+"
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Por favor, instale pip"
    exit 1
fi

# Instalar dependências
echo "📦 Instalando dependências Python..."
pip3 install -r requirements.txt

# Verificar se OPENAI_API_KEY está configurada
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY não está configurada como variável de ambiente"
    echo "   Configure com: export OPENAI_API_KEY='sua_chave_aqui'"
    echo "   Ou adicione ao seu ~/.zshrc ou ~/.bashrc"
fi

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p _posts data

echo "✅ Setup concluído!"
echo ""
echo "Para rodar o script:"
echo "  python3 sync_from_sitemap.py"
echo ""

