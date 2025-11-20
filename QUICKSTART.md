# 🚀 Guia Rápido - Começar a Publicar

## 1. Configuração Inicial (Primeira Vez)

```bash
# Instalar dependências
./setup.sh

# OU manualmente:
pip3 install -r requirements.txt
```

## 2. Configurar Chave da OpenAI

```bash
export OPENAI_API_KEY="sk-sua-chave-aqui"
```

**Importante**: Adicione isso ao seu `~/.zshrc` para não perder:
```bash
echo 'export OPENAI_API_KEY="sk-sua-chave-aqui"' >> ~/.zshrc
source ~/.zshrc
```

## 3. Rodar o Script

```bash
python3 sync_from_sitemap.py
```

O script vai:
- ✅ Baixar o sitemap do VizaRepo
- ✅ Identificar imagens novas
- ✅ Gerar até 3 posts (configurável em `MAX_PER_RUN`)
- ✅ Salvar em `_posts/`
- ✅ Registrar URLs processadas em `data/processed_images.json`

## 4. Verificar os Posts Gerados

```bash
ls -la _posts/
```

Cada post terá o formato: `YYYY-MM-DD-slug.md`

## 5. Criar Repositório no GitHub

### Opção A: Via GitHub CLI (recomendado)

```bash
gh repo create vizarepository --public --source=. --remote=origin --push
```

### Opção B: Manual

1. Acesse: https://github.com/new
2. Nome: `vizarepository`
3. **NÃO** marque "Initialize with README"
4. Clique em "Create repository"
5. Execute:

```bash
git remote add origin https://github.com/SEU-USUARIO/vizarepository.git
git push -u origin main
```

## 6. Configurar GitHub Actions (Opcional)

1. Vá em **Settings → Secrets and variables → Actions**
2. Clique em **New repository secret**
3. Adicione:
   - **Name**: `OPENAI_API_KEY`
   - **Value**: sua chave da OpenAI

Pronto! O workflow vai rodar automaticamente todo dia às 03:00 UTC.

## 🔧 Ajustes Rápidos

### Mudar quantidade de posts por execução

Edite `sync_from_sitemap.py`:
```python
MAX_PER_RUN = 5  # ao invés de 3
```

### Reprocessar uma imagem específica

Edite `data/processed_images.json` e remova a URL que quer reprocessar.

### Ver logs detalhados

O script já mostra logs. Para mais detalhes, os erros aparecem com traceback completo.

## ❓ Problemas Comuns

**Erro: "OPENAI_API_KEY não encontrada"**
- Verifique se exportou: `echo $OPENAI_API_KEY`
- Se não aparecer nada, exporte novamente

**Erro: "Nenhuma nova imagem encontrada"**
- Todas as imagens já foram processadas
- Aguarde novas imagens no sitemap ou limpe `data/processed_images.json`

**Erro ao instalar dependências**
- Use `pip3` ao invés de `pip`
- Ou crie um ambiente virtual: `python3 -m venv venv && source venv/bin/activate`

