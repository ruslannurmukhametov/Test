# Пиццерии с выручкой как у Надым-1 (±20%), октябрь 2026 — только общая выручка
#
# Источник: Google-таблица выручки сети (лист по умолчанию), столбец «окт.-26», RUR:
#   https://docs.google.com/spreadsheets/d/13Yb5zzvnY6l5i2rwlBpl_cJTbKAk-aPvGAHYVW1XQys
#   - франшиза: раздел «Russia / Domestic» (по строке на пиццерию; сумма = «Total franchise»);
#   - собственные: раздел «Company-owned Dine-in sales», строки Total (сумма = «Total Company-owned»).
#   Вместе сходится с «Total Russia».
#
# Обновить данные: скачать таблицу в CSV
#   curl -o sheet.csv "https://docs.google.com/spreadsheets/d/13Yb5zzvnY6l5i2rwlBpl_cJTbKAk-aPvGAHYVW1XQys/gviz/tq?tqx=out:csv"
#   python3 analysis/peers_revenue_nadym1_2026_10.py sheet.csv > analysis/reports/peers_revenue_nadym1_2026_10.md
# Без аргумента скрипт берёт уже извлечённое data/revenue_units_2026_10.csv.
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "revenue_units_2026_10.csv")
MONTH = "окт.-26"
NADYM = "Надым-1"
BAND = 0.20


def num(x):
    x = x.replace("\xa0", "").replace(" ", "")
    return int(float(x)) if x not in ("", "-") else None


def extract(path):
    rows = list(csv.reader(open(path, encoding="utf-8")))
    hdr = [i for i, r in enumerate(rows) if r[1] == "Russia" and r[2] == "Domestic"][0] + 1  # строка с месяцами
    col = rows[hdr].index(MONTH)
    end = [i for i, r in enumerate(rows) if r[1] == "Total franchise"][0]
    franchise = {r[2]: num(r[col]) for r in rows[hdr + 2:end] if r[2] and not r[3]}  # +2: пропуск строки Company-owned
    co_start = [i for i, r in enumerate(rows) if r[1] == "Company-owned Dine-in sales"][0] + 2
    co_end = [i for i, r in enumerate(rows) if r[1] == "Total Company-owned" and i > co_start][0]
    own, cur = {}, None
    for r in rows[co_start:co_end]:
        if r[2]:
            cur = r[2]
        if r[3] == "Total":
            own[cur] = num(r[col])
    # сверка с итогами таблицы
    assert sum(v or 0 for v in franchise.values()) == num(rows[end][col])
    assert sum(v or 0 for v in own.values()) == num(rows[co_end][col])
    out = {}
    entries = [(n, "собственная", v) for n, v in own.items()] + [(n, "франшиза", v) for n, v in franchise.items()]
    for name, typ, v in entries:
        if name not in out or (v and not out[name][1]):  # Химки-1, Новомосковск-1 есть в обоих разделах: берём непустое
            out[name] = (typ, v)
    with open(DATA, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pizzeria", "type", "revenue_2026_10_rub"])
        for name, (typ, v) in sorted(out.items(), key=lambda kv: -(kv[1][1] or 0)):
            w.writerow([name, typ, "" if v is None else v])


if len(sys.argv) > 1:
    extract(sys.argv[1])

units = [(r["pizzeria"], r["type"], int(r["revenue_2026_10_rub"])) for r in csv.DictReader(open(DATA))
         if r["revenue_2026_10_rub"] and int(r["revenue_2026_10_rub"]) > 0]
units.sort(key=lambda u: -u[2])
nadym = dict((u[0], u[2]) for u in units)[NADYM]
lo, hi = nadym * (1 - BAND), nadym * (1 + BAND)
peers = [u for u in units if lo <= u[2] <= hi]
rank = [u[0] for u in units].index(NADYM) + 1


def rub(x):
    return f"{x:,.0f}".replace(",", " ")


print("# Пиццерии с выручкой как у Надым-1: октябрь 2026\n")
print("Источник — Google-таблица выручки сети, столбец «окт.-26», ₽. Пиццерии России: франшиза и собственные.\n")
print(f"- Выручка Надым-1 — **{rub(nadym)} ₽**, {rank}-е место из {len(units)} пиццерий с выручкой за октябрь.")
def pizzerias(n):
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} пиццерия"
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return f"{n} пиццерии"
    return f"{n} пиццерий"


print(f"- Диапазон ±{BAND * 100:.0f}%: {rub(lo)} – {rub(hi)} ₽. В него попали **{pizzerias(len(peers))}** вместе с Надымом.\n")
print("| # | Пиццерия | Выручка, ₽ | К Надым-1 |")
print("|---:|---|---:|---:|")
for i, (name, typ, v) in enumerate(peers, 1):
    d = f"{(v / nadym - 1) * 100:+.0f}%".replace("+0%", "0%")
    label = f"**{name}**" if name == NADYM else name + (" (собств.)" if typ == "собственная" else "")
    print(f"| {i} | {label} | {rub(v)} | {d} |")
