"""Busca una bodega óptima con coordenada `y` fija bajo distancia Manhattan."""

import statistics


def read_points_txt(path):
    """Lee puntos 3D desde un archivo de texto con una terna por línea."""
    points = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"Línea {line_num}: esperaba 3 valores")
            x, y, z = map(float, parts)
            points.append((x, y, z))
    return points


def manhattan_3d(a, b):
    """Calcula la distancia Manhattan entre dos puntos 3D."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def constrained_center(points, fixed_y=-40):
    """Calcula el centro taxicab restringido a un plano horizontal `y = fixed_y`."""
    xs = [p[0] for p in points]
    zs = [p[2] for p in points]

    # En distancia Manhattan, la mediana minimiza la suma de distancias por eje.
    center = (
        statistics.median(xs),
        fixed_y,
        statistics.median(zs),
    )

    total_distance = sum(manhattan_3d(p, center) for p in points)
    distances = [manhattan_3d(p, center) for p in points]

    return center, total_distance, distances


if __name__ == "__main__":
    points = read_points_txt("puntos.txt")

    center, total, distances = constrained_center(points, fixed_y=-40)

    print("Bodega óptima con y fijo:")
    print("Centro:", center)
    print("Suma total mínima:", total)

    print("\nDistancias individuales:")
    for i, (p, d) in enumerate(zip(points, distances)):
        print(f"{i}: punto={p}, distancia={d}")
