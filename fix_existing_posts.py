#!/usr/bin/env python3
"""
Script para corrigir URLs de imagens nos posts existentes.
Extrai a URL real da imagem da página do VizaRepo e atualiza o post.
"""

import os
import re
import json
import requests
from pathlib import Path

POSTS_DIR = "_posts"


def extrair_url_real_imagem(page_url):
    """Extrai a URL real da imagem da página do VizaRepo."""
    try:
        resp = requests.get(page_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        resp.raise_for_status()
        html = resp.text
        
        # Tenta pegar do srcSet (com S maiúsculo, formato React/Next.js)
        srcset_patterns = [
            r'srcSet\s*=\s*["\']([^"\']+)["\']',
            r'srcset\s*=\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in srcset_patterns:
            srcset_match = re.search(pattern, html, re.IGNORECASE)
            if srcset_match:
                srcset = srcset_match.group(1)
                urls = [url.strip().split()[0] for url in srcset.split(',') if url.strip()]
                if urls:
                    # Prefere .avif ou .webp se disponível
                    for url in urls:
                        if '.avif' in url or '.webp' in url:
                            return url
                    return urls[0]
        
        # Fallback: procura URLs CloudFront
        cloudfront_pattern = r'https://[^"\'>\s]*cloudfront[^"\'>\s]*\.(avif|webp|png|jpg)'
        cloudfront_match = re.search(cloudfront_pattern, html, re.IGNORECASE)
        if cloudfront_match:
            return cloudfront_match.group(0)
            
    except Exception as e:
        print(f"[ERRO] Ao extrair URL de {page_url}: {e}")
    
    return None


def extrair_page_url_do_post(content):
    """Extrai a URL da página do VizaRepo do schema_org ou do conteúdo."""
    # Tenta do schema_org primeiro
    schema_match = re.search(r'"mainEntityOfPage"\s*:\s*"([^"]+)"', content)
    if schema_match:
        return schema_match.group(1)
    
    # Tenta do link no conteúdo
    link_match = re.search(r'https://www\.vizarepo\.com/i/[^\s\)]+', content)
    if link_match:
        return link_match.group(0)
    
    return None


def atualizar_post(filepath):
    """Atualiza um post com a URL correta da imagem."""
    print(f"\nProcessando: {filepath.name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extrai a URL da página
    page_url = extrair_page_url_do_post(content)
    if not page_url:
        print(f"  ⚠️  Não foi possível encontrar a URL da página")
        return False
    
    print(f"  📄 URL da página: {page_url}")
    
    # Extrai a URL real da imagem
    real_image_url = extrair_url_real_imagem(page_url)
    if not real_image_url:
        print(f"  ⚠️  Não foi possível extrair a URL real da imagem")
        return False
    
    print(f"  ✅ URL real da imagem: {real_image_url}")
    
    # Atualiza og_image no front matter
    old_og_pattern = r'(og_image:\s*")([^"]+)(")'
    if re.search(old_og_pattern, content):
        content = re.sub(old_og_pattern, rf'\1{real_image_url}\3', content)
        print(f"  ✅ Atualizado og_image")
    
    # Atualiza a imagem no schema_org
    old_schema_img_pattern = r'("image"\s*:\s*")([^"]+)(")'
    if re.search(old_schema_img_pattern, content):
        content = re.sub(old_schema_img_pattern, rf'\1{real_image_url}\3', content)
        print(f"  ✅ Atualizado schema_org image")
    
    # Atualiza a imagem no markdown (primeira ocorrência de ![alt](url))
    old_md_img_pattern = r'(!\[[^\]]+\]\()([^\)]+)(\))'
    md_matches = list(re.finditer(old_md_img_pattern, content))
    if md_matches:
        # Pega a primeira imagem no conteúdo (depois do front matter)
        for match in md_matches:
            if match.start() > content.find('---', content.find('---') + 1):
                old_url = match.group(2)
                if 'cloudfront' in old_url:
                    content = content[:match.start()] + match.group(1) + real_image_url + match.group(3) + content[match.end():]
                    print(f"  ✅ Atualizado markdown image")
                    break
    
    # Salva o arquivo atualizado
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ Post atualizado com sucesso!")
    return True


def main():
    """Função principal."""
    posts_dir = Path(POSTS_DIR)
    if not posts_dir.exists():
        print(f"❌ Diretório {POSTS_DIR} não encontrado")
        return
    
    posts = list(posts_dir.glob("*.md"))
    if not posts:
        print(f"❌ Nenhum post encontrado em {POSTS_DIR}")
        return
    
    print(f"📝 Encontrados {len(posts)} posts para processar")
    
    sucesso = 0
    for post_file in posts:
        if atualizar_post(post_file):
            sucesso += 1
    
    print(f"\n✅ Processo concluído: {sucesso}/{len(posts)} posts atualizados")


if __name__ == "__main__":
    main()

