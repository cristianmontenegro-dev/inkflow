# 📊 InkFlow — Estadísticas de cotizaciones

# Abrir el archivo en modo lectura ("r" = read)
with open("cotizaciones.txt", "r", encoding="utf-8") as archivo:
    lineas = archivo.readlines()

# Mostrar cuántas líneas tiene
print(f"📄 Total de cotizaciones: {len(lineas)}")
print()

# Mostrar cada línea
for linea in lineas:
    print(linea.strip())  # .strip() quita el salto de línea al final



# ================================
# 📊 CALCULAR ESTADÍSTICAS
# ================================

precios = []

for linea in lineas:
    partes = linea.split("|")
    precio_texto = partes[-1].replace("$", "").replace(" COP", "").replace(",", "").strip()
    precio = int(precio_texto)
    precios.append(precio)

total = sum(precios)
promedio = total / len(precios)
mas_caro = max(precios)

print()
print("=" * 35)
print("   📊 ESTADÍSTICAS INKFLOW")
print("=" * 35)
print(f"  💰 Total cotizado: ${total:,.0f} COP")
print(f"  👥 Clientes:       {len(precios)}")
print(f"  📈 Promedio:       ${promedio:,.0f} COP")
print(f"  🏆 Más caro:       ${mas_caro:,.0f} COP")
print("=" * 35)
