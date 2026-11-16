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

# ================================
# 📍 ZONA MÁS PEDIDA
# ================================

zonas = []

for linea in lineas:
    partes = linea.split("|")
    zona = partes[2].strip()
    zonas.append(zona)

# Contar cuántas veces aparece cada zona
conteo = {}
for zona in zonas:
    if zona in conteo:
        conteo[zona] = conteo[zona] + 1
    else:
        conteo[zona] = 1

# Encontrar la que más aparece
zona_top = max(conteo, key=conteo.get)

print()
print(f"📍 Zona más pedida: {zona_top} ({conteo[zona_top]} cotizaciones)")
