#!/bin/bash

# Script para gerar posts, commitar e fazer push automaticamente

set -e  # Para em caso de erro

echo "🚀 Iniciando geração de posts e deploy..."

# Verificar se OPENAI_API_KEY está configurada
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERRO: OPENAI_API_KEY não está configurada"
    echo "   Configure com: export OPENAI_API_KEY='sua_chave'"
    exit 1
fi

# Verificar se estamos no diretório correto
if [ ! -f "sync_from_sitemap.py" ]; then
    echo "❌ ERRO: Execute este script no diretório do projeto"
    exit 1
fi

# 1. Gerar os posts
echo ""
echo "📝 Passo 1: Gerando posts..."
python3 sync_from_sitemap.py

# Verificar se novos posts foram gerados
NEW_POSTS=$(git status --porcelain _posts/ | grep "^??" | wc -l | tr -d ' ')

if [ "$NEW_POSTS" -eq "0" ]; then
    echo ""
    echo "ℹ️  Nenhum novo post foi gerado."
    echo "   (Todas as imagens já foram processadas ou não há novas imagens)"
    exit 0
fi

echo ""
echo "✅ $NEW_POSTS novo(s) post(s) gerado(s)"

# 2. Adicionar arquivos ao git
echo ""
echo "📦 Passo 2: Adicionando arquivos ao git..."
git add _posts/ data/processed_images.json

# 3. Verificar se há mudanças para commitar
if git diff --staged --quiet; then
    echo "ℹ️  Nenhuma mudança para commitar"
    exit 0
fi

# 4. Fazer commit
echo ""
echo "💾 Passo 3: Fazendo commit..."
COMMIT_MSG="Auto: Adiciona novos posts gerados automaticamente ($(date +'%Y-%m-%d %H:%M:%S'))"
git commit -m "$COMMIT_MSG"

# 5. Fazer push
echo ""
echo "☁️  Passo 4: Fazendo push para o GitHub..."
git push origin main

echo ""
echo "✅ Deploy concluído com sucesso!"
echo ""
echo "📊 Resumo:"
echo "   - Posts gerados: $NEW_POSTS"
echo "   - Commit: $COMMIT_MSG"
echo "   - Push: ✅ Enviado para origin/main"
echo ""
echo "⏳ Aguarde 2-3 minutos para o GitHub Pages fazer o deploy"
echo "   URL: https://lucasagrotech.github.io/vizarepository/"

