# Списания, Березовский Свердловская-1, 27.09.2026 (с 00:00 по 28.09 00:00, местное время)
# Источники (MCP Dodo Sky): accounting.write-offs.products, accounting.write-offs.stock-items,
# accounting.defective-products. Данные получены 28.09.2026 — последние 7 дней ещё могут измениться.
# Готовые продукты: сумма по цене меню (pricePerPiece), НЕ себестоимость. Сырьё: цены в наборе нет.
from collections import defaultdict
REASON = {"ExpiredShowcaseTime": "истекло время на витрине", "HumanElement": "человеческий фактор",
          "Expired": "истёк срок годности", "Defected": "брак", "Marketing": "маркетинг"}
# (время, причина, продукт, кол-во, цена меню за шт, ₽)
products = [
 ("12:48","ExpiredShowcaseTime","Кус Пепперони Римская",2,89),
 ("13:09","ExpiredShowcaseTime","Кус Песто Римская",4,89),
 ("15:44","ExpiredShowcaseTime","Кус Песто Римская",1,89),
 ("15:44","ExpiredShowcaseTime","Кус Пепперони Римская",1,89),
 ("17:15","ExpiredShowcaseTime","Кус Пепперони Римская",3,89),
 ("18:15","ExpiredShowcaseTime","Кус Мясо и овощи Римская",4,89),
 ("18:15","ExpiredShowcaseTime","Кус Бекон BBQ Римская",4,89),
 ("20:36","ExpiredShowcaseTime","Кус Бекон BBQ Римская",1,89),
 ("21:16","HumanElement","Чесночный цыпленок Маленькая",1,379),
]
# (время, причина, сырьё, кол-во, ед.)
stock = [
 ("21:16","Defected","Томаты свежие",0.002,"кг"),
 ("21:16","Expired","Соус сырный",0.033,"кг"),
 ("21:16","Expired","Томаты свежие",0.002,"кг"),
 ("21:16","Expired","Шампиньоны свежие",0.422,"кг"),
 ("21:16","Expired","Огурцы маринован.",0.094,"кг"),
 ("21:16","Expired","Пита",10,"шт"),
 ("21:16","Marketing","Торт шоколадно-малиновый",1,"шт"),
 ("21:16","Expired","Крылья барбекю",2,"кг"),
]
# Брак: (время продажи, продукт, цена со скидкой, ₽)
defective = [
 ("13:19","Пицца Том Ям Маленькая",471.74),
 ("13:24","Картофель по-деревенски Большая",201.75),
 ("13:52","Креветки терияки 5 шт",389.00),
]

by = defaultdict(lambda: [0, 0])
for _, r, name, q, p in products:
    by[(REASON[r], name)][0] += q; by[(REASON[r], name)][1] += q * p
print(f"Готовые продукты: {len(products)} строк, {sum(p[3] for p in products)} шт, "
      f"{sum(p[3]*p[4] for p in products)} ₽ по цене меню")
for (r, name), (q, s) in sorted(by.items(), key=lambda x: -x[1][1]):
    print(f"  {name:32s} {q:3d} шт {s:6.0f} ₽  ({r})")
sby = defaultdict(list)
for _, r, name, q, u in stock:
    sby[REASON[r]].append(f"{name} {q:g} {u}")
print(f"Сырьё: {len(stock)} строк, без цены")
for r, items in sby.items():
    print(f"  {r}: " + "; ".join(items))
print(f"Брак (продукты): {len(defective)} шт, {sum(d[2] for d in defective):.2f} ₽ по цене со скидкой")
for t, name, p in defective:
    print(f"  {t} {name:32s} {p:7.2f} ₽")
