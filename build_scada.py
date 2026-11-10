"""Genera scada.js a partir de los Excel de HistoryView (hoja Datos) de cada planta.
Uso: python3 build_scada.py <periodo> <xlsx_TTY> <xlsx_SQL> <desde> <hasta>
Agrega por día solo los registros en operación (Ngp > 5 %)."""
import sys, json, math
import pandas as pd, numpy as np

periodo, fT, fS, desde, hasta = sys.argv[1:6]
TCS = [f"AN_T5_TC{i}" for i in range(1, 18)]
SKIP = {"AA_HPC_Pri_Vent_HH", "AA_HPC_Buffer_Air_LL"}

def r(v, sig=4):
    if v is None or (isinstance(v, float) and math.isnan(v)): return None
    if v == 0: return 0
    d = max(0, sig - 1 - int(math.floor(math.log10(abs(v)))))
    return round(float(v), min(d, 4))

def load(f):
    d = pd.read_excel(f, sheet_name="Datos").rename(columns={"Fecha y Hora": "t"})
    d["t"] = pd.to_datetime(d["t"]).dt.floor("h")
    d = d[(d.t >= desde) & (d.t < hasta)]
    return d.groupby("t", as_index=False).mean(numeric_only=True).sort_values("t").reset_index(drop=True)

def paradas(d):
    # horas sin operar (Ngp<=5) o huecos de registro; tramos > 12 h
    full = pd.DataFrame({"t": pd.date_range(d.t.min(), d.t.max(), freq="h")}).merge(d[["t", "AN_Ngp"]], how="left")
    off = ~(full.AN_Ngp > 5)
    out, start = [], None
    for t, o in zip(full.t, off):
        if o and start is None: start = t
        if not o and start is not None:
            if (t - start).total_seconds() / 3600 > 12: out.append([start.strftime("%Y-%m-%d %H:%M"), t.strftime("%Y-%m-%d %H:%M"), round((t - start).total_seconds() / 86400, 1)])
            start = None
    if start is not None and (full.t.iloc[-1] - start).total_seconds() / 3600 > 12:
        out.append([start.strftime("%Y-%m-%d %H:%M"), full.t.iloc[-1].strftime("%Y-%m-%d %H:%M"), round((full.t.iloc[-1] - start).total_seconds() / 86400, 1)])
    return out

def planta(f):
    d = load(f)
    op = d[d.AN_Ngp > 5].copy()
    op["div"] = op[TCS].max(axis=1) - op[TCS].min(axis=1)
    med = op[TCS].median(axis=1)
    dias = pd.date_range(d.t.min().normalize(), d.t.max().normalize(), freq="D")
    op["dia"] = op.t.dt.normalize(); d["dia"] = d.t.dt.normalize()
    g = op.groupby("dia")
    vars_ = [c for c in d.columns if c.startswith("AN_") and c not in SKIP] + ["div"]
    agg = {}
    for c in vars_:
        a = g[c].agg(["mean", "min", "max"]).reindex(dias)
        agg[c] = {"a": [r(x) for x in a["mean"]], "n": [r(x) for x in a["min"]], "x": [r(x) for x in a["max"]]}
    st = {c: [r(op[c].mean()), r(op[c].min()), r(op[c].max())] for c in vars_}
    # desvío diario de cada termocupla respecto de la mediana del resto
    dev = {}
    for c in TCS:
        others = op[[x for x in TCS if x != c]].median(axis=1)
        dev[c] = [r(x, 3) for x in (op[c] - others).groupby(op.dia).mean().reindex(dias)]
    # anomalía de termocupla: valor < 50 % de la mediana del resto
    anom = {}
    for c in TCS:
        others = op[[x for x in TCS if x != c]].median(axis=1)
        m = op[c] < 0.5 * others
        if m.sum() > 0:
            anom[c] = {"n": int(m.sum()), "prom": r(op.loc[m, c].mean()), "med": r(others[m].mean()), "desde": op.loc[m, "t"].min().strftime("%Y-%m-%d"), "hasta": op.loc[m, "t"].max().strftime("%Y-%m-%d")}
    hop = op.groupby("dia").size().reindex(dias, fill_value=0).tolist()
    hreg = d.groupby("dia").size().reindex(dias, fill_value=0).tolist()
    return {"desde": d.t.min().strftime("%Y-%m-%d %H:%M"), "hasta": d.t.max().strftime("%Y-%m-%d %H:%M"), "registros": int(len(d)), "op": int(len(op)),
            "operacion": round(len(op) / len(d) * 100, 1), "paradas": paradas(d), "dias": [x.strftime("%Y-%m-%d") for x in dias],
            "hop": hop, "hreg": hreg, "v": agg, "st": st, "t5dev": dev, "t5anom": anom}

out = {"TTY": planta(fT), "SQL": planta(fS)}
js = f"/* Generado por build_scada.py desde HistoryView · período {periodo} · agregados diarios en operación (Ngp > 5 %) */\n" \
     f"window.SCADA_DATA = window.SCADA_DATA || {{}};\nSCADA_DATA[{json.dumps(periodo)}] = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n"
open(f"scada_{periodo}.js", "w", encoding="utf-8").write(js)
for p in out: print(p, out[p]["registros"], out[p]["operacion"], out[p]["paradas"], list(out[p]["t5anom"].items())[:2])
print(len(js) // 1024, "KB")
