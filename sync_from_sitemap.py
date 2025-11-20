import os
import json
import requests
from datetime import date
from slugify import slugify
from xml.etree import ElementTree as ET
from openai import OpenAI

SITEMAP_URL = "https://www.vizarepo.com/sitemap-images.xml"
POSTS_DIR = "_posts"
PROCESSED_FILE = "data/processed_images.json"
MAX_PER_RUN = 3  # para não estourar tokens / custo em um único run

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_processed():
    """Carrega a lista de URLs já processadas."""
    if not os.path.exists(PROCESSED_FILE):
        os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
        return set()
    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_processed(processed_set):
    """Salva a lista de URLs processadas."""
    os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(processed_set)), f, ensure_ascii=False, indent=2)


def fetch_sitemap(url=SITEMAP_URL):
    """Baixa o sitemap XML do VizaRepo."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_image_sitemap(xml_text):
    """
    Retorna lista de dicts:
    {
      'page_url': ...,
      'image_url': ...,
      'image_title': ...,
      'image_caption': ...
    }
    """
    ns = {
        "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "image": "http://www.google.com/schemas/sitemap-image/1.1",
    }
    root = ET.fromstring(xml_text)
    items = []

    for url in root.findall("sm:url", ns):
        page_url_el = url.find("sm:loc", ns)
        if page_url_el is None:
            continue
        page_url = page_url_el.text.strip()

        img_el = url.find("image:image", ns)
        if img_el is None:
            continue

        img_url_el = img_el.find("image:loc", ns)
        title_el = img_el.find("image:title", ns)
        caption_el = img_el.find("image:caption", ns)

        image_url = img_url_el.text.strip() if img_url_el is not None else None
        image_title = title_el.text.strip() if title_el is not None else ""
        image_caption = caption_el.text.strip() if caption_el is not None else ""

        items.append(
            {
                "page_url": page_url,
                "image_url": image_url,
                "image_title": image_title,
                "image_caption": image_caption,
            }
        )
    return items


def gerar_conteudo_e_seo(item, idioma="pt-BR"):
    """
    Usa IA para gerar:
    - JSON de SEO
    - Artigo em Markdown
    baseada na imagem do VizaRepo
    """
    page_url = item["page_url"]
    image_url = item["image_url"]
    image_title = item["image_title"]
    image_caption = item["image_caption"]

    prompt = f"""
Você é um especialista em SEO, blog e copy.

Você vai receber os dados de uma imagem de um repositório de imagens premium:

- URL da página da imagem (landing): {page_url}
- URL da imagem: {image_url}
- Título da imagem: "{image_title}"
- Caption/descrição da imagem: "{image_caption}"

Tarefa:

1. Escolher um ANGLE de conteúdo para blog que faça sentido para essa imagem
   (ex: lifestyle, fotografia, branding, inspiração visual, design, marketing, etc.).

2. Criar um artigo COMPLETO em {idioma}, pensado para rankear bem em mecanismos de busca e gerar clique.

O artigo deve:

- Ser em Markdown.
- Ter H1, H2, H3 bem estruturados.
- Trazer contexto de uso da imagem (como usar em campanhas, posts, sites, ou que tipo de público ela atrai).
- Ter CTA suave apontando para a página da imagem em {page_url} para download/licenciamento.
- Incluir a imagem em Markdown no topo: ![ALT OTIMIZADO]({image_url})
  onde o ALT deve ser descritivo e natural.

Além do artigo, gere um JSON com os seguintes campos:

- seo_title: até 60 caracteres, com foco em CTR.
- meta_description: até 155 caracteres, persuasiva.
- slug: curto, em kebab-case (pode ser com base no tema do artigo, não apenas no título da imagem).
- og_title
- og_description
- og_image: use {image_url}
- canonical_url: use a própria URL do post que será /blog/<slug>/ (apenas o path, que depois eu completo).
- tags: lista de 3-7 tags relevantes.
- category: uma categoria principal (ex: "Fotografia", "Inspiração Visual", "Marketing Digital" etc.)
- schema_org: JSON-LD de BlogPosting como STRING, válido para rich snippets.
  Use {page_url} como mainEntityOfPage para referenciar a imagem original também.

Responda EXATAMENTE no formato:

<SEO_JSON>
{{ ...json aqui... }}
</SEO_JSON>

<ARTICLE_MD>
# Título H1

...
</ARTICLE_MD>
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um especialista em SEO e criação de conteúdo para blogs."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    text = response.choices[0].message.content

    # Extrair JSON e Markdown da resposta
    seo_part = text.split("<SEO_JSON>")[1].split("</SEO_JSON>")[0].strip()
    article_md = text.split("<ARTICLE_MD>")[1].split("</ARTICLE_MD>")[0].strip()

    import json as _json
    seo = _json.loads(seo_part)
    return seo, article_md


def salvar_post(seo, article_md):
    """Salva o post em formato Markdown com front matter."""
    hoje = date.today().isoformat()
    raw_slug = seo.get("slug") or seo.get("seo_title") or "post"
    slug = slugify(raw_slug)
    filename = f"{hoje}-{slug}.md"
    path = os.path.join(POSTS_DIR, filename)

    os.makedirs(POSTS_DIR, exist_ok=True)

    # Se quiser prefixar a canonical com domínio depois, dá pra fazer via layout.
    canonical_path = seo.get("canonical_url") or f"/blog/{slug}/"

    # Evitar quebras de linha malucas no schema_org
    schema_org = (seo.get("schema_org") or "").replace("\n", " ")

    front_matter = f"""---
layout: default
title: "{seo.get('seo_title', '').replace('"', '\\"')}"
seo_title: "{seo.get('seo_title', '').replace('"', '\\"')}"
date: {hoje}
lang: "pt-BR"

slug: "{slug}"
meta_description: "{seo.get('meta_description', '').replace('"', '\\"')}"
tags:
"""

    for tag in seo.get("tags", []):
        front_matter += f'  - "{tag.replace(\'"\', \'\\"\')}"\n'

    front_matter += f"""category: "{seo.get('category', '').replace('"', '\\"')}"

og_title: "{seo.get('og_title', '').replace('"', '\\"')}"
og_description: "{seo.get('og_description', '').replace('"', '\\"')}"
og_image: "{seo.get('og_image', '')}"

canonical_url: "{canonical_path}"

schema_org: >
  {schema_org}
---

"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(front_matter)
        f.write("\n")
        f.write(article_md)

    print(f"[OK] Post criado: {path}")


def main():
    """Função principal que orquestra todo o processo."""
    processed = load_processed()
    xml_text = fetch_sitemap()
    items = parse_image_sitemap(xml_text)

    novos = [it for it in items if it["page_url"] not in processed]
    if not novos:
        print("Nenhuma nova imagem encontrada no sitemap.")
        return

    print(f"Novas imagens encontradas: {len(novos)}")

    count = 0
    for item in novos:
        if count >= MAX_PER_RUN:
            break

        try:
            print(f"Processando: {item['page_url']}")
            seo, md = gerar_conteudo_e_seo(item)
            salvar_post(seo, md)
            processed.add(item["page_url"])
            count += 1
        except Exception as e:
            print(f"[ERRO] Ao processar {item['page_url']}: {e}")
            import traceback
            traceback.print_exc()

    save_processed(processed)
    print(f"Processo concluído. {count} posts gerados.")


if __name__ == "__main__":
    main()

