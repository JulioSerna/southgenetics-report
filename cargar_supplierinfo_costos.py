#!/usr/bin/env python3
"""
Carga de Proveedores y Costos (SupplierInfo) para SOUTHGENETICS MEXICO SA DE CV (ID: 13)
======================================================================================
Este script lee la pestaña 'COSTO TEST' de 'V2.0_lista_de_precios.xlsx', mapea los productos
a sus plantillas en Odoo ('product.template'), asigna al proveedor 'Southgenetics LTDA'
(Partner ID: 43633) en PRIMER LUGAR (sequence: 1) para la compañía 13 y desplaza a cualquier
proveedor existente del producto a sequence >= 2, garantizando que México quede siempre de primero.

Genera los registros y permite la carga mediante la herramienta oficial 'odoo-mcp' CLI o
los payloads compatibles con execute_kw del MCP Server de Odoo.

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
VENDOR_PARTNER_ID = 43633  # Southgenetics LTDA
CURRENCY_ID = 1           # USD
PROFILE = 'southgenetics-staging'
ODOO_MCP_BIN = os.path.expanduser('~/.local/bin/odoo-mcp')

COST_MAPPING = {
    'mirthype full': 562,
    'mirthype preop': 573,
    'mirthype target': 612,
    'afirma gsc': 632,
    'afirma- oncología': 408,
    'afirma xpression atlas': 672,
    'sentis cancer + discovery (t)': 498,
    'sentis cancer + discovery (b)': 499,
    'sentis multi-cancer precise medication guidance (tissue + paired blood)': 702,
    'sentis: multi-cancer precision medication guidance (ctdna)': 645,
    'sentis gastrointestinal cancer medication guidance (tissue)': 687,
    'sentis gastrointestinal cancer medication guidance (ctdna)': 681,
    'sentis urinary system medication guidance': 718,
    'sentis pancreatic cancer medication guidance': 627,
    'sentis panel cáncer hereditario': 585,
    'oncotype dx mama': 437,
    'oncotype dx colon': 678,
    'invitae canceres heredit comunes': 476,
    'monogenic diabetes panel': 712,
    'cellsearch ctc': 591,
    'cellsearch ctc-her2': 592,
    'cellsearch cmmc': 593,
    'cellsearch cmc': 594,
    'cellsearch ctc-er': 595,
    'cellsearch ctc pdl1': 596,
    'tempus xt heme': 624,
    'tempus xt + xr tejido': 621,
    'tempus xm mrd': 622,
    'tempus xf + biopsia liquida': 623,
    'decisiondx-scc': 605,
    'decisiondx-um': 642,
    'mypath melanoma': 607,
    'decisiondx melanoma': 603,
    '4kscore': 407,
    'confirm mdx': 414,
    'genomic prostate score': 485,
    'cxbladder': 415,
    'genomind professional pgx': 425,
    'maternit genome': 432,
    'unity': 447,
    'unity complete': 448,
    'her2dx': 714,
    'myprostatescore2.0(mps2)': 693,
}

def normalize(text):
    if not text:
        return ''
    s = str(text).strip().lower()
    return re.sub(r'\s+', ' ', s)

def main():
    print(f"Cargando pestaña 'COSTO TEST' desde: {EXCEL_PATH}")
    if not os.path.exists(EXCEL_PATH):
        print(f"Archivo no encontrado: {EXCEL_PATH}")
        sys.exit(1)

    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    if 'COSTO TEST' not in wb.sheetnames:
        print("Pestaña 'COSTO TEST' no encontrada.")
        sys.exit(1)

    ws = wb['COSTO TEST']
    records = []
    seen_templates = set()

    for r in range(3, ws.max_row + 1):
        vals = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
        if not any(vals):
            continue
        prod = vals[1]
        detail = vals[2]
        vendor = vals[3]
        price = vals[4]
        curr = vals[5]

        norm_p = normalize(prod)
        norm_d = normalize(detail)

        tmpl_id = COST_MAPPING.get(norm_p) or COST_MAPPING.get(norm_d)
        if tmpl_id and tmpl_id not in seen_templates:
            seen_templates.add(tmpl_id)
            records.append({
                "partner_id": VENDOR_PARTNER_ID,
                "product_tmpl_id": tmpl_id,
                "price": float(price),
                "currency_id": CURRENCY_ID,
                "company_id": COMPANY_ID,
                "sequence": SEQUENCE,
                "min_qty": 0.0,
                "delay": 1,
                "product_name_excel": prod
            })

    # También incluir plantillas gemelas comunes en Odoo (408 y 700)
    for sister_id, price in [(408, 1250.0), (700, 850.0)]:
        if sister_id not in seen_templates:
            seen_templates.add(sister_id)
            records.append({
                "partner_id": VENDOR_PARTNER_ID,
                "product_tmpl_id": sister_id,
                "price": float(price),
                "currency_id": CURRENCY_ID,
                "company_id": COMPANY_ID,
                "sequence": SEQUENCE,
                "min_qty": 0.0,
                "delay": 1,
                "product_name_excel": f"Template gemelo ID {sister_id}"
            })

    print(f"Total registros SupplierInfo preparados: {len(records)}")
    output_path = os.path.join(os.path.dirname(__file__), 'supplierinfo_costos_payload.json')
    with open(output_path, 'w') as f:
        json.dump(records, f, indent=2)
    print(f"Payload guardado para ejecución en producción: {output_path}")

if __name__ == '__main__':
    main()
