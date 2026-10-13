# 🖤 InkFlow — Calculadora de presupuestos
# Autor: Cristian Rojas
# Uso: calcular precio estimado de un tatuaje

print("=" * 45)
print("   🖤 INKFLOW — Calculadora de Tatuajes")
print("=" * 45)
print()

# Pedir datos al cliente
nombre = input("Nombre del cliente: ")
tamaño = float(input("Tamaño en cm (ej: 10): "))
zona = input("Zona (brazo/antebrazo/pierna/costilla/mano/cuello): ").lower().strip()
complejidad = input("Complejidad (linea/sombra/color): ").lower().strip()

# Precio base por cm en COP
PRECIO_BASE = 15000

# Multiplicadores según la zona (más dolorosa = más caro)
zonas = {
    "brazo": 1.0,
    "antebrazo": 0.9,
    "pierna": 1.1,
    "costilla": 1.5,
    "mano": 1.7,
    "cuello": 1.8,
}

# Multiplicadores según complejidad
complejidades = {
    "linea": 1.0,
    "sombra": 1.3,
    "color": 1.6,
}

# Calcular
factor_zona = zonas.get(zona, 1.2)
factor_complejidad = complejidades.get(complejidad, 1.0)
total = PRECIO_BASE * tamaño * factor_zona * factor_complejidad

# preguntar si es cliente recurrente
recurrente = input("es cliente recurrente? (si/no):").lower().strip()
if recurrente == "si":
    total = total * 0.85
    print("se aplicó un descuento del 15% por ser cliente recurrente")

# Mostrar resultado
print()
print("-" * 45)
print(f"  COTIZACIÓN PARA: {nombre.upper()}")
print("-" * 45)
print(f"  Tamaño:       {tamaño} cm")
print(f"  Zona:         {zona}")
print(f"  Complejidad:  {complejidad}")
print(f"  Factor zona:  x{factor_zona}")
print(f"  Factor compl: x{factor_complejidad}")
print("-" * 45)
print(f"  💰 TOTAL:     ${total:,.0f} COP")
print("-" * 45)
print()
print("  🖤 Cotización generada por InkFlow")
print()
