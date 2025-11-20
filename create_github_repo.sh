#!/bin/bash

# Script para criar o repositório no GitHub e fazer push

REPO_NAME="vizarepository"
GITHUB_USER=$(git config user.name 2>/dev/null || echo "")

if [ -z "$GITHUB_USER" ]; then
    echo "❌ Não foi possível detectar seu usuário do GitHub"
    echo "   Configure com: git config --global user.name 'seu-usuario'"
    exit 1
fi

echo "🔗 Configurando repositório remoto: $REPO_NAME"
echo ""
echo "Opção 1: Criar via GitHub CLI (gh)"
if command -v gh &> /dev/null; then
    echo "   Executando: gh repo create $REPO_NAME --public --source=. --remote=origin --push"
    read -p "   Criar repositório agora? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        gh repo create $REPO_NAME --public --source=. --remote=origin --push
        exit 0
    fi
fi

echo ""
echo "Opção 2: Criar manualmente no GitHub"
echo "   1. Acesse: https://github.com/new"
echo "   2. Nome do repositório: $REPO_NAME"
echo "   3. Deixe vazio (não inicialize com README)"
echo "   4. Clique em 'Create repository'"
echo ""
echo "   Depois execute:"
echo "   git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git"
echo "   git push -u origin main"
echo ""

