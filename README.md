# Predictivo de Turbocompresores · GPM

Tablero web (GitHub Pages) del seguimiento predictivo de los turbocompresores TC1 (Solar Mars 100) de PC Tratayén y PC Salliqueló. Ordenado por tema, como los informes predictivos:

- **Condición operativa (SCADA):** histórico HistoryView por sistema (general, T5, lubricación, seal gas, buffer air, admisión, vibraciones del motor, compresor HPC). Registros horarios filtrados a operación (Ngp > 5 %) y agregados por día.
- **Relevamiento de vibraciones:** mediciones con equipo portátil (planilla VIBR TTCC) contra alarma y paro.
- **Análisis de aceite:** muestras del laboratorio YPF AUCTOR contra valores Mín/Máx del lubricante, y ensayos de oxidación RPVOT, RULER y MPC.
- **Hallazgos y seguimiento.**

## Archivos
- `index.html`: el tablero. Lee vibraciones, aceite, oxidación y hallazgos del Google Sheets (Apps Script).
- `embebido.js`: copia de respaldo de la base; se usa si la URL del Apps Script falla o está vacía (lo indica el pie).
- `Code.gs`: Apps Script que expone el Google Sheets como JSON.
- `BASE_PREDICTIVO_TC.xlsx`: base para crear el Google Sheets (pestañas VIBRACIONES, LIMITES_VIB, ACEITE, LIMITES_ACEITE, OXIDACION, HALLAZGOS, AYUDA).
- `scada_<período>.js`: agregados diarios de la condición operativa, uno por período (p. ej. `scada_2026-S1.js`).
- `build_scada.py`: genera el archivo de un período a partir de los Excel de HistoryView (hoja `Datos`).

## Puesta en marcha del Google Sheets
1. Subir `BASE_PREDICTIVO_TC.xlsx` a Drive y guardarlo como Hojas de cálculo de Google.
2. Extensiones > Apps Script: pegar `Code.gs` e implementarlo como aplicación web (Ejecutar como: Yo · Acceso: Cualquier usuario). Copiar la URL `/exec`.
3. En `index.html`, completar `const FUENTE = { appsScriptUrl: "https://script.google.com/macros/s/.../exec" };`.
4. GitHub: Settings > Pages > Deploy from branch `main` / root.

## Carga
- **VIBRACIONES:** una fila por medición y planta (TTY / SQL), todo en µm.
- **ACEITE:** una fila por muestra; diagnóstico y criticidad al menos en la última de cada planta.
- **OXIDACION:** una fila por informe RPVOT / RULER / MPC.
- **HALLAZGOS:** solo lo que requiere acción. El tablero muestra los que no están `Cerrado`.

## Cargar un período nuevo de SCADA
```
python3 build_scada.py 2026-S2 TC_Tratayen_1226.xlsx TC_Salliquelo_1226.xlsx 2026-07-01 2027-01-01
```
Subir el `scada_2026-S2.js` generado, agregar su `<script src>` en `index.html` y el período en `PERIODOS`.

## Criterios
- Semáforo: Atención desde el 60 % del valor de alarma o con hallazgo abierto (constante `UMBRAL`).
- Termocupla T5 fuera de servicio: lectura < 50 % de la mediana del resto durante 24 h o más en operación.
- Relevamiento de vibraciones: todo en µm. Salliqueló usa la Alarma/Paro de Tratayén (mismo modelo; sin documentación propia).
