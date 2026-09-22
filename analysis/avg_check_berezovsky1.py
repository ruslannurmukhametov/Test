# Средний чек, Березовский Свердловская-1, июль–август 2026
# Источник: finances.sales.units.monthly (MCP Dodo Sky), без НДС, ₽
# (канал, продажи, заказы) из salesBreakdown
jul = dict(total=(5500622,6717), rows=[
 ("Dine-in",457963,1150),("Delivery",2473139,1923),("Dine-in",1036427,1637),("Delivery",260507,199),
 ("Dine-in",838673,1209),("Dine-in",150089,365),("Dine-in",7057,4),("Dine-in",35358,38),
 ("Delivery",158252,119),("Dine-in",12240,14),("Dine-in",15999,18),("Delivery",25269,17),
 ("Dine-in",1135,1),("Delivery",22556,16),("Dine-in",2368,2),("Dine-in",3590,4),("Dine-in",0,1)])
aug = dict(total=(5250532,6314), rows=[
 ("Dine-in",900071,1502),("Delivery",2380281,1815),("Dine-in",867853,1206),("Dine-in",161548,356),
 ("Delivery",279331,215),("Delivery",12982,9),("Dine-in",32189,35),("Dine-in",405519,1006),
 ("Dine-in",0,5),("Dine-in",9405,13),("Delivery",156290,116),("Dine-in",11506,10),
 ("Dine-in",10487,8),("Delivery",17604,12),("Dine-in",3252,3),("Dine-in",1445,2),("Dine-in",769,1)])
def agg(months):
    out={}
    for c in ("Delivery","Dine-in"):
        s=sum(r[1] for m in months for r in m["rows"] if r[0]==c); o=sum(r[2] for m in months for r in m["rows"] if r[0]==c)
        out[c]=(s,o)
    S=sum(m["total"][0] for m in months); O=sum(m["total"][1] for m in months)
    assert S==sum(v[0] for v in out.values()) and O==sum(v[1] for v in out.values())
    return S,O,out
for name,ms in (("Июль",[jul]),("Август",[aug]),("Июль–август",[jul,aug])):
    S,O,out=agg(ms)
    print(f"{name}: итого {S/O:.0f} ₽ ({O} зак.) | доставка {out['Delivery'][0]/out['Delivery'][1]:.0f} ₽ ({out['Delivery'][1]} зак.) | ресторан {out['Dine-in'][0]/out['Dine-in'][1]:.0f} ₽ | доля доставки {out['Delivery'][1]/O:.0%}")
