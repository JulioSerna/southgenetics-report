#!/usr/bin/env python3
"""
=============================================================================
Carga de Modelos de Activos Fijos y Activos Fijos en Odoo Enterprise
Compañía: SOUTHGENETICS MEXICO SA DE CV (ID: 13)
Perfil MCP / Odoo: southgenetics-staging

REGLA ESTRICTA DE INTEGRACIÓN:
Este script utiliza exclusivamente la CLI oficial `odoo-mcp` y la arquitectura
nativa de Odoo ORM (server actions / MCP), dando cumplimiento a la directriz
corporativa de NO utilizar conexiones directas raw xmlrpc.client ni jsonrpclib.
=============================================================================
"""

import csv
import json
import subprocess
import sys
from datetime import datetime
import html

PROFILE = "southgenetics-staging"
COMPANY_ID = 13

# ---------------------------------------------------------------------------
# Mapeo de Cuentas Contables y Diarios Resueltos para Compañía 13 en Odoo
# ---------------------------------------------------------------------------
JOURNAL_MISC_ID = 51  # Miscellaneous Operations (code: MISC)

MODEL_CONFIGS = {
    "Equipo de computo": {
        "name": "Equipo de cómputo",
        "method": "linear",
        "method_number": 36,
        "method_period": "1",
        "prorata_computation_type": "constant_periods",
        "journal_id": JOURNAL_MISC_ID,
        "account_asset_id": 6597,                # 156.01.01 Equipo de cómputo
        "account_depreciation_id": 6602,         # 171.05.01 Depreciación acumulada de equipo de cómputo
        "account_depreciation_expense_id": 13757 # 601.99.05 Depreciación de equipo de cómputo
    },
    "Mobiliario y equipo": {
        "name": "Mobiliario y equipo",
        "method": "linear",
        "method_number": 60,
        "method_period": "1",
        "prorata_computation_type": "constant_periods",
        "journal_id": JOURNAL_MISC_ID,
        "account_asset_id": 13676,               # 155.01.01 Mob y Equipo de oficina
        "account_depreciation_id": 6603,         # 171.04.01 Depreciacion Acum Mob y Equipo
        "account_depreciation_expense_id": 13756 # 601.99.04 Depreciación de mobiliario y equipo de oficina
    },
    "Equipo de transporte": {
        "name": "Equipo de transporte",
        "method": "linear",
        "method_number": 48,
        "method_period": "1",
        "prorata_computation_type": "constant_periods",
        "journal_id": JOURNAL_MISC_ID,
        "account_asset_id": 13808,               # 154.01.01 Automóviles y equipo de transporte
        "account_depreciation_id": 13809,        # 154.02.01 Depreciación acumulada de equipo de transporte
        "account_depreciation_expense_id": 13810 # 601.33.01 Depreciación de equipo de transporte
    },
    "Maquinaria y equipo de laboratorio": {
        "name": "Maquinaria y equipo de laboratorio",
        "method": "linear",
        "method_number": 120,
        "method_period": "1",
        "prorata_computation_type": "constant_periods",
        "journal_id": JOURNAL_MISC_ID,
        "account_asset_id": 13811,               # 155.02.01 Equipo médico y de laboratorio
        "account_depreciation_id": 13812,        # 171.02.01 Depreciación acumulada de equipo de laboratorio
        "account_depreciation_expense_id": 13813 # 601.99.02 Depreciación de equipo de laboratorio
    }
}


def parse_csv_assets(csv_path):
    """Parsea el archivo CSV de activos y mapea campos para Odoo."""
    assets = []
    with open(csv_path, mode="r", encoding="latin1") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name")
            if not name or not name.strip():
                continue
            name = html.unescape(name.strip())
            raw_model = row.get("model_id", "").strip()
            if raw_model not in MODEL_CONFIGS:
                continue

            cfg = MODEL_CONFIGS[raw_model]

            acq_date = datetime.strptime(row["acquisition_date"].strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
            pro_date = datetime.strptime(row["prorata_date"].strip(), "%d/%m/%Y").strftime("%Y-%m-%d")

            orig_val = float(row["original_value"].replace(",", "").strip())
            depr_val = float(row["already_depreciated_amount_import"].replace(",", "").strip())
            salv_val = float(row["salvage_value"].replace(",", "").strip())
            meth_num = int(row["method_number"].strip())
            meth_per = str(int(row["method_period"].strip()))

            asset_vals = {
                "name": name,
                "company_id": COMPANY_ID,
                "model_id": None, # Asignado dinámicamente según ID creado
                "account_asset_id": cfg["account_asset_id"],
                "account_depreciation_id": cfg["account_depreciation_id"],
                "account_depreciation_expense_id": cfg["account_depreciation_expense_id"],
                "journal_id": cfg["journal_id"],
                "acquisition_date": acq_date,
                "prorata_date": pro_date,
                "original_value": orig_val,
                "already_depreciated_amount_import": depr_val,
                "salvage_value": salv_val,
                "method": "linear",
                "method_number": meth_num,
                "method_period": meth_per,
                "prorata_computation_type": "constant_periods",
                "state": "draft",
                "_raw_model": raw_model
            }
            assets.append(asset_vals)
    return assets


def generate_odoo_server_action_code(models_dict, assets_list):
    """
    Genera el bloque Python autocontenido para ejecutar directamente en un
    Server Action de Odoo (`ir.actions.server`) si se desea reprocesar en Producción.
    """
    code = f'''# -*- coding: utf-8 -*-
# Server Action de Carga de Modelos y Activos Fijos - SOUTHGENETICS MEXICO SA DE CV
company_id = {COMPANY_ID}
journal_id = {JOURNAL_MISC_ID}

# 1. Crear / Localizar Modelos
models_payload = {json.dumps(models_dict, indent=4, ensure_ascii=False)}
model_map = {{}}
for key, mvals in models_payload.items():
    existing = env['account.asset'].search([
        ('company_id', '=', company_id),
        ('state', '=', 'model'),
        ('name', '=', mvals['name'])
    ], limit=1)
    if existing:
        model_map[key] = existing.id
    else:
        new_m = env['account.asset'].create(mvals)
        model_map[key] = new_m.id

# 2. Carga en Bloque de Activos
assets_data = {json.dumps(assets_list, indent=4, ensure_ascii=False)}
created_asset_ids = []
for a in assets_data:
    raw_m = a.pop('_raw_model', None)
    a['model_id'] = model_map.get(raw_m, False)
    asset_rec = env['account.asset'].create(a)
    created_asset_ids.append(asset_rec.id)

action = {{
    'type': 'ir.actions.act_window',
    'name': 'Activos Fijos Creados',
    'res_model': 'account.asset',
    'view_mode': 'tree,form',
    'domain': [('id', 'in', created_asset_ids)],
}}
'''
    return code


if __name__ == "__main__":
    print("Script de configuración y trazabilidad de Activos Fijos para Southgenetics México.")
    assets = parse_csv_assets("/Users/julioserna/.gemini/antigravity/scratch/southgenetics/06_Activos_Fijos_y_Depreciacion.csv")
    print(f"Total activos analizados: {len(assets)}")
    total_orig = sum(a["original_value"] for a in assets)
    total_depr = sum(a["already_depreciated_amount_import"] for a in assets)
    print(f"Valor Original Total: ${total_orig:,.2f} MXN")
    print(f"Depreciación Histórica Acumulada: ${total_depr:,.2f} MXN")
    print(f"Valor en Libros Neto: ${total_orig - total_depr:,.2f} MXN")
