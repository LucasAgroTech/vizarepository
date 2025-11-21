# 🛡️ Como Filtrar Tráfego Robótico no Google Analytics

## Problema
Você está vendo tráfego robótico da Alemanha (ou outros países) no Google Analytics que não são visitantes reais.

## Soluções

### 1. Filtro no Google Analytics (Recomendado)

1. Acesse: **Admin → Visualizações → Filtros**
2. Clique em **+ Novo Filtro**
3. Configure:
   - **Nome**: "Excluir Bots e Crawlers"
   - **Tipo**: Personalizado
   - **Excluir**
   - **Campo**: User Agent
   - **Padrão**: `bot|crawler|spider|scraper|headless|phantom|selenium|webdriver|curl|wget|python|java|php|ruby|perl|go-http|okhttp|httpie|postman|insomnia`

### 2. Filtro por IP (se souber o IP específico)

1. **Admin → Visualizações → Filtros**
2. **+ Novo Filtro**
3. Configure:
   - **Nome**: "Excluir IPs Alemanha"
   - **Tipo**: Excluir
   - **Campo**: IP do visitante
   - **Padrão**: `^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$` (ou IPs específicos)

### 3. Filtro por País (se for sempre da Alemanha)

1. **Admin → Visualizações → Filtros**
2. **+ Novo Filtro**
3. Configure:
   - **Nome**: "Excluir Tráfego Alemanha"
   - **Tipo**: Excluir
   - **Campo**: País
   - **Padrão**: `Germany`

### 4. Configurar no Código (Já implementado)

O código já foi atualizado para filtrar bots automaticamente. Para ativar:

1. Adicione sua chave do Google Analytics no `_config.yml`:
```yaml
google_analytics: G-XXXXXXXXXX  # Sua chave do GA4
```

2. Faça commit e push:
```bash
git add _config.yml _layouts/default.html
git commit -m "Adiciona filtro de bots no Google Analytics"
git push origin main
```

## Verificar Bots no GA

1. **Relatórios → Tempo Real → Usuários**
2. Veja o User Agent dos visitantes
3. Se aparecer algo como:
   - `bot`, `crawler`, `spider`
   - `python-requests`, `curl`, `wget`
   - `HeadlessChrome`, `PhantomJS`
   → São bots!

## Bots Comuns da Alemanha

- **AhrefsBot** (SEO tool)
- **SemrushBot** (SEO tool)
- **MJ12bot** (Crawler)
- **DotBot** (Crawler)
- **Bingbot** (às vezes aparece como Alemanha)

## Dica Extra

No Google Analytics 4, você pode criar uma **Visualização Filtrada** que exclui bots automaticamente, mantendo a visualização original intacta.

