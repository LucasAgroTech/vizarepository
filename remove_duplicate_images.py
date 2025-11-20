#!/usr/bin/env python3
"""
Remove imagens duplicadas do markdown dos posts.
A imagem já aparece no layout destacado, então não precisa no markdown.
"""

import re
from pathlib import Path

POSTS_DIR = "_posts"


def remover_imagem_duplicada(filepath):
    """Remove a primeira imagem do markdown (já aparece no layout)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontra o final do front matter
    front_matter_end = content.find('---', content.find('---') + 1)
    if front_matter_end == -1:
        return False
    
    # Pega o conteúdo após o front matter
    markdown_content = content[front_matter_end + 3:]
    
    # Procura pela primeira imagem markdown (![alt](url))
    img_pattern = r'!\[[^\]]+\]\([^\)]+\)\s*\n'
    match = re.search(img_pattern, markdown_content)
    
    if match:
        # Remove a imagem e linhas em branco seguintes
        start = match.start()
        end = match.end()
        # Remove linhas em branco extras após a imagem
        while end < len(markdown_content) and markdown_content[end:end+1] in ['\n', ' ']:
            end += 1
        
        new_markdown = markdown_content[:start] + markdown_content[end:]
        new_content = content[:front_matter_end + 3] + new_markdown
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    
    return False


def main():
    posts_dir = Path(POSTS_DIR)
    posts = list(posts_dir.glob("*.md"))
    
    print(f"📝 Processando {len(posts)} posts...")
    
    for post_file in posts:
        if remover_imagem_duplicada(post_file):
            print(f"  ✅ {post_file.name} - imagem duplicada removida")
        else:
            print(f"  ⏭️  {post_file.name} - sem imagem duplicada")


if __name__ == "__main__":
    main()

