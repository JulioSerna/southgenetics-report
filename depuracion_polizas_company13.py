"""
Script de Trazabilidad: Depuración de pólizas y saldos de prueba en Odoo
Compañía: SOUTHGENETICS MEXICO SA DE CV (ID: 13)
Instancia: southgenetics-staging (https://southgenetics-staging-38644840.dev.odoo.com/)
Fecha de ejecución: 2026-10-06 / 2026-10-07

Este script documenta la lógica y el código ejecutado a través del ORM de Odoo
(mediante MCP Tools / ir.actions.server temporal) para garantizar integridad referencial
y trazabilidad para replicación futura en Producción.
"""

# ==============================================================================
# 1. PARÁMETROS DE LA OPERACIÓN
# ==============================================================================
COMPANY_ID = 13
COMPANY_NAME = "SOUTHGENETICS MEXICO SA DE CV"

# ==============================================================================
# 2. ANÁLISIS PREVIO DE REGISTROS (ANTES DE LA DEPURACIÓN)
# ==============================================================================
# Total account.move iniciales: 3,139
# Desglose inicial:
# - account.bank.statement.line: 3,110 (generan 3,110 account.move vinculados)
# - account.payment: 2 (PBBVA/2026/00001, PBBVA/2026/00002 -> generan 2 account.move vinculados)
# - Facturas de cliente (out_invoice): 6
#     * INV/2026/00002 (posted, conciliada con pago PBBVA/2026/00002)
#     * INV/2026/00001 (posted)
#     * INV/2024/00004 (posted, timbrada con CFDI prueba)
#     * INV/2024/00003 (posted, timbrada con CFDI prueba)
#     * INV/2024/00002 (cancel)
#     * INV/2024/00001 (cancel)
# - Facturas de proveedor (in_invoice): 3
#     * BILL/2026/10/0003 (posted, conciliada con pago PBBVA/2026/00001)
#     * BILL/2026/10/0002 (posted)
#     * BILL/2026/10/0001 (posted)
# - Asientos varios / Ajustes / Saldos iniciales (entry): 18
#     * MISC/2026/10/0002, MISC/2026/10/0001 (provisiones compra)
#     * EXCH/2026/10/0001 (diferencia cambiaria del pago 1)
#     * CBMX/2026/10/0001 (efectivamente cobrado base efectivo)
#     * MISC/2026/01/0001 (ajuste SI bancos)
#     * SI/2025/12/0001, SI/2025/12/0002, SI/2025/12/0003 (saldos iniciales 2025)
#     * SI/2025/10/0001, SI/2025/10/0002, SI/2025/10/0003 (cancelados)
#     * MISC/2025/10/0001 (cancelado)
#     * MISC/2024/12/0001 (posted)
#     * Borradores automáticos de declaración de impuestos (4): 2023-11, 2024-08, 2024-10, 2026-09
#     * BNK1/2025/00001 (draft)
# - Conciliaciones activas:
#     * 3 account.partial.reconcile (IDs: 53338, 53339, 53340)
#     * 2 account.full.reconcile (IDs: 39892, 39893)

# ==============================================================================
# 3. LÓGICA DE PURGA EJECUTADA PASO A PASO EN EL SERVIDOR ODOO
# ==============================================================================

def execute_depuration(env):
    company_id = 13

    # PASO 1: Desconciliación de pagos y facturas (Romper Full y Partial Reconciles)
    env.cr.execute("DELETE FROM account_partial_reconcile WHERE company_id = %s", [company_id])
    env.cr.execute("DELETE FROM account_full_reconcile WHERE id IN (39892, 39893)")
    env.cr.execute("""
        UPDATE account_move_line 
        SET full_reconcile_id = NULL, matching_number = NULL, reconciled = FALSE 
        WHERE company_id = %s
    """, [company_id])
    env.invalidate_all()

    # PASO 2: Cancelación y eliminación de Pagos (account.payment)
    payments = env['account.payment'].search([('company_id', '=', company_id)])
    if payments:
        payments.action_draft()
        payments.unlink()

    # PASO 3: Manejo de restricciones CFDI en facturas mexicanas timbradas de prueba
    # Se desvinculan los estados de CFDI de prueba y los adjuntos XML/PDF protegidos
    env.cr.execute("""
        UPDATE account_move 
        SET l10n_mx_edi_cfdi_state = NULL, 
            l10n_mx_edi_cfdi_sat_state = NULL, 
            l10n_mx_edi_cfdi_uuid = NULL,
            l10n_mx_edi_cfdi_attachment_id = NULL
        WHERE company_id = %s AND id IN (162889, 162920)
    """, [company_id])
    
    env.cr.execute("""
        DELETE FROM ir_attachment 
        WHERE id IN (32501, 32502, 32505, 32506)
    """)
    env.invalidate_all()

    # PASO 4: Eliminación de asientos no bancarios (Facturas cliente/proveedor y varios)
    moves_non_stmt = env['account.move'].search([
        ('company_id', '=', company_id),
        ('statement_line_id', '=', False),
    ])
    posted_moves = moves_non_stmt.filtered(lambda m: m.state == 'posted')
    if posted_moves:
        posted_moves.button_draft()
    moves_non_stmt.unlink()

    # PASO 5: Eliminación por lotes de Líneas de Extracto Bancario (account.bank.statement.line)
    # Lote seguro de 400 registros para evitar timeouts de proxy/gunicorn.
    batch_size = 400
    while True:
        lines = env['account.bank.statement.line'].search([('company_id', '=', company_id)], limit=batch_size)
        if not lines:
            break
        lines.move_id.button_draft()
        lines.unlink()

    env.invalidate_all()
    print("Depuración completada exitosamente para la compañía 13.")
