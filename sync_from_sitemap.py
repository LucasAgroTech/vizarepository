import os
import json
import requests
import re
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


def extrair_url_real_imagem(page_url):
    """
    Extrai a URL real da imagem da página do VizaRepo.
    Tenta pegar do srcset ou da tag img principal.
    """
    try:
        resp = requests.get(page_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        resp.raise_for_status()
        html = resp.text
        
        # Tenta pegar do srcSet (com S maiúsculo, formato React/Next.js)
        # Procura por srcSet="..." ou srcset="..."
        srcset_patterns = [
            r'srcSet\s*=\s*["\']([^"\']+)["\']',
            r'srcset\s*=\s*["\']([^"\']+)["\']',
            r'srcset\s*=\s*([^\s>]+)',
        ]
        
        for pattern in srcset_patterns:
            srcset_match = re.search(pattern, html, re.IGNORECASE)
            if srcset_match:
                srcset = srcset_match.group(1)
                # Pega a primeira URL do srcset (geralmente a maior/resolução mais alta)
                urls = [url.strip().split()[0] for url in srcset.split(',') if url.strip()]
                if urls:
                    # Prefere .avif ou .webp se disponível
                    for url in urls:
                        if '.avif' in url or '.webp' in url:
                            return url
                    return urls[0]
        
        # Tenta pegar URLs diretas de imagens CloudFront com formato moderno
        cloudfront_pattern = r'https://[^"\'>\s]*cloudfront[^"\'>\s]*\.(avif|webp)'
        cloudfront_match = re.search(cloudfront_pattern, html, re.IGNORECASE)
        if cloudfront_match:
            return cloudfront_match.group(0)
        
        # Tenta pegar da tag img com src
        img_patterns = [
            r'<img[^>]*src\s*=\s*["\'](https://[^"\']*cloudfront[^"\']*\.(avif|webp|jpg|jpeg|png))["\']',
            r'<img[^>]*src\s*=\s*["\'](https://[^"\']*cloudfront[^"\']+)["\']',
        ]
        
        for pattern in img_patterns:
            img_match = re.search(pattern, html, re.IGNORECASE)
            if img_match:
                return img_match.group(1)
            
    except Exception as e:
        print(f"[AVISO] Não foi possível extrair URL real de {page_url}: {e}")
    
    return None


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


def gerar_conteudo_e_seo(item, idioma="en-US"):
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
    
    # Extrai a URL real da imagem apenas quando for gerar o post (otimização)
    print(f"[INFO] Extraindo URL real da imagem de: {page_url}")
    real_image_url = extrair_url_real_imagem(page_url)
    if real_image_url:
        image_url = real_image_url
        print(f"[INFO] ✅ URL real extraída: {image_url}")
    else:
        print(f"[AVISO] Usando URL do sitemap: {image_url}")

    prompt = f"""
You are an expert in SEO, blogging, and copywriting.

You will receive data from a premium image repository:

- Image page URL (landing): {page_url}
- Image URL: {image_url}
- Image title: "{image_title}"
- Image caption/description: "{image_caption}"

Task:

1. Choose a content ANGLE for a blog post that makes sense for this image
   (e.g., lifestyle, photography, branding, visual inspiration, design, marketing, etc.).

2. Create a COMPLETE article in English, designed to rank well in search engines and generate clicks.

The article must:

- Be in Markdown format.
- Have well-structured H1, H2, H3 headings.
- Provide context on how to use the image (how to use in campaigns, posts, websites, or what type of audience it attracts).
- Have a subtle CTA pointing to the image page at {page_url} for download/licensing.
- DO NOT include the image in the Markdown content - the image will be displayed automatically at the top of the post.
- Start directly with the H1 title and content.

In addition to the article, generate a JSON with the following fields:

- seo_title: up to 60 characters, focused on CTR.
- meta_description: up to 155 characters, persuasive.
- slug: short, in kebab-case (can be based on the article theme, not just the image title).
- og_title
- og_description
- og_image: use {image_url}
- canonical_url: use the post URL that will be /blog/<slug>/ (only the path, I'll complete it later).
- tags: list of 3-7 relevant tags (in English).
- category: a main category (e.g., "Photography", "Visual Inspiration", "Digital Marketing", etc.)
- schema_org: BlogPosting JSON-LD as STRING, valid for rich snippets.
  Use {page_url} as mainEntityOfPage to reference the original image as well.

Respond EXACTLY in this format:

<SEO_JSON>
{{ ...json here... }}
</SEO_JSON>

<ARTICLE_MD>
# H1 Title

...
</ARTICLE_MD>
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in SEO and blog content creation. Always generate content in English."},
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

    # Escapar aspas duplas para evitar problemas no YAML
    seo_title_escaped = (seo.get('seo_title', '') or '').replace('"', '\\"')
    meta_desc_escaped = (seo.get('meta_description', '') or '').replace('"', '\\"')
    category_escaped = (seo.get('category', '') or '').replace('"', '\\"')
    og_title_escaped = (seo.get('og_title', '') or '').replace('"', '\\"')
    og_desc_escaped = (seo.get('og_description', '') or '').replace('"', '\\"')
    og_image_url = seo.get('og_image', '') or ''

    front_matter = f"""---
layout: post
title: "{seo_title_escaped}"
seo_title: "{seo_title_escaped}"
date: {hoje}
lang: "en-US"

slug: "{slug}"
meta_description: "{meta_desc_escaped}"
tags:
"""

    for tag in seo.get("tags", []):
        escaped_tag = tag.replace('"', '\\"')
        front_matter += f'  - "{escaped_tag}"\n'

    front_matter += f"""category: "{category_escaped}"

og_title: "{og_title_escaped}"
og_description: "{og_desc_escaped}"
og_image: "{og_image_url}"

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

