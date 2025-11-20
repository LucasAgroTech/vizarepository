# 🌐 Como Ver o Blog no GitHub Pages

## Passo 1: Habilitar GitHub Pages

1. Acesse: https://github.com/LucasAgroTech/vizarepository/settings/pages
2. Em **Source**, selecione:
   - **Branch**: `main`
   - **Folder**: `/ (root)`
3. Clique em **Save**

## Passo 2: Aguardar Deploy

O GitHub Pages leva alguns minutos para fazer o primeiro deploy. Você verá uma mensagem verde quando estiver pronto.

## Passo 3: Acessar o Blog

Após o deploy, seu blog estará disponível em:

**https://lucasagrotech.github.io/vizarepository/**

Ou, se você configurou um domínio customizado, use seu domínio.

## 📝 Verificar Status

Você pode verificar o status do deploy em:
- **Actions** tab: https://github.com/LucasAgroTech/vizarepository/actions
- **Settings → Pages**: https://github.com/LucasAgroTech/vizarepository/settings/pages

## 🔧 Troubleshooting

### Blog não aparece
- Aguarde 5-10 minutos após habilitar
- Verifique se há erros em **Actions**
- Certifique-se de que o branch `main` está selecionado

### Posts não aparecem
- Verifique se os arquivos estão em `_posts/` com formato `YYYY-MM-DD-slug.md`
- Verifique se o front matter está correto (layout: post)

### Erro de build
- Verifique os logs em **Actions**
- Certifique-se de que `_config.yml` está correto

## 🚀 Testar Localmente (Opcional)

Se quiser testar localmente antes de fazer push:

```bash
# Instalar Jekyll
gem install bundler jekyll

# Rodar servidor local
bundle exec jekyll serve

# Acessar: http://localhost:4000/vizarepository/
```

