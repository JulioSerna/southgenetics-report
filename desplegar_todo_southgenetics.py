#!/usr/bin/env python3
"""
Orquestador Maestro para aplicar todo el despliegue validado de SouthGenetics México (Company ID: 13)
en cualquier nuevo Staging o en Producción, seguido de la generación del reporte cuenta por cuenta.

Uso:
  python3 desplegar_todo_southgenetics.py [perfil_mcp]
"""
import subprocess
import sys

PROFILE = sys.argv[1] if len(sys.argv) > 1 else 'southgenetics-staging'

STEPS = [
    ("1. Depuración de pólizas y extractos de prueba", ["python3", "ejecutar_depuracion.py"]),
    ("2. Depuración, unificación (78) y alta (84) del Plan Contable (162 Drive + 9 Técnicas, 80 CxC/CxP eliminadas)", ["python3", "estructurar_cuentas.py", PROFILE]),
    ("3. Alta de 4 Modelos y 17 Activos Fijos ($1.00 residual)", ["python3", "ejecutar_activos_fijos.py"]),
    ("4. Alta de 11 Listas de Precios en MXN y 286 Reglas (incluyendo Afirma GSC)", ["python3", "cargar_listas_precios_final.py"]),
    ("5. Alta de 44 Costos de Proveedor en USD (Southgenetics LTDA en secuencia 1)", ["python3", "ejecutar_supplierinfo.py"]),
    ("6. Sincronización de 45 Proveedores y 19 Clientes (con RFC, Régimen Fiscal y Cuentas 105.01.01 / 201.01.01)", ["python3", "sync_contactos_robusto.py"]),
    ("7. Asignación de Listas de Precios a los 15 Clientes de México", ["python3", "ejecutar_asignacion_listas.py"]),
    ("8. Auditoría integral de verificación", ["python3", "auditar_todo.py"]),
    ("9. Generación del Reporte HTML Vauxoo (con desglose cuenta por cuenta)", ["python3", "generate_html_report_vauxoo.py"]),
]

if __name__ == '__main__':
    print(f"=== INICIANDO DESPLIEGUE MAESTRO SOUTHGENETICS MÉXICO (Perfil: {PROFILE}) ===")
    for title, cmd in STEPS:
        print(f"\n---> {title}")
        res = subprocess.run(cmd)
        if res.returncode != 0:
            print(f"ERROR en el paso: {title}")
            sys.exit(res.returncode)
    print("\n=== DESPLIEGUE Y REPORTE COMPLETADOS EXITOSAMENTE ===")
