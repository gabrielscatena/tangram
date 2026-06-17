#!/usr/bin/env python3
"""Download original source PDFs used by Tangram AI Feedback Lab.

This script downloads public source PDFs and verifies SHA256 hashes.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import urllib.request

ROOT = Path(__file__).resolve().parent
SOURCES = [
    {
        'url': 'https://basenacionalcomum.mec.gov.br/images/BNCC_20dez_site.pdf',
        'path': 'data/raw/bncc/BNCC_20dez_site.pdf',
        'sha256': '7d0004aacde591d4d898cbdf950ab7ed28e875f837dab12bb88cb15567cdf180',
    },
    {
        'url': 'https://basenacionalcomum.mec.gov.br/images/implementacao/cadernos_tematicos/caderno_economia_consolidado_v_final_09_03_2022.pdf',
        'path': 'data/raw/mec_tct/caderno_economia_consolidado_v_final_09_03_2022.pdf',
        'sha256': '3814d34580849e0a47f6b17d92604ef6b54ad20cc342dd6b09f0552dc72123a1',
    },
    {
        'url': 'https://basenacionalcomum.mec.gov.br/images/implementacao/contextualizacao_temas_contemporaneos.pdf',
        'path': 'data/raw/mec_tct/contextualizacao_temas_contemporaneos.pdf',
        'sha256': 'd9cdd4ccd4c14cae24d8ff6fd75ee724ec2406faaa1305b7e1a95fb75533dc41',
    },
    {
        'url': 'https://basenacionalcomum.mec.gov.br/images/implementacao/guia_pratico_temas_contemporaneos.pdf',
        'path': 'data/raw/mec_tct/guia_pratico_temas_contemporaneos.pdf',
        'sha256': '2c156e39a550d73de7bb89c76232daa10c7f1dfeb7727a379c96867a9fcf3a37',
    },
    {
        'url': 'https://aprendervalor.bcb.gov.br/content/cidadaniafinanceira/documentos_cidadania/Matriz%20Geral.pdf',
        'path': 'data/raw/bcb/Matriz_Geral_Letramento_Financeiro.pdf',
        'sha256': 'bb302457fe03c9d5b6282d37ea17ba881fb53c85ddf55282649c58189db18a2e',
    },
    {
        'url': 'https://www.bcb.gov.br/nor/relcidfin/docs/art8_educacao_finanaceira_escolas.pdf',
        'path': 'data/raw/bcb/art8_educacao_financeira_escolas.pdf',
        'sha256': '5360e49ca367a01d758081a316fa183d0b6667e3a25b1a4e58194ba32e039145',
    },
]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main() -> None:
    for source in SOURCES:
        out_path = ROOT / source['path']
        out_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {source['url']} -> {out_path}")
        urllib.request.urlretrieve(source['url'], out_path)
        digest = sha256_file(out_path)
        if digest != source['sha256']:
            raise RuntimeError(f"SHA256 mismatch for {out_path}: {digest} != {source['sha256']}")
        print(f"OK: {out_path.name}")

if __name__ == '__main__':
    main()
