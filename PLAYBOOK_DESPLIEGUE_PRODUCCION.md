# Playbook de Despliegue en Producción: SouthGenetics México (ID: 13)

**Versión:** 1.0  
**Fecha de Validación en Staging:** 6 de Octubre de 2026  
**Ambiente de Validación:** `southgenetics-staging-38644840.dev.odoo.com`  
**Compañía Objetivo:** `SOUTHGENETICS MEXICO SA DE CV` (ID: 13)  
**Autor:** Julio Serna (Vauxoo)  

---

## 📌 Propósito y Filosofía del Playbook
Este documento es la **guía maestra paso a paso** para ejecutar el Go-Live en la base de datos de **Producción**.  
Recopila **todas las lecciones aprendidas, errores sorteados y correcciones finas** obtenidas durante las pruebas en Staging, garantizando que el despliegue en Producción sea 100% determinista, rápido, sin ensayo y error, y protegiendo de forma absoluta la integridad multicompañía de las demás filiales del grupo (Chile, Uruguay, Argentina, Colombia, etc.).

---

## 🚨 Bitácora de Errores en Staging y su Solución Definitiva (Lessons Learned)

A continuación se detallan los tropiezos técnicos identificados en Staging y la solución exacta probada que debe aplicarse en Producción:

### 1. Proveedor Predeterminado en Compras (`product.supplierinfo`): La regla de "México de Primero"
* **Problema encontrado:**
  * Al importar los costos de proveedor (`COSTO TEST`), asignar `sequence = 1` no garantiza que México quede de primero si ya existía otro proveedor global con `sequence = 1` (Odoo desempataba por fecha de creación `id asc` y mostraba primero al proveedor viejo).
  * Si se aumentaba numéricamente la secuencia a `2` o `3`, Odoo colocaba a México al final de la lista, priorizando al proveedor extranjero.
* **Solución definitiva probada:**
  1. Desplazar masivamente cualquier proveedor preexistente del producto a **`sequence = 2`** (o superior).
  2. Asignar al proveedor de México (`Southgenetics LTDA`, ID `43633`, `company_id = 13`) estrictamente **`sequence = 1`**.
  * **Efecto garantizado:** En el 100% de los casos México queda en **Posición 1 (Primero)** tanto en la vista de producto como en el motor de abastecimiento MTO/Buy.

### 2. Depuración Contable: Bloqueos de Desconciliación y Adjuntos CFDI
* **Problema encontrado:**
  * Intentar eliminar (`unlink`) pólizas directamente arroja errores de llaves foráneas o apuntes conciliados.
  * Facturas históricas de prueba con timbrado CFDI o intentos de timbrado tienen adjuntos `ir.attachment` de tipo XML/EDI y estatus `sent` que bloquean el método `button_draft()`.
* **Solución definitiva probada:**
  1. Romper previamente las conciliaciones parciales (`account.partial.reconcile`) y totales (`account.full.reconcile`).
  2. Limpiar/desvincular los adjuntos EDI y marcas de timbrado en facturas antes de llamar `button_draft()`.
  3. Desconciliar y borrar líneas de extractos bancarios (`account.bank.statement.line`) en lotes controlados (lotes de 400).
  4. Convertir a borrador y eliminar en cascada.
  * **Garantía multicompañía:** El filtro `company_id = 13` debe aplicarse de forma estricta en cada consulta para no tocar un solo asiento de las filiales.

### 3. Cuentas Contables de Activos Fijos: Colisión de Códigos
* **Problema encontrado:**
  * Las plantillas sugerían cuentas de catálogo SAT estándar (`153.01.01`, `155.01.01`, `601.34.01`), pero en la base de datos real dichas cuentas ya estaban ocupadas por otros conceptos (ej. `155.01.01` era Mobiliario, `601.34.01` era Servicios contables).
* **Solución definitiva probada:**
  * Se utilizaron las cuentas reales y homologadas de la compañía 13:
    * **Cómputo:** Activo `156.01.01`, Depr. Acumulada `171.05.01`, Gasto `601.99.05`.
    * **Mobiliario:** Activo `155.01.01`, Depr. Acumulada `171.04.01`, Gasto `601.99.04`.
    * **Transporte:** Activo `154.01.01`, Depr. Acumulada `154.02.01`, Gasto `601.33.01`.
    * **Laboratorio:** Activo `155.02.01`, Depr. Acumulada `171.02.01`, Gasto `601.99.02`.
  * Se fijó **$1.00 MXN de valor residual** para preservar la evidencia fiscal de los activos 100% depreciados sin generar amortizaciones futuras indebidas.

### 4. Productos Archivados en Listas de Precios
* **Problema encontrado:**
  * Productos como `Afirma GSC` (ID 632) estaban archivados (`active = False`), lo que provocaba que las reglas de lista de precios no se aplicaran o fallaran en la búsqueda.
* **Solución definitiva probada:**
  * Reactivar previamente (`active = True`) cualquier producto clave del catálogo médico antes de importar las reglas de precios.

---

## 📋 Secuencia Maestra de Ejecución en Producción

El despliegue en Producción debe realizarse en el siguiente orden secuencial estricto:

```
[Fase 1: Pre-chequeo y Respaldo]
               │
               ▼
[Fase 2: Depuración Contable Limpia (Ceros)]
               │
               ▼
[Fase 3: Estructura Contable Oficial (SAT 402)]
               │
               ▼
[Fase 4: Carga de Modelos y Cédulas de Activos Fijos]
               │
               ▼
[Fase 5: Actualización de Listas de Precios de Venta V2 (11 Listas)]
               │
               ▼
[Fase 6: Carga de Costos de Proveedor (SupplierInfo con México de Primero)]
               │
               ▼
[Fase 7: Verificación Final y Auditoría de Integridad]
```

---

## 🛠️ Detalle Paso a Paso de Ejecución

### PASO 1: Pre-chequeo de Seguridad y Respaldo
1. Confirmar perfil Odoo de producción en la CLI:
   ```bash
   odoo-mcp search-read --profile southgenetics-production --model res.company --domain "[('id', '=', 13)]" --fields "name"
   ```
2. Verificar que el ID de la compañía México coincida con `13` (`SOUTHGENETICS MEXICO SA DE CV`).

---

### PASO 2: Depuración Contable (Dejar México en Ceros)
* **Objetivo:** Eliminar asientos previos de prueba y dejar la contabilidad lista para los saldos iniciales limpios al 30 de noviembre.
* **Script de Ejecución:** [`depuracion_polizas_company13.py`](./depuracion_polizas_company13.py)
* **Acciones automáticas:**
  1. Rompe conciliaciones en diarios de México.
  2. Desvincula adjuntos EDI en facturas cliente/proveedor.
  3. Revierte y elimina extractos bancarios BBVA.
  4. Convierte a borrador y elimina pólizas `out_invoice`, `in_invoice` y `entry`.
* **Criterio de Aceptación:**
  ```text
  account.move (company_id=13): 0 registros
  account.payment (company_id=13): 0 registros
  account.bank.statement.line (company_id=13): 0 registros
  ```

---

### PASO 3: Validación del Catálogo Contable (Estructura SAT)
* **Objetivo:** Asegurar que las cuentas de devoluciones se encuentren bajo el código agrupador SAT **402** y no 401.
* **Cuentas requeridas activas en company 13:**
  * `401.01.01` a `401.01.06`: Cuentas de Ingresos (Oncología, Otros test, Urología, etc.).
  * `402.01.01` a `402.01.06`: Devoluciones correspondientes (Dev Oncología, Dev Otros test, etc.).

---

### PASO 4: Carga de Modelos y Cédulas de Activos Fijos
* **Objetivo:** Dar de alta los 4 modelos de depreciación y los 17 activos fijos con sus curvas históricas y valor residual de $1 MXN.
* **Archivos Insumo:**
  * [`06_Modelos_Activos_Fijos.csv`](./06_Modelos_Activos_Fijos.csv)
  * [`06_Activos_Fijos_y_Depreciacion.csv`](./06_Activos_Fijos_y_Depreciacion.csv)
* **Script de Ejecución:** [`cargar_activos_fijos.py`](./cargar_activos_fijos.py)
* **Criterio de Aceptación:**
  * 4 Modelos en `account.asset` (`state = 'model'`).
  * 17 Activos en `account.asset` (`state = 'draft'`).
  * Valor original total: `$217,337.65 MXN`.
  * Depreciación histórica acumulada: `$143,114.41 MXN`.
  * Valor residual total: `$17.00 MXN`.

---

### PASO 5: Actualización de Listas de Precios de Venta en MXN (V2.0)
* **Objetivo:** Sincronizar las 11 listas de precios de clientes con el archivo oficial del Drive.
* **Archivo Insumo:** [`V2.0_lista_de_precios.xlsx`](./V2.0_lista_de_precios.xlsx)
* **Script de Ejecución:** [`actualizar_listas_precios_v2.py`](./actualizar_listas_precios_v2.py)
* **Puntos Críticos:**
  * Reactivación de producto `Afirma GSC` (ID 632) si se encuentra archivado.
  * Inserción de las 18 reglas clave faltantes (`4KSCORE`, `Mir-THYpe(R)`, `DecisionDx-UM`, `Afirma GSC`).
* **Criterio de Aceptación:**
  * 286 reglas activas en `product.pricelist.item` vinculadas a la compañía 13.

---

### PASO 6: Carga de Costos de Proveedor (`product.supplierinfo` - Pestaña COSTO TEST)
* **Objetivo:** Cargar costos en USD con proveedor `Southgenetics LTDA` asegurando que México quede **DE PRIMERO (Posición 1)** en todos los productos.
* **Script de Ejecución:** [`cargar_supplierinfo_costos.py`](./cargar_supplierinfo_costos.py)
* **Regla Inquebrantable:**
  1. Proveedor de México (`Southgenetics LTDA`, ID 43633) asignado con **`sequence = 1`** y `company_id = 13`.
  2. Proveedores preexistentes desplazados a **`sequence = 2`** o superior.
* **Criterio de Aceptación:**
  * 44 registros de costos en USD para la compañía 13.
  * En el 100% de los productos con múltiples proveedores, la línea de México aparece en la Posición 1.

---

### PASO 7: Script de Auditoría Automatizada Post-Despliegue
Al concluir los 6 pasos anteriores, ejecutar el script de verificación integral:
```bash
python3 /Users/julioserna/.gemini/antigravity/scratch/southgenetics/verificar_despliegue_produccion.py
```
Este script valida automáticamente:
- [x] Que `account.move` para company 13 tenga 0 registros.
- [x] Que existan los 4 modelos y 17 activos fijos en borrador con montos cuadrados al centavo.
- [x] Que existan las 286 reglas en las 11 listas de precios de MXN.
- [x] Que en los 44 productos de México el proveedor Southgenetics LTDA esté en la Posición 1 (`sequence = 1`).

---

## 📁 Inventario de Archivos Entregables en el Repositorio

| Archivo | Tipo | Función en Producción |
|:---|:---:|:---|
| [`PLAYBOOK_DESPLIEGUE_PRODUCCION.md`](./PLAYBOOK_DESPLIEGUE_PRODUCCION.md) | Documento | Guía maestra y procedimiento operativo. |
| [`depuracion_polizas_company13.py`](./depuracion_polizas_company13.py) | Script | Borrado masivo y seguro de asientos para dejar contabilidad en ceros. |
| [`cargar_activos_fijos.py`](./cargar_activos_fijos.py) | Script | Alta de modelos y los 17 activos fijos en Odoo. |
| [`actualizar_listas_precios_v2.py`](./actualizar_listas_precios_v2.py) | Script | Carga de las 286 reglas en las 11 listas de precios MXN. |
| [`cargar_supplierinfo_costos.py`](./cargar_supplierinfo_costos.py) | Script | Carga de los 44 costos de proveedor con México de primero. |
| [`resultado_depuracion.json`](./resultado_depuracion.json) | Auditoría | Log estructurado de registros eliminados en staging. |
| [`resultado_activos_fijos.json`](./resultado_activos_fijos.json) | Auditoría | Log de activos creados con sus montos históricos. |
| [`reporte_listas_y_costos_v2.json`](./reporte_listas_y_costos_v2.json) | Auditoría | Log completo de listas de precios y supplierinfo. |
| [`V2.0_lista_de_precios.xlsx`](./V2.0_lista_de_precios.xlsx) | Insumo | Archivo Excel fuente del Drive. |
| [`06_Activos_Fijos_y_Depreciacion.csv`](./06_Activos_Fijos_y_Depreciacion.csv) | Insumo | Cédula oficial de activos fijos. |
| [`06_Modelos_Activos_Fijos.csv`](./06_Modelos_Activos_Fijos.csv) | Insumo | Definición de modelos de depreciación. |
