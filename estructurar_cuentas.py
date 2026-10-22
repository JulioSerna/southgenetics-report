#!/usr/bin/env python3
"""
Script Maestro y Definitivo de Depuración, Homologación y Creación del Plan Contable
para SOUTHGENETICS MEXICO SA DE CV (Company ID: 13).

Reglas de oro implementadas de forma idempotente (para cualquier Staging o Producción):
1. Toma como única fuente de verdad las 162 cuentas a 3 niveles de 'Catalogo_de_cuentas_SOUTH_Odoo_2_niveles.xlsx'.
2. Libera la cuenta transitoria bancaria (ID 1841 -> '102.01.97 Cuenta transitoria de banco (Suspense)')
   para que la cuenta del banco BBVA 3786 (ID 1839) pueda tomar su código oficial '102.01.02'.
3. Homologa/unifica las 75 cuentas preexistentes en Odoo que corresponden al catálogo del Drive
   (actualizando su código a 3 niveles y su nombre tanto en en_US como en es_AR) y conserva las 3 cuentas
   preexistentes que ya tenían el código y nombre oficial ('107.05.01', '201.01.01', '205.06.01').
4. Crea únicamente las cuentas del Excel del Drive que aún no existen (84 cuentas nuevas), sin duplicar
   las cuentas unificadas. Si existieran duplicados creados por error previo, reasigna referencias y los elimina.
5. Reasigna todas las propiedades contables (ir.property) de la Compañía 13:
   - property_account_receivable_id -> '105.01.01' (Clientes nacionales)
   - property_account_payable_id    -> '201.01.01' (Proveedores nacionales)
   - property_account_income_categ_id -> '401.01.01' (Oncología)
6. Elimina definitivamente (unlink) las 80 cuentas individuales legacy de clientes y proveedores
   (105.01.xxx, 107.xx.xxx, 201.01.xxx) para que nunca queden múltiples cuentas por cobrar o pagar.
7. Marca como obsoletas (deprecated = True) todas las demás cuentas no oficiales que no sean cuentas
   técnicas indispensables de Odoo (bancos suspense/transferencia, impuestos SAT, provisión laboratorio).
"""

import subprocess
import json
import sys
import openpyxl
import re

PROFILE = sys.argv[1] if len(sys.argv) > 1 else 'southgenetics-staging'

def run_server_code(code, name="__master_coa_sync"):
    create_val = {'name': name, 'model_id': 94, 'state': 'code', 'code': code}
    res = subprocess.run(
        ['odoo-mcp', 'create', '--profile', PROFILE, '--model', 'ir.actions.server', '--values', json.dumps(create_val)],
        capture_output=True, text=True
    )
    try:
        act_id = json.loads(res.stdout)['id']
    except Exception:
        print("Error creando ir.actions.server:", res.stdout, res.stderr)
        raise
    try:
        res_run = subprocess.run(
            ['odoo-mcp', 'execute-kw', '--profile', PROFILE, '--model', 'ir.actions.server', '--method', 'run', '--args', f'[[{act_id}]]'],
            capture_output=True, text=True
        )
        return json.loads(res_run.stdout)
    except Exception:
        print("Error ejecutando ir.actions.server:", res_run.stdout, res_run.stderr)
        raise
    finally:
        subprocess.run(
            ['odoo-mcp', 'unlink', '--profile', PROFILE, '--model', 'ir.actions.server', '--ids', str(act_id)],
            capture_output=True, text=True
        )

# 1. Leer las 162 cuentas oficiales del Excel del Drive
excel_path = '/Users/julioserna/.gemini/antigravity/scratch/southgenetics/Catalogo_de_cuentas_SOUTH_Odoo_2_niveles.xlsx'
wb = openpyxl.load_workbook(excel_path, data_only=True)
ws = wb['CATALOGO NIVEL 3']

excel_accounts = []
for row in ws.iter_rows(min_row=11, values_only=True):
    code = str(row[1]).strip() if row[1] is not None else ''
    sat = str(row[2]).strip() if row[2] is not None else ''
    name = str(row[3]).strip() if row[3] is not None else ''
    if re.match(r'^\d{3}\.\d{2}\.\d{2}$', code) and name:
        excel_accounts.append({'code': code, 'name': name, 'sat': sat})

# 2. Leer el mapa validado de unificación (IDs preexistentes y cuentas técnicas)
with open('/Users/julioserna/.gemini/antigravity/scratch/southgenetics/full_report_data_v2.json') as f:
    report_ref = json.load(f)

unified_map = [
    {'id': u['id'], 'old_code': u['old_code'], 'new_code': u['new_code'], 'new_name': u['new_name']}
    for u in report_ref['unified'] if u['id'] <= 12810
]

# Las 80 cuentas legacy individuales (105.01.xxx, 107.xx.xxx, 201.01.xxx, etc.) que siempre deben eliminarse (unlink)
legacy_unlink_ids = [
    1793, 8034, 8035, 8036, 8037, 8038, 8039, 8040, 8041, 8042, 8043, 12752, 12753,
    8044, 8045, 12760, 8046, 8047, 8048, 8049, 8050, 8051, 8052, 8053, 8054, 8055,
    8056, 4708, 8061, 8062, 8063, 8064, 8065, 8066, 8067, 8068, 8069, 8070, 8071,
    8072, 8073, 8074, 8075, 8076, 8077, 12754, 8078, 8079, 8080, 8081, 8082, 8083,
    8084, 8085, 8086, 8087, 8088, 8089, 8090, 12755, 8091, 8092, 12756, 8093, 8094,
    8095, 8096, 8097, 8098, 8099, 8100, 8101, 8102, 8103, 8104, 8105, 8106, 8107,
    8108, 12810
]

# Cuentas técnicas preexistentes que Odoo requiere activas (deprecated = False)
tech_active_ids = [1846, 1841, 4702, 1805, 1816, 8115, 1824, 1821, 1822]

server_code = f"""
company_id = 13
Account = env['account.account']
Prop = env['ir.property']
Journal = env['account.journal']
Asset = env['account.asset']

excel_accs = {repr(excel_accounts)}
unified_list = {repr(unified_map)}
legacy_ids = {repr(legacy_unlink_ids)}
tech_ids = {repr(tech_active_ids)}

type_map = {{
    '101': 'asset_cash', '102': 'asset_cash', '103': 'asset_current',
    '105': 'asset_receivable', '106': 'asset_current', '107': 'asset_current',
    '108': 'asset_current', '109': 'asset_current', '110': 'asset_current',
    '111': 'asset_current', '112': 'asset_current', '113': 'asset_current',
    '114': 'asset_current', '115': 'asset_current', '118': 'asset_current',
    '119': 'asset_current', '120': 'asset_current', '151': 'asset_fixed',
    '152': 'asset_fixed', '153': 'asset_fixed', '154': 'asset_fixed',
    '155': 'asset_fixed', '156': 'asset_fixed', '157': 'asset_fixed',
    '158': 'asset_fixed', '171': 'asset_fixed', '184': 'asset_fixed',
    '201': 'liability_payable', '202': 'liability_current', '203': 'liability_current',
    '204': 'liability_current', '205': 'liability_current', '208': 'liability_current',
    '209': 'liability_current', '210': 'liability_current', '211': 'liability_current',
    '212': 'liability_current', '213': 'liability_current', '215': 'liability_current',
    '216': 'liability_current', '301': 'equity', '302': 'equity',
    '303': 'equity', '304': 'equity', '401': 'income', '402': 'income_other',
    '403': 'income_other', '501': 'expense_direct_cost', '502': 'expense_direct_cost',
    '503': 'income_other', '504': 'income_other', '601': 'expense',
    '602': 'expense', '607': 'expense', '610': 'expense', '611': 'expense',
    '701': 'expense', '702': 'expense', '703': 'income_other', '704': 'expense'
}}

# 1. Liberar primero la cuenta transitoria de banco (ID 1841) para no colisionar con 102.01.02
acc_1841 = Account.browse(1841)
if acc_1841.exists():
    acc_1841.with_context(lang='en_US').write({{
        'code': '102.01.97',
        'name': 'Cuenta transitoria de banco (Suspense)',
        'deprecated': False
    }})
    acc_1841.with_context(lang='es_AR').write({{'name': 'Cuenta transitoria de banco (Suspense)'}})

# 2. Homologar las 75 cuentas preexistentes (y eliminar cualquier duplicado nuevo si existiera)
unified_target_codes = {{}}
for u in unified_list:
    uid = u['id']
    t_code = u['new_code']
    t_name = u['new_name']
    unified_target_codes[t_code] = uid
    # Si existe otra cuenta diferente con ese código oficial (duplicado), liberarla o borrarla
    dups = Account.search([('company_id', '=', company_id), ('code', '=', t_code), ('id', '!=', uid)])
    for d in dups:
        # Reasignar activos si apuntaban al duplicado
        for r in Asset.search([('company_id', '=', company_id)]):
            avals = {{}}
            if r.account_asset_id.id == d.id: avals['account_asset_id'] = uid
            if r.account_depreciation_id.id == d.id: avals['account_depreciation_id'] = uid
            if r.account_depreciation_expense_id.id == d.id: avals['account_depreciation_expense_id'] = uid
            if avals: r.write(avals)
        for p in Prop.search([('company_id', '=', company_id), ('value_reference', '=', f'account.account,{{d.id}}')]):
            p.write({{'value_reference': f'account.account,{{uid}}'}})
        d.unlink()
    acc = Account.browse(uid)
    if acc.exists():
        acc.with_context(lang='en_US').write({{'code': t_code, 'name': t_name, 'deprecated': False}})
        acc.with_context(lang='es_AR').write({{'name': t_name}})

# 3. Crear o asegurar las cuentas restantes del Excel del Drive (84 nuevas + 3 que ya existían)
existing_by_code = {{a.code: a for a in Account.search([('company_id', '=', company_id)])}}
created_count = 0
for item in excel_accs:
    c = item['code']
    n = item['name']
    if c in existing_by_code:
        acc = existing_by_code[c]
        acc.with_context(lang='en_US').write({{'name': n, 'deprecated': False}})
        acc.with_context(lang='es_AR').write({{'name': n}})
    else:
        acc_type = type_map.get(c[:3], 'expense')
        new_acc = Account.with_context(lang='en_US').create({{
            'code': c,
            'name': n,
            'company_id': company_id,
            'account_type': acc_type,
            'deprecated': False
        }})
        new_acc.with_context(lang='es_AR').write({{'name': n}})
        existing_by_code[c] = new_acc
        created_count += 1

# 4. Reasignar ir.property a las cuentas oficiales únicas (105.01.01, 201.01.01, 401.01.01)
acc_cxc = Account.search([('company_id', '=', company_id), ('code', '=', '105.01.01')], limit=1)
acc_cxp = Account.search([('company_id', '=', company_id), ('code', '=', '201.01.01')], limit=1)
acc_inc = Account.search([('company_id', '=', company_id), ('code', '=', '401.01.01')], limit=1)

for p in Prop.search([('company_id', '=', company_id), ('value_reference', 'like', 'account.account,')]):
    if p.name == 'property_account_receivable_id' and acc_cxc:
        p.write({{'value_reference': f'account.account,{{acc_cxc.id}}'}})
    elif p.name == 'property_account_payable_id' and acc_cxp:
        p.write({{'value_reference': f'account.account,{{acc_cxp.id}}'}})
    elif p.name == 'property_account_income_categ_id' and acc_inc:
        p.write({{'value_reference': f'account.account,{{acc_inc.id}}'}})

if acc_inc:
    j49 = Journal.browse(49)
    if j49.exists():
        j49.write({{'default_account_id': acc_inc.id}})

# 5. Eliminar (unlink) todas las cuentas individuales CxC / CxP legacy (80 cuentas)
unlinked_legacy = 0
for lid in legacy_ids:
    acc = Account.browse(lid)
    if acc.exists():
        acc.unlink()
        unlinked_legacy += 1

# 6. Marcar como obsoletas (deprecated = True) todas las cuentas que NO están en el Excel ni en tech_ids
excel_code_set = {{x['code'] for x in excel_accs}}
tech_id_set = set(tech_ids)
deprecated_marked = 0
for acc in Account.search([('company_id', '=', company_id)]):
    if acc.code in excel_code_set or acc.id in tech_id_set:
        if acc.deprecated:
            acc.write({{'deprecated': False}})
    else:
        if not acc.deprecated:
            acc.write({{'deprecated': True}})
            deprecated_marked += 1

action = {{
    'created_count': created_count,
    'unlinked_legacy': unlinked_legacy,
    'active_count': Account.search_count([('company_id', '=', company_id), ('deprecated', '=', False)]),
    'deprecated_count': Account.search_count([('company_id', '=', company_id), ('deprecated', '=', True)]),
    'total_count': Account.search_count([('company_id', '=', company_id)])
}}
"""

if __name__ == '__main__':
    res = run_server_code(server_code)
    print("Resultado estructuración y depuración del Plan Contable:", json.dumps(res, indent=2))
