"""Calcula la bodega óptima libre en 3D usando el centro taxicab."""

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


def taxicab_center(points):
    """Obtiene el punto que minimiza la suma de distancias Manhattan por coordenada."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    zs = [p[2] for p in points]

    # Cada coordenada óptima puede calcularse de forma independiente con la mediana.
    center = (
        statistics.median(xs),
        statistics.median(ys),
        statistics.median(zs),
    )

    total_distance = sum(manhattan_3d(p, center) for p in points)
    distances = [manhattan_3d(p, center) for p in points]

    return center, total_distance, distances


if __name__ == "__main__":
    points = read_points_txt("puntos.txt")
    center, total, distances = taxicab_center(points)

    print("Bodega óptima:", center)
    print("Suma total mínima:", total)
    print("\nDistancia de cada punto a la bodega:")
    for i, (p, d) in enumerate(zip(points, distances)):
        print(f"{i}: punto={p}, distancia={d}")
