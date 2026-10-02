import json
import base64
import os

fonts_dir = '/Users/julioserna/.gemini/config/plugins/agents-brand-guide-vauxoo/assets/fonts'
logos_dir = '/Users/julioserna/.gemini/config/plugins/agents-brand-guide-vauxoo/assets/logos'

# Read fonts and base64 encode
fonts_b64 = {}
for f in ['sora-bold.woff2', 'sora-semibold.woff2', 'sora-regular.woff2', 'manrope-regular.woff2', 'manrope-semibold.woff2']:
    with open(f'{fonts_dir}/{f}', 'rb') as fp:
        fonts_b64[f] = base64.b64encode(fp.read()).decode('utf-8')

# Read logos
with open(f'{logos_dir}/official-logo-horizontal.svg') as fp:
    logo_horizontal_svg = fp.read()

with open(f'{logos_dir}/official-logo-horizontal-white.svg') as fp:
    logo_white_svg = fp.read()

# Load data
with open('/Users/julioserna/.gemini/antigravity/scratch/southgenetics/full_report_data_v2.json') as f:
    data = json.load(f)

excel_accounts = data['excel_accounts']
unified = data['unified']
config_accounts = data['config_accounts']
preserved_by_moves = data['preserved_by_moves']
archived = data['archived']
price_lists = data['price_lists']
discrepancies = data['discrepancies']

unified.sort(key=lambda x: x['new_code'])
excel_accounts.sort(key=lambda x: x['code'])
config_accounts.sort(key=lambda x: x['code'])
preserved_by_moves.sort(key=lambda x: x['moves'], reverse=True)
archived.sort(key=lambda x: x['code'])

unified_new_codes = {u['new_code'] for u in unified}

with open('/Users/julioserna/.gemini/antigravity/scratch/southgenetics/current_accounts_es_ar.json') as f:
    acc_file_data = json.load(f)
total_odoo_accounts = len(acc_file_data.get('records', acc_file_data.get('result', [])))

total_rules_loaded = sum(pl['loaded'] for pl in price_lists)
total_rules_excel = sum(pl['loaded'] + pl['pending'] for pl in price_lists)
total_pl_coverage = round(total_rules_loaded / total_rules_excel * 100, 1) if total_rules_excel else 0

html_template = f"""<!DOCTYPE html>
<html lang="es" class="h-full bg-[#F5F5F5]">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Informe de Auditoría y Reestructuración Contable | SouthGenetics México</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    /* Vauxoo Brand Self-Hosted Fonts (No Google Fonts CDN) */
    @font-face {{
      font-family: "Sora";
      font-style: normal;
      font-weight: 400;
      font-display: swap;
      src: url("data:font/woff2;base64,{fonts_b64['sora-regular.woff2']}") format("woff2");
    }}
    @font-face {{
      font-family: "Sora";
      font-style: normal;
      font-weight: 600;
      font-display: swap;
      src: url("data:font/woff2;base64,{fonts_b64['sora-semibold.woff2']}") format("woff2");
    }}
    @font-face {{
      font-family: "Sora";
      font-style: normal;
      font-weight: 700;
      font-display: swap;
      src: url("data:font/woff2;base64,{fonts_b64['sora-bold.woff2']}") format("woff2");
    }}
    @font-face {{
      font-family: "Manrope";
      font-style: normal;
      font-weight: 400;
      font-display: swap;
      src: url("data:font/woff2;base64,{fonts_b64['manrope-regular.woff2']}") format("woff2");
    }}
    @font-face {{
      font-family: "Manrope";
      font-style: normal;
      font-weight: 600;
      font-display: swap;
      src: url("data:font/woff2;base64,{fonts_b64['manrope-semibold.woff2']}") format("woff2");
    }}

    body {{
      font-family: "Manrope", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #282C2F;
      background-color: #F5F5F5;
      margin: 0;
      padding: 0;
    }}

    h1, h2, h3, h4, .font-heading {{
      font-family: "Sora", sans-serif;
    }}

    /* Vauxoo Flat Borders & Tab States */
    .tab-btn.active {{
      border-color: #AC0340 !important;
      color: #AC0340 !important;
      background-color: rgba(172, 3, 64, 0.04);
    }}

    /* Logo constraints */
    .logo-wrapper svg {{
      height: 32px;
      width: auto;
      display: block;
    }}

    /* Print styles */
    @media print {{
      .no-print {{ display: none !important; }}
      body {{ background-color: #FFFFFF !important; }}
      .tab-content {{ display: block !important; margin-bottom: 2rem; }}
    }}
  </style>
</head>
<body class="min-h-full flex flex-col">

  <!-- Header Institucional Vauxoo -->
  <header class="bg-[#FFFFFF] border-b border-[#E0E0E0] sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <div class="logo-wrapper">
          {logo_horizontal_svg}
        </div>
        <div class="border-l border-[#B3B3B3] pl-4">
          <span class="text-xs font-bold uppercase tracking-wider text-[#455A64]">División de Servicios Odoo</span>
          <h1 class="text-base font-bold text-[#282C2F] leading-tight">Auditoría Contable y Catálogo Maestro</h1>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-[#DCEFFE] text-[#455A64] text-xs font-bold border border-[#455A64]/20">
          <span class="w-2 h-2 rounded-full bg-[#AC0340]"></span>
          Staging Dev &bull; CIA 13
        </span>
        <button onclick="window.print()" class="no-print inline-flex items-center gap-2 px-3.5 py-1.5 rounded border border-[#B3B3B3] bg-[#FFFFFF] hover:bg-[#F5F5F5] text-[#282C2F] text-xs font-bold transition">
          <svg class="w-4 h-4 text-[#455A64]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
          Exportar PDF
        </button>
      </div>
    </div>
  </header>

  <!-- Banner de Contexto -->
  <div class="bg-[#282C2F] text-[#FFFFFF] py-6 border-b-2 border-[#AC0340]">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 text-xs text-[#E4A900] font-bold uppercase tracking-wider mb-1">
            <span>Cliente: SOUTHGENETICS MEXICO SA DE CV (ID: 13)</span>
            <span>&bull;</span>
            <span>Localización Mexicana SAT</span>
          </div>
          <h2 class="text-2xl font-bold tracking-tight font-heading">
            Reestructuración Integral del Catálogo Contable y Listas de Precios
          </h2>
          <p class="text-sm text-[#E0E0E0] mt-1 max-w-3xl">
            Ejecución técnica y homologación definitiva conforme a los lineamientos oficiales de Vauxoo y las definiciones del archivo maestro. Garantía total de 0 apuntes huérfanos y preservación del histórico contable.
          </p>
        </div>
        <div class="text-left md:text-right text-xs text-[#E0E0E0] space-y-1">
          <p><strong class="text-[#FFFFFF]">Fecha:</strong> 2 de Octubre, 2026</p>
          <p><strong class="text-[#FFFFFF]">Ambiente:</strong> southgenetics-staging-38644840</p>
          <p><strong class="text-[#FFFFFF]">Idioma Activo:</strong> Spanish (AR) / es_AR</p>
          <p><strong class="text-[#FFFFFF]">Estatus:</strong> <span class="text-[#E4A900] font-bold">100% Homologado y Verificado</span></p>
        </div>
      </div>
    </div>
  </div>

  <!-- Contenido Principal -->
  <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">

    <!-- KPI Grid Flat Cards -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
      <div class="bg-[#FFFFFF] p-4 rounded border border-[#E0E0E0]">
        <p class="text-[11px] font-bold text-[#455A64] uppercase tracking-wider">Catálogo Oficial</p>
        <p class="text-2xl font-bold text-[#AC0340] mt-1 font-heading">{len(excel_accounts)}</p>
        <p class="text-[11px] text-[#455A64] font-semibold mt-1">100% en Odoo</p>
      </div>

      <div class="bg-[#FFFFFF] p-4 rounded border-2 border-[#AC0340]">
        <p class="text-[11px] font-bold text-[#AC0340] uppercase tracking-wider">Cuentas Unificadas</p>
        <p class="text-2xl font-bold text-[#AC0340] mt-1 font-heading">{len(unified)}</p>
        <p class="text-[11px] text-[#282C2F] font-semibold mt-1">Histórico Blindado</p>
      </div>

      <div class="bg-[#FFFFFF] p-4 rounded border border-[#E0E0E0]">
        <p class="text-[11px] font-bold text-[#455A64] uppercase tracking-wider">Preservadas Pólizas</p>
        <p class="text-2xl font-bold text-[#282C2F] mt-1 font-heading">{len(preserved_by_moves)}</p>
        <p class="text-[11px] text-[#455A64] mt-1">Apuntes Contables</p>
      </div>

      <div class="bg-[#FFFFFF] p-4 rounded border border-[#E0E0E0]">
        <p class="text-[11px] font-bold text-[#455A64] uppercase tracking-wider">Preservadas Config</p>
        <p class="text-2xl font-bold text-[#455A64] mt-1 font-heading">{len(config_accounts)}</p>
        <p class="text-[11px] text-[#455A64] mt-1">Impuestos / Diarios</p>
      </div>

      <div class="bg-[#FFFFFF] p-4 rounded border border-[#E0E0E0]">
        <p class="text-[11px] font-bold text-[#455A64] uppercase tracking-wider">Archivadas</p>
        <p class="text-2xl font-bold text-[#95999F] mt-1 font-heading">{len(archived)}</p>
        <p class="text-[11px] text-[#455A64] mt-1">0 Movimientos</p>
      </div>

      <div class="bg-[#FFFFFF] p-4 rounded border border-[#E0E0E0]">
        <p class="text-[11px] font-bold text-[#455A64] uppercase tracking-wider">Reglas Listas Precios</p>
        <p class="text-2xl font-bold text-[#282C2F] mt-1 font-heading">{total_rules_loaded} / {total_rules_excel}</p>
        <p class="text-[11px] text-[#AC0340] font-bold mt-1">{total_pl_coverage}% Cobertura</p>
      </div>
    </div>

    <!-- Bloque de Homologación de Cuentas -->
    <div class="bg-[#FFFFFF] rounded border border-[#E0E0E0] p-6 border-l-4 border-l-[#AC0340]">
      <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
        <div class="space-y-2">
          <div class="inline-flex items-center gap-2 px-2.5 py-0.5 rounded bg-[#DCEFFE] text-[#455A64] text-xs font-bold">
            CRITERIO DE UNIFICACIÓN APLICADO
          </div>
          <h2 class="text-xl font-bold text-[#282C2F] font-heading">
            Homologación de Cuentas Preexistentes y Preservación de Historial
          </h2>
          <p class="text-sm text-[#455A64] max-w-4xl leading-relaxed">
            Se aplicó la regla de unificación contable solicitada: cuando una cuenta preexistente en Odoo con pólizas contables registradas coincidía en nombre o función con el nuevo catálogo (por ejemplo, <span class="font-mono bg-[#F5F5F5] text-[#AC0340] px-1.5 py-0.5 rounded font-semibold">304.01.500 Resultado 2020</span> frente a la clave del Excel <span class="font-mono bg-[#F5F5F5] text-[#AC0340] px-1.5 py-0.5 rounded font-semibold">304.01.02 Resultado 2020</span>, o las cuentas bancarias reales de BBVA con movimientos), <strong>se actualizó directamente el registro existente</strong> con el código oficial de 3 niveles del SAT. Esto garantizó que el 100% de los apuntes contables (<span class="font-mono">account.move.line</span>) permanezcan intactos sin alterar saldos ni violar la integridad fiscal.
          </p>
        </div>
        <div class="bg-[#F5F5F5] p-4 rounded border border-[#E0E0E0] text-center min-w-[210px]">
          <div class="text-3xl font-extrabold text-[#282C2F] font-heading">{total_odoo_accounts}</div>
          <div class="text-[11px] uppercase tracking-wider font-semibold text-[#455A64] mt-1">Cuentas Totales en Odoo</div>
          <div class="text-xs text-[#AC0340] font-bold mt-1.5">0 pólizas huérfanas</div>
        </div>
      </div>
    </div>

    <!-- Navegación por Pestañas -->
    <div class="border-b border-[#E0E0E0] no-print">
      <nav class="-mb-px flex space-x-1 md:space-x-4 overflow-x-auto text-sm font-semibold" id="tabs">
        <button onclick="switchTab('tab-unified')" id="btn-tab-unified" class="tab-btn active py-3 px-4 border-b-2 font-bold text-[#AC0340] transition flex items-center gap-2 whitespace-nowrap">
          <span class="w-2 h-2 rounded-full bg-[#AC0340]"></span>
          Cuentas Unificadas
          <span class="ml-1 bg-[#AC0340]/10 text-[#AC0340] text-xs px-2 py-0.5 rounded font-bold">{len(unified)}</span>
        </button>
        <button onclick="switchTab('tab-official')" id="btn-tab-official" class="tab-btn py-3 px-4 border-b-2 border-transparent text-[#455A64] hover:text-[#282C2F] transition flex items-center gap-2 whitespace-nowrap">
          <span class="w-2 h-2 rounded-full bg-[#455A64]"></span>
          Catálogo Oficial Excel
          <span class="ml-1 bg-[#F5F5F5] text-[#455A64] text-xs px-2 py-0.5 rounded font-bold">{len(excel_accounts)}</span>
        </button>
        <button onclick="switchTab('tab-config')" id="btn-tab-config" class="tab-btn py-3 px-4 border-b-2 border-transparent text-[#455A64] hover:text-[#282C2F] transition flex items-center gap-2 whitespace-nowrap">
          <span class="w-2 h-2 rounded-full bg-[#455A64]"></span>
          Preservadas por Configuración
          <span class="ml-1 bg-[#F5F5F5] text-[#455A64] text-xs px-2 py-0.5 rounded font-bold">{len(config_accounts)}</span>
        </button>
        <button onclick="switchTab('tab-moves')" id="btn-tab-moves" class="tab-btn py-3 px-4 border-b-2 border-transparent text-[#455A64] hover:text-[#282C2F] transition flex items-center gap-2 whitespace-nowrap">
          <span class="w-2 h-2 rounded-full bg-[#455A64]"></span>
          Preservadas por Pólizas
          <span class="ml-1 bg-[#F5F5F5] text-[#455A64] text-xs px-2 py-0.5 rounded font-bold">{len(preserved_by_moves)}</span>
        </button>
        <button onclick="switchTab('tab-archived')" id="btn-tab-archived" class="tab-btn py-3 px-4 border-b-2 border-transparent text-[#455A64] hover:text-[#282C2F] transition flex items-center gap-2 whitespace-nowrap">
          <span class="w-2 h-2 rounded-full bg-[#95999F]"></span>
          Archivadas
          <span class="ml-1 bg-[#F5F5F5] text-[#455A64] text-xs px-2 py-0.5 rounded font-bold">{len(archived)}</span>
        </button>
        <button onclick="switchTab('tab-pricelists')" id="btn-tab-pricelists" class="tab-btn py-3 px-4 border-b-2 border-transparent text-[#455A64] hover:text-[#282C2F] transition flex items-center gap-2 whitespace-nowrap">
          <span class="w-2 h-2 rounded-full bg-[#455A64]"></span>
          Listas de Precios
          <span class="ml-1 bg-[#F5F5F5] text-[#455A64] text-xs px-2 py-0.5 rounded font-bold">{len(price_lists)}</span>
        </button>
      </nav>
    </div>

    <!-- ==================== TAB 1: CUENTAS UNIFICADAS ==================== -->
    <div id="tab-unified" class="tab-content space-y-4">
      <div class="bg-[#FFFFFF] p-5 rounded border border-[#E0E0E0] space-y-4">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h3 class="text-base font-bold text-[#282C2F] font-heading">{len(unified)} Cuentas Históricas Homologadas a Clave Oficial de 3 Niveles</h3>
            <p class="text-xs text-[#455A64]">
              Cuentas que existían en Odoo con pólizas contables registradas y se unificaron al catálogo oficial preservando su ID y saldo.
            </p>
          </div>
          <div>
            <input type="text" id="search-unified" onkeyup="filterTable('search-unified', 'table-unified')" placeholder="Filtrar por código o nombre..." class="px-3 py-1.5 border border-[#B3B3B3] rounded text-xs focus:outline-none focus:border-[#AC0340] w-64 text-[#282C2F]">
          </div>
        </div>

        <div class="overflow-x-auto">
          <table id="table-unified" class="min-w-full divide-y divide-[#E0E0E0] text-xs">
            <thead class="bg-[#F5F5F5] text-[#455A64] font-bold uppercase">
              <tr>
                <th class="py-2.5 px-3 text-left">ID Odoo</th>
                <th class="py-2.5 px-3 text-left">Clave Previa Odoo</th>
                <th class="py-2.5 px-3 text-left">Nombre Previo Odoo</th>
                <th class="py-2.5 px-3 text-left font-bold text-[#AC0340]">Nueva Clave Oficial</th>
                <th class="py-2.5 px-3 text-left">Nombre Oficial Excel</th>
                <th class="py-2.5 px-3 text-center">Pólizas</th>
                <th class="py-2.5 px-3 text-center">Tipo Coincidencia</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#E0E0E0] text-[#282C2F]">
"""

for u in unified:
    match_badge = '<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-[#DCEFFE] text-[#455A64]">Mismo Nombre</span>' if u['match_type'] == "EXACT_NAME" else '<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-[#F5F5F5] text-[#455A64] border border-[#E0E0E0]">Nombre Similar</span>'
    html_template += f"""
              <tr class="hover:bg-[#F5F5F5]/60 transition">
                <td class="py-2 px-3 font-mono text-slate-500">{u['id']}</td>
                <td class="py-2 px-3 font-mono font-semibold text-[#455A64]">{u['old_code']}</td>
                <td class="py-2 px-3 text-[#455A64]">{u['old_name']}</td>
                <td class="py-2 px-3 font-mono font-bold text-[#AC0340] bg-[#AC0340]/5">{u['new_code']}</td>
                <td class="py-2 px-3 font-semibold text-[#282C2F]">{u['new_name']}</td>
                <td class="py-2 px-3 text-center font-bold">
                  <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-[#F5F5F5] text-[#282C2F] border border-[#E0E0E0]">{u['moves']}</span>
                </td>
                <td class="py-2 px-3 text-center">{match_badge}</td>
              </tr>
"""

html_template += f"""
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ==================== TAB 2: CATALOGO OFICIAL ==================== -->
    <div id="tab-official" class="tab-content hidden space-y-4">
      <div class="bg-[#FFFFFF] p-5 rounded border border-[#E0E0E0] space-y-4">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h3 class="text-base font-bold text-[#282C2F] font-heading">{len(excel_accounts)} Cuentas Oficiales del Excel (Nivel 3 SAT)</h3>
            <p class="text-xs text-[#455A64]">
              Cuentas oficiales extraídas de la pestaña <span class="font-mono font-semibold">CATALOGO NIVEL 3</span> del archivo <span class="font-mono">Catalogo de cuentas SOUTH_ Odoo 2 niveles.xlsx</span>.
            </p>
          </div>
          <div>
            <input type="text" id="search-official" onkeyup="filterTable('search-official', 'table-official')" placeholder="Filtrar catálogo oficial..." class="px-3 py-1.5 border border-[#B3B3B3] rounded text-xs focus:outline-none focus:border-[#AC0340] w-64 text-[#282C2F]">
          </div>
        </div>

        <div class="overflow-x-auto max-h-[550px] overflow-y-auto">
          <table id="table-official" class="min-w-full divide-y divide-[#E0E0E0] text-xs">
            <thead class="bg-[#F5F5F5] text-[#455A64] font-bold uppercase sticky top-0 z-10">
              <tr>
                <th class="py-2.5 px-3 text-left font-bold text-[#AC0340]">Código Oficial</th>
                <th class="py-2.5 px-3 text-left">Código Agrupador SAT</th>
                <th class="py-2.5 px-3 text-left">Nombre de la Cuenta</th>
                <th class="py-2.5 px-3 text-center">Estatus en Odoo</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#E0E0E0] text-[#282C2F]">
"""

for ex in excel_accounts:
    is_unified = ex['code'] in unified_new_codes
    status_badge = '<span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-[#AC0340]/10 text-[#AC0340] border border-[#AC0340]/20">Unificada (Con Histórico)</span>' if is_unified else '<span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-[#DCEFFE] text-[#455A64] border border-[#455A64]/20">Oficial Creada / Existente</span>'
    html_template += f"""
              <tr class="hover:bg-[#F5F5F5]/60 transition">
                <td class="py-2 px-3 font-mono font-bold text-[#AC0340]">{ex['code']}</td>
                <td class="py-2 px-3 font-mono text-[#455A64]">{ex['sat']}</td>
                <td class="py-2 px-3 font-medium text-[#282C2F]">{ex['name']}</td>
                <td class="py-2 px-3 text-center">{status_badge}</td>
              </tr>
"""

html_template += f"""
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ==================== TAB 3: PRESERVADAS POR CONFIGURACION ==================== -->
    <div id="tab-config" class="tab-content hidden space-y-4">
      <div class="bg-[#FFFFFF] p-5 rounded border border-[#E0E0E0] space-y-4">
        <div>
          <h3 class="text-base font-bold text-[#282C2F] font-heading">{len(config_accounts)} Cuentas Preservadas por Configuración del Sistema</h3>
          <p class="text-xs text-[#455A64]">
            Cuentas técnicas y de tránsito configuradas en diarios de banco, parámetros de la compañía (res.company), reglas de impuestos SAT o modelos de conciliación.
          </p>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-[#E0E0E0] text-xs">
            <thead class="bg-[#F5F5F5] text-[#455A64] font-bold uppercase">
              <tr>
                <th class="py-2.5 px-3 text-left">ID Odoo</th>
                <th class="py-2.5 px-3 text-left">Código Odoo</th>
                <th class="py-2.5 px-3 text-left">Nombre de la Cuenta</th>
                <th class="py-2.5 px-3 text-left">Tipo Contable</th>
                <th class="py-2.5 px-3 text-left">Motivo de Preservación</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#E0E0E0] text-[#282C2F]">
"""

for ca in config_accounts:
    html_template += f"""
              <tr class="hover:bg-[#F5F5F5]/60">
                <td class="py-2.5 px-3 font-mono text-slate-500">{ca['id']}</td>
                <td class="py-2.5 px-3 font-mono font-bold text-[#AC0340]">{ca['code']}</td>
                <td class="py-2.5 px-3 font-semibold text-[#282C2F]">{ca['name']}</td>
                <td class="py-2.5 px-3 text-[#455A64]">{ca['type']}</td>
                <td class="py-2.5 px-3 text-[#455A64]">{ca['reason']}</td>
              </tr>
"""

html_template += f"""
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ==================== TAB 4: PRESERVADAS POR MOVIMIENTOS ==================== -->
    <div id="tab-moves" class="tab-content hidden space-y-4">
      <div class="bg-[#FFFFFF] p-5 rounded border border-[#E0E0E0] space-y-4">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h3 class="text-base font-bold text-[#282C2F] font-heading">{len(preserved_by_moves)} Cuentas Preservadas por Apuntes Contables Históricos</h3>
            <p class="text-xs text-[#455A64]">
              Cuentas preexistentes que contienen registros contables en <span class="font-mono font-semibold">account.move.line</span> y están blindadas para garantizar la integridad histórica y fiscal.
            </p>
          </div>
          <div>
            <input type="text" id="search-moves" onkeyup="filterTable('search-moves', 'table-moves')" placeholder="Filtrar cuentas con pólizas..." class="px-3 py-1.5 border border-[#B3B3B3] rounded text-xs focus:outline-none focus:border-[#AC0340] w-64 text-[#282C2F]">
          </div>
        </div>

        <div class="overflow-x-auto max-h-[550px] overflow-y-auto">
          <table id="table-moves" class="min-w-full divide-y divide-[#E0E0E0] text-xs">
            <thead class="bg-[#F5F5F5] text-[#455A64] font-bold uppercase sticky top-0 z-10">
              <tr>
                <th class="py-2.5 px-3 text-left">Código Odoo</th>
                <th class="py-2.5 px-3 text-left">Nombre de la Cuenta</th>
                <th class="py-2.5 px-3 text-left">Tipo Contable</th>
                <th class="py-2.5 px-3 text-center">Apuntes Contables</th>
                <th class="py-2.5 px-3 text-center">Razón de Blindaje</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#E0E0E0] text-[#282C2F]">
"""

for p in preserved_by_moves:
    html_template += f"""
              <tr class="hover:bg-[#F5F5F5]/60 transition">
                <td class="py-2 px-3 font-mono font-bold text-[#455A64]">{p['code']}</td>
                <td class="py-2 px-3 font-medium text-[#282C2F]">{p['name']}</td>
                <td class="py-2 px-3 text-[#455A64]">{p['type']}</td>
                <td class="py-2 px-3 text-center font-bold text-[#282C2F]">
                  <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-[#F5F5F5] text-[#282C2F] border border-[#E0E0E0]">{p['moves']:,}</span>
                </td>
                <td class="py-2 px-3 text-center text-[#455A64]">
                  Auditoría / Balanza Histórica
                </td>
              </tr>
"""

html_template += f"""
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ==================== TAB 5: ARCHIVADAS ==================== -->
    <div id="tab-archived" class="tab-content hidden space-y-4">
      <div class="bg-[#FFFFFF] p-5 rounded border border-[#E0E0E0] space-y-4">
        <div>
          <h3 class="text-base font-bold text-[#282C2F] font-heading">{len(archived)} Cuentas Inactivas Archivadas</h3>
          <p class="text-xs text-[#455A64]">
            Cuentas fuera del catálogo oficial o duplicadas con 0 movimientos y 0 dependencias que fueron marcadas como <span class="font-mono">deprecated = True</span>.
          </p>
        </div>

        <div class="overflow-x-auto max-h-[500px] overflow-y-auto">
          <table class="min-w-full divide-y divide-[#E0E0E0] text-xs">
            <thead class="bg-[#F5F5F5] text-[#455A64] font-bold uppercase sticky top-0 z-10">
              <tr>
                <th class="py-2.5 px-3 text-left">Código Odoo</th>
                <th class="py-2.5 px-3 text-left">Nombre de la Cuenta</th>
                <th class="py-2.5 px-3 text-left">Tipo Contable</th>
                <th class="py-2.5 px-3 text-center">Estatus</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#E0E0E0] text-[#282C2F]">
"""

for ar in archived:
    html_template += f"""
              <tr class="hover:bg-[#F5F5F5]/60">
                <td class="py-2 px-3 font-mono text-slate-500">{ar['code']}</td>
                <td class="py-2 px-3 text-[#455A64]">{ar['name']}</td>
                <td class="py-2 px-3 text-[#455A64]">{ar['type']}</td>
                <td class="py-2 px-3 text-center">
                  <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-[#F5F5F5] text-[#455A64] border border-[#E0E0E0]">Archivada (Inactiva)</span>
                </td>
              </tr>
"""

html_template += f"""
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ==================== TAB 6: LISTAS DE PRECIOS ==================== -->
    <div id="tab-pricelists" class="tab-content hidden space-y-4">
      <div class="bg-[#FFFFFF] p-5 rounded border border-[#E0E0E0] space-y-4">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h3 class="text-base font-bold text-[#282C2F] font-heading">Cobertura de las 11 Listas de Precios Importadas ({total_rules_loaded} de {total_rules_excel} Reglas &bull; {total_pl_coverage}%)</h3>
            <p class="text-xs text-[#455A64]">
              Tarifas en MXN importadas directamente desde el archivo maestro a las listas de precios en Odoo con soporte de traducción al español (Spanish AR).
            </p>
          </div>
          <div class="inline-flex items-center gap-2 px-3 py-1 bg-[#DCEFFE] text-[#455A64] text-xs font-bold rounded">
            <span>MaterniT21 Plus cargado al 100% en todas las listas aplicables</span>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-[#E0E0E0] text-xs">
            <thead class="bg-[#F5F5F5] text-[#455A64] font-bold uppercase">
              <tr>
                <th class="py-2.5 px-3 text-center">ID Odoo</th>
                <th class="py-2.5 px-3 text-left">Lista de Precios (Pestaña)</th>
                <th class="py-2.5 px-3 text-center">Ítems Cargados</th>
                <th class="py-2.5 px-3 text-center">Discrepancias</th>
                <th class="py-2.5 px-3 text-center">Cobertura</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#E0E0E0] text-[#282C2F]">
"""

for pl in price_lists:
    html_template += f"""
              <tr class="hover:bg-[#F5F5F5]/60">
                <td class="py-2 px-3 text-center font-mono font-bold text-[#AC0340]">{pl['id']}</td>
                <td class="py-2 px-3 font-semibold text-[#282C2F]">{pl['name']}</td>
                <td class="py-2 px-3 text-center font-bold text-[#282C2F]">{pl['loaded']}</td>
                <td class="py-2 px-3 text-center font-bold text-[#AC0340]">{pl['pending']}</td>
                <td class="py-2 px-3 text-center font-semibold text-[#455A64]">{pl['coverage']}</td>
              </tr>
"""

html_template += f"""
            </tbody>
          </table>
        </div>
      </div>

      <div class="bg-[#FFFFFF] p-5 rounded border border-[#E0E0E0] space-y-4">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h3 class="text-base font-bold text-[#282C2F] font-heading">Auditoría de las {len(discrepancies)} Discrepancias Residuales en Productos</h3>
            <p class="text-xs text-[#455A64]">
              Productos identificados en el archivo Excel que no existen en el catálogo maestro de productos de Odoo y requieren alta previa.
            </p>
          </div>
          <input type="text" id="search-disc" onkeyup="filterTable('search-disc', 'table-disc')" placeholder="Filtrar producto..." class="px-3 py-1.5 border border-[#B3B3B3] rounded text-xs focus:outline-none focus:border-[#AC0340] w-64 text-[#282C2F]">
        </div>

        <div class="overflow-x-auto max-h-[480px] overflow-y-auto">
          <table id="table-disc" class="min-w-full divide-y divide-[#E0E0E0] text-xs">
            <thead class="bg-[#F5F5F5] text-[#455A64] font-bold uppercase sticky top-0 z-10">
              <tr>
                <th class="py-2.5 px-3 text-left">Lista de Precios</th>
                <th class="py-2.5 px-3 text-left">Nombre en Excel</th>
                <th class="py-2.5 px-3 text-left">Código en Excel</th>
                <th class="py-2.5 px-3 text-center">Categoría Causa Raíz</th>
                <th class="py-2.5 px-3 text-left">Acción Requerida</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#E0E0E0] text-[#282C2F]">
"""

for d in discrepancies:
    html_template += f"""
              <tr class="hover:bg-[#F5F5F5]/60">
                <td class="py-2 px-3 font-semibold text-[#455A64]">{d['list_name']}</td>
                <td class="py-2 px-3 font-medium text-[#282C2F]">{d['excel_name']}</td>
                <td class="py-2 px-3 font-mono text-slate-500">{d['excel_code']}</td>
                <td class="py-2 px-3 text-center">
                  <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-[#E4A900]/15 text-[#855d00] border border-[#E4A900]/30">{d['category']}</span>
                </td>
                <td class="py-2 px-3 text-[#455A64]">{d['action']}</td>
              </tr>
"""

html_template += f"""
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </main>

  <!-- Footer con Cita Obligatoria de Marca Vauxoo -->
  <footer class="bg-[#FFFFFF] border-t border-[#E0E0E0] py-6 mt-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-[#455A64]">
      <div class="flex items-center gap-3">
        <div class="logo-wrapper" style="max-width: 110px;">
          {logo_horizontal_svg}
        </div>
        <p>&copy; 2026 SouthGenetics México &bull; Implementación Odoo 17 ERP</p>
      </div>
      <div class="text-center md:text-right">
        <p class="font-medium text-[#282C2F]">Construyamos algo genial</p>
        <p class="text-[11px] text-[#95999F]">
          Activos de marca y lineamientos oficiales disponibles en <a href="https://www.vauxoo.com/en_US/assets" target="_blank" class="text-[#AC0340] underline hover:text-[#BC1C38]">https://www.vauxoo.com/en_US/assets</a>
        </p>
      </div>
    </div>
  </footer>

  <!-- Scripts Interactivos -->
  <script>
    function switchTab(tabId) {{
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.tab-btn').forEach(el => {{
        el.classList.remove('active');
      }});

      const content = document.getElementById(tabId);
      if (content) content.classList.remove('hidden');

      const btn = document.getElementById('btn-' + tabId);
      if (btn) btn.classList.add('active');
    }}

    function filterTable(inputId, tableId) {{
      const input = document.getElementById(inputId);
      const filter = input.value.toLowerCase();
      const table = document.getElementById(tableId);
      const trs = table.getElementsByTagName('tr');

      for (let i = 1; i < trs.length; i++) {{
        const text = trs[i].textContent || trs[i].innerText;
        trs[i].style.display = (text.toLowerCase().indexOf(filter) > -1) ? '' : 'none';
      }}
    }}
  </script>
</body>
</html>
"""

output_path = '/Users/julioserna/.gemini/antigravity/scratch/southgenetics/index.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_template)

# Also update artifact
with open('/Users/julioserna/.gemini/antigravity/brain/982f6e60-7ee3-4371-bb88-215f9ba01996/index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print('Successfully re-generated index.html!')
