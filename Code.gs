/**
 * Apps Script – Predictivo de Turbocompresores GPM
 * Pegar en Extensiones > Apps Script del Google Sheets que contiene VIBRACIONES, LIMITES_VIB, ACEITE,
 * LIMITES_ACEITE, OXIDACION y HALLAZGOS.
 * Implementar > Nueva implementación > Aplicación web
 *   Ejecutar como: Yo · Quién tiene acceso: Cualquier usuario
 * Copiar la URL /exec en FUENTE.appsScriptUrl dentro de index.html.
 */
function doGet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const tz = ss.getSpreadsheetTimeZone();
  const leer = n => {
    const sh = ss.getSheetByName(n);
    if (!sh) return [];
    return sh.getDataRange().getValues().map(r => r.map(v => v instanceof Date ? Utilities.formatDate(v, tz, 'yyyy-MM-dd') : v));
  };
  const out = { generado: new Date().toISOString() };
  ['VIBRACIONES', 'LIMITES_VIB', 'ACEITE', 'LIMITES_ACEITE', 'OXIDACION', 'HALLAZGOS'].forEach(n => out[n] = leer(n));
  return ContentService.createTextOutput(JSON.stringify(out)).setMimeType(ContentService.MimeType.JSON);
}
