# Сравнение пиццерий с выручкой как у Надым-1 (±20%), октябрь 2026
#
# Источники (MCP Dodo Sky, выгрузка 11.11.2026):
#   data/sales_units_2026_10.csv — finances.sales.units.monthly, fromDate=2026-10-01, toDate=2026-10-31,
#     без НДС, ₽; все открытые пиццерии сети РФ, которые нашлись в units.directory (1158 с продажами).
#     Колонки *_sales/*_orders — суммы строк salesBreakdown по каналу (deliv/dinein/takeaway)
#     и по источнику заказа (app/web/kiosk/call/cashier/aggr/othersrc).
#     region_in_directory=no — у пиццерии в справочнике не заполнен регион, её нашли фильтром по городу.
#   data/lfl_peers_2026_10.csv — finances.lfl.by-units, октябрь 2026, granularity=Month (доли, округлены до 0,01).
#   Производительность и доставка Надым-1 — production.productivity, delivery.statistics (числа ниже).
#     По чужим пиццериям эти наборы Dodo IS не открывает, поэтому сравнение группы — только по продажам.
#
# Запуск: python3 analysis/peers_nadym1_2026_10.py > analysis/reports/peers_nadym1_2026_10.md
import csv
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
NADYM = "000d3a2c5b29a94711e807f6e8382b35"
BAND = 0.20
OPEN_NO_REGION = 116  # «Регион не указан», открыто — сводка units.directory на 11.11.2026

rows = list(csv.DictReader(open(os.path.join(HERE, "data", "sales_units_2026_10.csv"))))
for r in rows:
    for k, v in r.items():
        if k.endswith("_sales") or k.endswith("_orders") or k in ("sales", "orders"):
            r[k] = int(v)
lfl = {r["unitId"]: r for r in csv.DictReader(open(os.path.join(HERE, "data", "lfl_peers_2026_10.csv")))}

by_id = {r["unitId"]: r for r in rows}
nadym = by_id[NADYM]
lo, hi = nadym["sales"] * (1 - BAND), nadym["sales"] * (1 + BAND)
rank_all = {r["unitId"]: i + 1 for i, r in enumerate(sorted(rows, key=lambda r: -r["sales"]))}
group = sorted([r for r in rows if lo <= r["sales"] <= hi], key=lambda r: -r["sales"])
peers = [r for r in group if r["unitId"] != NADYM]
assert all(r["name"] for r in group), "у пиццерии из диапазона нет имени"
assert all(r["unitId"] in lfl for r in group), "нет LFL по пиццерии из диапазона"


def num(x, d=0):
    """Число по-русски: пробел между тысячами, запятая в дробной части."""
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


def lfl_val(r, key):
    x = lfl[r["unitId"]]
    # 0 и 0 одновременно у пиццерий, открытых в 2025 (id 11f0…): сопоставимой базы ещё нет
    if float(x["lflRevenue"]) == 0 and float(x["lflOrder"]) == 0 and r["unitId"].startswith("11f0"):
        return None
    return float(x[key])


def metrics(r):
    rest_s = r["dinein_sales"] + r["takeaway_sales"]
    rest_o = r["dinein_orders"] + r["takeaway_orders"]
    return {
        "Выручка, млн ₽": r["sales"] / 1e6,
        "Заказы": r["orders"],
        "Средний чек, ₽": r["sales"] / r["orders"],
        "Доля доставки в выручке": r["deliv_sales"] / r["sales"],
        "Доля доставки в заказах": r["deliv_orders"] / r["orders"],
        "Чек доставки, ₽": r["deliv_sales"] / r["deliv_orders"] if r["deliv_orders"] else None,
        "Чек зал+самовывоз, ₽": rest_s / rest_o if rest_o else None,  # None — только доставка
        "Доля приложения в выручке": r["app_sales"] / r["sales"],
        "Доля киосков в выручке": r["kiosk_sales"] / r["sales"],
        "Доля сайта в выручке": r["web_sales"] / r["sales"],
        "Доля кассы в выручке": r["cashier_sales"] / r["sales"],
        "LFL выручки": lfl_val(r, "lflRevenue"),
        "LFL заказов": lfl_val(r, "lflOrder"),
    }


M = {r["unitId"]: metrics(r) for r in group}
N = M[NADYM]
KEYS = list(N.keys())


def fmt(k, v):
    if v is None:
        return "н/д"
    if k.startswith("LFL"):
        return f"{v * 100:+.0f}%".replace("+0%", "0%")
    if k.startswith("Доля"):
        return f"{v * 100:.0f}%"
    if k.startswith("Выручка"):
        return num(v, 2)
    return num(v)


def peer_vals(k):
    return [M[r["unitId"]][k] for r in peers if M[r["unitId"]][k] is not None]


def place(k):
    allv = sorted([M[r["unitId"]][k] for r in group if M[r["unitId"]][k] is not None], reverse=True)
    return allv.index(N[k]) + 1, len(allv)


med = {k: st.median(peer_vals(k)) for k in KEYS}
no_region = sum(1 for r in rows if r["region_in_directory"] == "no")

# похожие по профилю: доля доставки в выручке ±5 п.п. и средний чек ±10% от Надыма
similar = [r for r in peers
           if abs(M[r["unitId"]]["Доля доставки в выручке"] - N["Доля доставки в выручке"]) <= 0.05
           and abs(M[r["unitId"]]["Средний чек, ₽"] / N["Средний чек, ₽"] - 1) <= 0.10]
sim_lfl = [M[r["unitId"]]["LFL выручки"] for r in similar if M[r["unitId"]]["LFL выручки"] is not None]

print("# Пиццерии с выручкой как у Надым-1: октябрь 2026\n")
print("**Основа:** finances.sales.units.monthly (MCP Dodo Sky), 01.10.2026–31.10.2026 включительно, выручка без НДС, ₽. "
      "LFL — finances.lfl.by-units за октябрь 2026. Выгрузка 11.11.2026.\n")
print(f"**Группа:** пиццерии сети РФ с выручкой ±{BAND * 100:.0f}% от Надым-1 ({num(lo / 1e6, 2)}–{num(hi / 1e6, 2)} млн ₽). "
      f"В группе {len(group)} пиццерий вместе с Надымом, выбраны из {len(rows)} пиццерий с продажами за октябрь.\n")
print("**Что сравнивается:** только продажи. Выручку и продукты на человеко-час, время доставки и выдачи "
      "Dodo IS по чужим пиццериям не открывает — эти метрики ниже есть только для Надым-1.\n")


def diff(k):
    return N[k] / med[k] - 1


print("## Главное\n")
print(f"- **Надым-1 — {num(N['Выручка, млн ₽'], 2)} млн ₽, {rank_all[NADYM]}-е место по выручке в сети** из {len(rows)}; "
      f"в группе — {place('Выручка, млн ₽')[0]}-е из {len(group)}. Медиана группы — {num(med['Выручка, млн ₽'], 2)} млн ₽.")
print(f"- **Слабое место — динамика к прошлому году.** LFL выручки {fmt('LFL выручки', N['LFL выручки'])} "
      f"при медиане группы {fmt('LFL выручки', med['LFL выручки'])}: {place('LFL выручки')[0]}-е место из {place('LFL выручки')[1]}. "
      f"LFL заказов {fmt('LFL заказов', N['LFL заказов'])} (медиана {fmt('LFL заказов', med['LFL заказов'])}).")
print(f"- **Чек выше группы за счёт доставки.** Средний чек {num(N['Средний чек, ₽'])} ₽ "
      f"({diff('Средний чек, ₽') * 100:+.0f}% к медиане), чек доставки {num(N['Чек доставки, ₽'])} ₽ "
      f"({diff('Чек доставки, ₽') * 100:+.0f}%). Чек в зале и на самовывозе ниже: {num(N['Чек зал+самовывоз, ₽'])} ₽ "
      f"({diff('Чек зал+самовывоз, ₽') * 100:+.0f}%).")
print(f"- **Надым больше других зависит от доставки и приложения.** Доставка — {fmt('Доля доставки в выручке', N['Доля доставки в выручке'])} выручки "
      f"(медиана {fmt('Доля доставки в выручке', med['Доля доставки в выручке'])}), приложение — "
      f"{fmt('Доля приложения в выручке', N['Доля приложения в выручке'])} (медиана {fmt('Доля приложения в выручке', med['Доля приложения в выручке'])}). "
      f"Сайт — {fmt('Доля сайта в выручке', N['Доля сайта в выручке'])}, {place('Доля сайта в выручке')[0]}-е место из {len(group)}.")
print(f"- **Похожих по профилю** (доля доставки ±5 п.п., средний чек ±10%) — {len(similar)}: "
      + ", ".join(f"{r['name']} ({fmt('LFL выручки', M[r['unitId']]['LFL выручки'])})" for r in similar)
      + f". Медиана их LFL выручки — {fmt('LFL выручки', st.median(sim_lfl))}, у Надыма {fmt('LFL выручки', N['LFL выручки'])}.")

print("\n## Надым-1 против группы\n")
print(f"Медиана и разброс — по {len(peers)} пиццериям группы без Надыма. Место — среди всех {len(group)} (1 = наибольшее значение).\n")
print("| Метрика | Надым-1 | Медиана группы | 25–75% группы | Место Надыма |")
print("|---|---:|---:|---:|---:|")
for k in KEYS:
    q = st.quantiles(peer_vals(k), n=4)
    p, n = place(k)
    print(f"| {k} | {fmt(k, N[k])} | {fmt(k, med[k])} | {fmt(k, q[0])} – {fmt(k, q[2])} | {p} из {n} |")

print(f"\n## Все {len(group)} пиццерий группы\n")
print("Отсортировано по выручке. Δ — отклонение выручки от Надым-1. «Чек зал» — каналы Dine-in и Takeaway вместе. "
      "Доли — от выручки.\n")
cols = ["Выручка, млн ₽", "Заказы", "Средний чек, ₽", "Доля доставки в выручке", "Чек доставки, ₽",
        "Чек зал+самовывоз, ₽", "Доля приложения в выручке", "Доля киосков в выручке", "LFL выручки", "LFL заказов"]
head = ["Выручка, млн ₽", "Δ", "Заказы", "Чек, ₽", "Доставка", "Чек доставки, ₽", "Чек зал, ₽",
        "Приложение", "Киоски", "LFL выр.", "LFL зак."]
print("| # | Пиццерия | Регион | " + " | ".join(head) + " |")
print("|---:|---|---|" + "---:|" * len(head))
for i, r in enumerate(group, 1):
    m = M[r["unitId"]]
    name = f"**{r['name']}**" if r["unitId"] == NADYM else r["name"]
    note = "¹" if r["region_in_directory"] == "no" else ""
    d = r["sales"] / nadym["sales"] - 1
    cells = [fmt(cols[0], m[cols[0]]), f"{d * 100:+.0f}%".replace("+0%", "0%")] + [fmt(c, m[c]) for c in cols[1:]]
    print(f"| {i} | {name}{note} | {r['region']} | " + " | ".join(cells) + " |")
print("\n¹ В справочнике Dodo IS у пиццерии не заполнен регион; регион указан по городу.")

print("\n## Производительность Надым-1 (по чужим пиццериям недоступна)\n")
print("production.productivity и delivery.statistics, местное время пиццерии, месяц целиком.\n")
prod = {  # месяц: (человеко-часы, выручка, выручка/чел-ч, продуктов/чел-ч, время на полке с, заказов на час курьера)
    "Сентябрь 2026": (5038.75, 19594715, 3888.80, 8.18, 183, 3.43),
    "Октябрь 2026": (5330.50, 21056194, 3950.13, 8.22, 125, 3.21),
}
assert prod["Октябрь 2026"][1] == nadym["sales"]
print("| Месяц | Выручка, млн ₽ | Человеко-часы | Выручка на чел.-час, ₽ | Продуктов на чел.-час | На тепловой полке, с | Заказов на час курьера |")
print("|---|---:|---:|---:|---:|---:|---:|")
for mth, (h, s, sph, pph, shelf, och) in prod.items():
    print(f"| {mth} | {num(s / 1e6, 2)} | {num(h)} | {num(sph)} | {num(pph, 2)} | {shelf} | {num(och, 2)} |")
(h9, s9, sph9, *_), (h10, s10, sph10, *_) = prod.values()
print(f"\nС сентября на октябрь выручка выросла на {num((s10 / s9 - 1) * 100, 1)}%, человеко-часы — на {num((h10 / h9 - 1) * 100, 1)}%, "
      f"выручка на человеко-час — на {num((sph10 / sph9 - 1) * 100, 1)}%.")
dl = dict(orders=10319, fulfil=1494, cook=720, trip=649, late=272, trips=6888)
print(f"\nДоставка, октябрь 2026: {num(dl['orders'])} заказов; от заказа до клиента в среднем {num(dl['fulfil'] / 60, 1)} мин "
      f"(приготовление {num(dl['cook'] / 60)} мин, в пути {num(dl['trip'] / 60, 1)} мин); опозданий {dl['late']} "
      f"({num(dl['late'] / dl['orders'] * 100, 1)}%); {num(dl['orders'] / dl['trips'], 2)} заказа на поездку.")

print("\n## Ограничения\n")
print("- Пиццерии без строк продаж за октябрь не вошли: «Додо Франчайзинг-1/2/3/4/6» (служебные), "
      "Королёв-3, Уссурийск-1, Астрахань-2 (временно закрыты), Ленинск-Кузнецкий-1.")
print(f"- У {OPEN_NO_REGION} открытых пиццерий в справочнике не заполнен регион. Их искали фильтром по городу "
      f"и нашли {no_region + 3} (из них {no_region} с продажами, 3 — служебные «Додо Франчайзинг»). "
      f"Около {OPEN_NO_REGION - no_region - 3} таких пиццерий, вероятно в малых городах, не нашлись и в сравнение не вошли.")
print("- LFL округлён Dodo IS до 1 п.п. У Самара-13 и Королёв-4 (открыты в 2025) сопоставимой базы ещё нет — «н/д».")
print("- Средний чек — выручка, делённая на все заказы, включая заказы с нулевой выручкой.")
