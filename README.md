# Predictivo de Turbocompresores · GPM

Tablero web (GitHub Pages) del seguimiento predictivo de los turbocompresores TC1 (Solar Mars 100) de PC Tratayén y PC Salliqueló. Ordenado por tema, como los informes predictivos:

- **Condición operativa (SCADA):** histórico HistoryView por sistema (general, T5, lubricación, seal gas, buffer air, admisión, vibraciones del motor, compresor HPC). Registros horarios filtrados a operación (Ngp > 5 %) y agregados por día.
- **Relevamiento de vibraciones:** mediciones con equipo portátil (planilla VIBR TTCC) contra alarma y paro.
- **Análisis de aceite:** muestras del laboratorio YPF AUCTOR contra valores Mín/Máx del lubricante, y ensayos de oxidación RPVOT, RULER y MPC.
- **Hallazgos y seguimiento.**

## Archivos
- `index.html`: el tablero. Hoy trae embebidos vibraciones, aceite y hallazgos (pasan a Google Sheets en la próxima etapa).
- `scada_<período>.js`: agregados diarios de la condición operativa, uno por período (p. ej. `scada_2026-S1.js`).
- `build_scada.py`: genera el archivo de un período a partir de los Excel de HistoryView (hoja `Datos`).

## Cargar un período nuevo de SCADA
```
python3 build_scada.py 2026-S2 TC_Tratayen_1226.xlsx TC_Salliquelo_1226.xlsx 2026-07-01 2027-01-01
```
Subir el `scada_2026-S2.js` generado, agregar su `<script src>` en `index.html` y el período en `PERIODOS`.

## Criterios
- Semáforo: Atención desde el 60 % del valor de alarma o con hallazgo abierto (constante `UMBRAL`).
- Termocupla T5 fuera de servicio: lectura < 50 % de la mediana del resto durante 24 h o más en operación.
- Relevamiento de vibraciones: todo en µm. Salliqueló usa la Alarma/Paro de Tratayén (mismo modelo; sin documentación propia).
