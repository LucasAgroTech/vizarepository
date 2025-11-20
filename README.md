# SEO GitHub - Sincronização Automática de Sitemap

Sistema automatizado que transforma imagens do sitemap do VizaRepo em posts de blog otimizados para SEO, usando IA para gerar conteúdo completo.

## 🎯 O que faz

1. **Puxa automaticamente** os links do sitemap de imagens do VizaRepo
2. **Extrai dados** (URL da página, URL da imagem, título/caption)
3. **Envia para IA** gerar SEO + artigo completo
4. **Gera o post Markdown** no repositório do blog
5. **Evita duplicados** + roda em lote (local ou GitHub Actions)

## 📋 Pré-requisitos

- Python 3.11+
- Chave de API da OpenAI
- Repositório Git configurado

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone <seu-repo>
cd seo-github
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure a chave da OpenAI:
```bash
export OPENAI_API_KEY="sua_chave_aqui"
```

## 💻 Uso Local

Execute o script manualmente:

```bash
python sync_from_sitemap.py
```

O script vai:
- Baixar o sitemap do VizaRepo
- Identificar imagens novas (não processadas)
- Gerar até `MAX_PER_RUN` posts (padrão: 3)
- Salvar os posts em `_posts/`
- Registrar URLs processadas em `data/processed_images.json`

## 🤖 Automação com GitHub Actions

O workflow está configurado para rodar automaticamente:

- **Cron diário**: 03:00 UTC (ajuste no arquivo `.github/workflows/sync-sitemap.yml`)
- **Manual**: Vá em Actions → Sync sitemap VizaRepo → Run workflow

### Configuração

1. Vá em **Settings → Secrets and variables → Actions**
2. Clique em **New repository secret**
3. Adicione:
   - **Name**: `OPENAI_API_KEY`
   - **Value**: sua chave da OpenAI

Pronto! O workflow vai rodar automaticamente e fazer commit dos novos posts.

## 📁 Estrutura do Projeto

```
seo-github/
├── sync_from_sitemap.py      # Script principal
├── requirements.txt           # Dependências Python
├── _posts/                   # Posts gerados (Markdown)
├── data/
│   └── processed_images.json # URLs já processadas
├── .github/
│   └── workflows/
│       └── sync-sitemap.yml  # Workflow GitHub Actions
└── README.md
```

## ⚙️ Configurações

No arquivo `sync_from_sitemap.py`, você pode ajustar:

- `SITEMAP_URL`: URL do sitemap de imagens
- `MAX_PER_RUN`: Quantidade máxima de posts por execução
- `POSTS_DIR`: Diretório onde os posts são salvos
- `PROCESSED_FILE`: Arquivo que armazena URLs processadas

## 📝 Formato dos Posts

Cada post gerado inclui:

- **Front Matter** completo com:
  - SEO (title, meta_description, slug)
  - Open Graph (og_title, og_description, og_image)
  - Schema.org JSON-LD
  - Tags e categoria
  - Canonical URL

- **Conteúdo Markdown** com:
  - Imagem embedada no topo
  - Estrutura H1, H2, H3
  - Contexto de uso da imagem
  - CTA para a página do VizaRepo

## 🔧 Troubleshooting

### Erro: "OPENAI_API_KEY não encontrada"
Certifique-se de exportar a variável de ambiente ou configurar no GitHub Secrets.

### Erro: "Nenhuma nova imagem encontrada"
Todas as imagens do sitemap já foram processadas. Aguarde novas imagens ou limpe `data/processed_images.json`.

### Posts duplicados
O sistema evita duplicados usando `processed_images.json`. Se precisar reprocessar, remova a URL específica desse arquivo.

## 📊 Monitoramento

O script imprime logs durante a execução:
- `[OK] Post criado: _posts/YYYY-MM-DD-slug.md`
- `[ERRO] Ao processar <url>: <erro>`

No GitHub Actions, veja os logs em **Actions → Sync sitemap VizaRepo**.

## 🎨 Personalização

### Ajustar o prompt da IA

Edite a função `gerar_conteudo_e_seo()` em `sync_from_sitemap.py` para modificar o prompt e o tipo de conteúdo gerado.

### Diferentes clusters/temas

Você pode adicionar lógica para detectar padrões nas URLs e ajustar o prompt por categoria (fitness, café, lifestyle, etc.).

### Linkagem interna

Adicione lógica para sugerir posts relacionados baseado em tags ou categorias similares.

## 📄 Licença

Este projeto é livre para uso e modificação.

