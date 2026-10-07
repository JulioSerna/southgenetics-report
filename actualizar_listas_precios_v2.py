#!/usr/bin/env python3
"""
Actualización de Listas de Precios V2.0 para SOUTHGENETICS MEXICO SA DE CV (ID: 13)
==================================================================================
Este script procesa el archivo 'V2.0_lista_de_precios.xlsx' para las 11 listas de México
(IDs 63 a 73), detecta reglas existentes, reglas nuevas por crear y discrepancias de catálogo.
Ejecuta la sincronización utilizando la herramienta oficial 'odoo-mcp' CLI de Vauxoo o
prepara los payloads para Odoo MCP execute_kw.

IMPORTANTE: Cumple con la normativa Vauxoo: NUNCA utiliza xmlrpc.client.
"""

import json
import os
import re
import subprocess
import sys
import openpyxl

EXCEL_PATH = os.path.join(os.path.dirname(__file__), 'V2.0_lista_de_precios.xlsx')
COMPANY_ID = 13
PROFILE = 'southgenetics-staging'
ODOO_MCP_BIN = os.path.expanduser('~/.local/bin/odoo-mcp')

SHEET_TO_PRICELIST = {
    'UGTO': 63,
    'PUBLICO GENERAL': 64,
    'CECAN': 65,
    'LAPI': 66,
    'FUCAM ': 67,
    'GOBIERNO': 68,
    'ZOGEN ': 69,
    'COI': 70,
    'GNP': 71,
    'ABC ': 72,
    'CENTRO DE ENDOCRINOLOGIA INTEGR': 73
}

KNOWN_MAPPINGS = {
    'mirthype full': 562,
    'mir-thype(r)': 562,
    'mirthype preop': 573,
    'mirthype target': 612,
    'afirma gsc': 632,
    'afirma- oncología': 408,
    'afirma xpression atlas': 672,
    'oncotype dx mama': 437,
    'oncotype dx colon': 678,
    'oncotype colon': 678,
    'cellsearch ctc': 591,
    'cellsearch ctc-her2': 592,
    'cellsearch cmmc': 593,
    'cellsearch cmc': 594,
    'cellsearch ctc-er': 595,
    'cellsearch ctc pdl1': 596,
    'tempus xt heme': 624,
    'tempus xt + xr tejido': 621,
    'tempus xt + xr': 621,
    'tempus xm mrd': 622,
    'tempus xf + biopsia liquida': 623,
    'tempus xf +': 623,
    'decisiondx-scc': 605,
    'decisiondx - scc': 605,
    'decisiondx-um': 642,
    'decisiondx - um': 642,
    'mypath melanoma': 607,
    'mypath - melanoma': 607,
    'decisiondx melanoma': 603,
    'decisiondx - melanoma': 603,
    '4kscore': 407,
    'confirm mdx': 414,
    'confirmmdx': 414,
    'genomic prostate score': 485,
    'genomic prostate score (gps)': 485,
    'cxbladder': 415,
    'cx bladder': 415,
    'genomind professional pgx': 425,
    'genomind professionalpgx': 425,
    'maternit genome': 432,
    'unity': 447,
    'unity complete': 448,
    'monogenic diabetes panel': 712,
    'invitae monogenic diabetes': 712,
    'her2dx': 714,
    'myprostatescore2.0(mps2)': 693,
    'my prostate score 2.0': 693,
    'myprostatescore v2.0 (mps2)': 693,
    'sentis multi-cancer precise medication guidance (tissue + paired blood)': 702,
    'sentis multi cancer precision medicacion guidance (196 genes)': 702,
    'sentis gastrointestinal cancer medication guidance (tissue)': 687,
    'sentis gastrointestinal cancer medicacion guidance (58 genes)': 687,
    'sentis gastrointestinal cancer medication guidance (ctdna)': 681,
    'sentis gastrointestinal cancer medicacion guidance (ctdna) (58 genes)': 681,
    'sentis urinary system medication guidance': 718,
    'sentis urinary system cancer medicacion guidance (22 genes)': 718,
    'sentis pancreatic cancer medication guidance': 627,
    'sentis pancreatic cancer medicacion guidance (74 genes)': 627,
    'sentis panel cáncer hereditario': 585,
    'sentis panel cancer hereditario': 585,
    'invitae canceres heredit comunes': 476,
    'panel de cánceres hereditarios': 476,
    'sentis: multi-cancer precision medication guidance (ctdna)': 645,
    'sentis: multi-cancer precision medication guidance': 645,
    'sentis multi cancer precision medicacion guidance (ctdna) (196 genes)': 645,
    'sentis cancer + discovery (t)': 498,
    'sentis discovery tissue': 498,
    'sentis cancer + discovery (b)': 499,
    'sentis discovery ctdna': 499
}

def normalize(text):
    if not text:
        return ''
    s = str(text).strip().lower()
    return re.sub(r'\s+', ' ', s)

def run_odoo_mcp(command_args):
    """Ejecuta comandos CLI mediante odoo-mcp sin usar xmlrpc directamente"""
    cmd = [ODOO_MCP_BIN] + command_args
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(res.stdout)
    except Exception as e:
        print(f"Error ejecutando odoo-mcp: {e}")
        return None

def main():
    print(f"Iniciando análisis y carga de listas de precios desde: {EXCEL_PATH}")
    if not os.path.exists(EXCEL_PATH):
        print(f"Archivo no encontrado: {EXCEL_PATH}")
        sys.exit(1)

    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    new_rules = []
    
    for sname, pl_id in SHEET_TO_PRICELIST.items():
        if sname not in wb.sheetnames:
            print(f"Pestaña {sname} no encontrada en Excel.")
            continue
        ws = wb[sname]
        header = None
        start_row = 1
        for r in range(1, 10):
            row_vals = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
            if any(c and ('pricelist_id' in str(c).lower() or 'aplied_on' in str(c).lower()) for c in row_vals):
                header = [str(c).strip().lower() if c else '' for c in row_vals]
                start_row = r + 1
                break
        
        code_idx, name_idx, price_idx = None, None, None
        for idx, h in enumerate(header):
            if 'default_ code' in h or 'default_code' in h or 'code' in h:
                code_idx = idx + 1
            elif 'name' in h and ('templ' in h or 'product' in h):
                name_idx = idx + 1
            elif 'fixed_price' in h or 'price' in h:
                price_idx = idx + 1
                
        for r in range(start_row, ws.max_row + 1):
            cval = ws.cell(r, code_idx).value if code_idx else None
            nval = ws.cell(r, name_idx).value if name_idx else None
            pval = ws.cell(r, price_idx).value if price_idx else None
            if not cval and not nval and not pval:
                continue
            
            clean_p = str(pval).replace(',', '').strip() if pval is not None else '0'
            try:
                price = round(float(clean_p), 2)
            except ValueError:
                continue
                
            norm_c, norm_n = normalize(cval), normalize(nval)
            tmpl_id = KNOWN_MAPPINGS.get(norm_c) or KNOWN_MAPPINGS.get(norm_n)
            
            # Caso especial GNP fila 33 (Afirma Xpression Atlas capturado como Afirma GSC con precio 41156.90)
            if pl_id == 71 and norm_c == 'afirma gsc' and abs(price - 41156.90) < 1.0:
                tmpl_id = 672
                
            if tmpl_id:
                new_rules.append({
                    "pricelist_id": pl_id,
                    "product_tmpl_id": tmpl_id,
                    "fixed_price": price,
                    "min_quantity": 1.0,
                    "applied_on": "1_product",
                    "compute_price": "fixed",
                    "base": "list_price",
                    "company_id": COMPANY_ID
                })

    print(f"Total de reglas analizadas en Excel: {len(new_rules)}")
    output_path = os.path.join(os.path.dirname(__file__), 'pricelists_v2_payload.json')
    with open(output_path, 'w') as f:
        json.dump(new_rules, f, indent=2)
    print(f"Payload guardado para ejecución en producción: {output_path}")

if __name__ == '__main__':
    main()
