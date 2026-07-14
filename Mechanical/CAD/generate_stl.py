"""
AERIS-10P Parametric STL Generator
====================================
Generates ASCII STL files for all AERIS-10P mechanical parts.
No external libraries required — uses only Python standard library.

Usage:
    python generate_stl.py           # Generate all parts to ./stl_output/
    python generate_stl.py --part enclosure  # Generate specific part
    python generate_stl.py --list    # List all available parts

Generated files:
    main_enclosure.stl        300 x 200 x 100 mm electronics box
    antenna_panel.stl         200 x 120 x 5 mm flat panel
    tripod_mount_adapter.stl  100 x 80 x 68 mm L-bracket
    electronics_tray.stl      280 x 180 x 12 mm PCB tray
    cooling_fan_bracket.stl   80 x 80 x 4 mm fan mount
    front_panel.stl           300 x 100 x 5 mm front panel

All dimensions in millimeters.
"""

import os
import argparse
import math
from typing import List, Tuple

# Type aliases
Vec3 = Tuple[float, float, float]
Triangle = Tuple[Vec3, Vec3, Vec3, Vec3]  # (normal, v0, v1, v2)


def vec3(x: float, y: float, z: float) -> Vec3:
    return (x, y, z)


def normalize(v: Vec3) -> Vec3:
    mag = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    if mag < 1e-12:
        return (0.0, 0.0, 1.0)
    return (v[0]/mag, v[1]/mag, v[2]/mag)


def cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    )


def compute_normal(v0: Vec3, v1: Vec3, v2: Vec3) -> Vec3:
    """Compute outward normal for triangle (v0, v1, v2) — CCW winding."""
    edge1 = (v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2])
    edge2 = (v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2])
    return normalize(cross(edge1, edge2))


def triangle(v0: Vec3, v1: Vec3, v2: Vec3) -> Triangle:
    """Create triangle with auto-computed normal."""
    n = compute_normal(v0, v1, v2)
    return (n, v0, v1, v2)


def box_triangles(W: float, D: float, H: float,
                   x0: float = 0, y0: float = 0, z0: float = 0) -> List[Triangle]:
    """
    Generate 12 triangles for a rectangular box W×D×H at origin (x0,y0,z0).

    Coordinate system:
      W = width  (X direction)
      D = depth  (Y direction)
      H = height (Z direction)

    Faces: bottom(z=z0), top(z=z0+H), front(y=y0), back(y=y0+D),
           left(x=x0), right(x=x0+W)
    """
    x1, y1, z1 = x0 + W, y0 + D, z0 + H
    tris = []

    # Bottom face (z=z0), normal (0,0,-1)
    tris += [
        triangle(vec3(x0, y0, z0), vec3(x1, y0, z0), vec3(x1, y1, z0)),
        triangle(vec3(x0, y0, z0), vec3(x1, y1, z0), vec3(x0, y1, z0)),
    ]
    # Top face (z=z1), normal (0,0,+1)
    tris += [
        triangle(vec3(x0, y0, z1), vec3(x1, y1, z1), vec3(x1, y0, z1)),
        triangle(vec3(x0, y0, z1), vec3(x0, y1, z1), vec3(x1, y1, z1)),
    ]
    # Front face (y=y0), normal (0,-1,0)
    tris += [
        triangle(vec3(x0, y0, z0), vec3(x1, y0, z1), vec3(x1, y0, z0)),
        triangle(vec3(x0, y0, z0), vec3(x0, y0, z1), vec3(x1, y0, z1)),
    ]
    # Back face (y=y1), normal (0,+1,0)
    tris += [
        triangle(vec3(x0, y1, z0), vec3(x1, y1, z0), vec3(x1, y1, z1)),
        triangle(vec3(x0, y1, z0), vec3(x1, y1, z1), vec3(x0, y1, z1)),
    ]
    # Left face (x=x0), normal (-1,0,0)
    tris += [
        triangle(vec3(x0, y0, z0), vec3(x0, y1, z0), vec3(x0, y1, z1)),
        triangle(vec3(x0, y0, z0), vec3(x0, y1, z1), vec3(x0, y0, z1)),
    ]
    # Right face (x=x1), normal (+1,0,0)
    tris += [
        triangle(vec3(x1, y0, z0), vec3(x1, y0, z1), vec3(x1, y1, z1)),
        triangle(vec3(x1, y0, z0), vec3(x1, y1, z1), vec3(x1, y1, z0)),
    ]
    return tris


def write_ascii_stl(filename: str, triangles: List[Triangle], name: str = "solid") -> None:
    """Write ASCII STL file."""
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    with open(filename, 'w') as f:
        f.write(f"solid {name}\n")
        for (nx, ny, nz), (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) in triangles:
            f.write(f"  facet normal {nx:.6f} {ny:.6f} {nz:.6f}\n")
            f.write(f"    outer loop\n")
            f.write(f"      vertex {x0:.4f} {y0:.4f} {z0:.4f}\n")
            f.write(f"      vertex {x1:.4f} {y1:.4f} {z1:.4f}\n")
            f.write(f"      vertex {x2:.4f} {y2:.4f} {z2:.4f}\n")
            f.write(f"    endloop\n")
            f.write(f"  endfacet\n")
        f.write(f"endsolid {name}\n")
    print(f"  Written: {filename} ({len(triangles)} triangles)")


# ─────────────────────────────────────────────────────────────────────────────
# Part Definitions
# ─────────────────────────────────────────────────────────────────────────────

def make_main_enclosure(output_dir: str) -> None:
    """Electronics enclosure: 300×200×100 mm."""
    tris = box_triangles(300, 200, 100)
    write_ascii_stl(
        os.path.join(output_dir, "main_enclosure.stl"),
        tris,
        "aeris_main_enclosure"
    )
    print("  Description: 300mm(W) x 200mm(D) x 100mm(H) electronics enclosure")
    print("  Material: 6061-T6 Aluminium or PETG 30% infill")


def make_antenna_panel(output_dir: str) -> None:
    """Antenna PCB mount panel: 200×120×5 mm."""
    tris = box_triangles(200, 120, 5)
    write_ascii_stl(
        os.path.join(output_dir, "antenna_panel.stl"),
        tris,
        "aeris_antenna_panel"
    )
    print("  Description: 200mm(W) x 120mm(D) x 5mm(H) flat antenna mounting panel")
    print("  Material: Aluminium backing plate (actual antenna is Rogers RO4003C PCB)")


def make_tripod_mount(output_dir: str) -> None:
    """Tripod mount adapter: 100×80×68 mm (L-bracket approximated as box)."""
    # Simplified: full bounding box
    # For production: model as actual L-bracket in FreeCAD
    tris = box_triangles(100, 80, 68)
    write_ascii_stl(
        os.path.join(output_dir, "tripod_mount_adapter.stl"),
        tris,
        "aeris_tripod_adapter"
    )
    print("  Description: 100mm(W) x 80mm(D) x 68mm(H) tripod mount (bounding box)")
    print("  Note: Actual L-bracket has hollow interior — refine in FreeCAD for production")
    print("  Material: 6061-T6 Aluminium")


def make_electronics_tray(output_dir: str) -> None:
    """PCB mounting tray: 280×180×12 mm."""
    tris = box_triangles(280, 180, 12)
    write_ascii_stl(
        os.path.join(output_dir, "electronics_tray.stl"),
        tris,
        "aeris_electronics_tray"
    )
    print("  Description: 280mm(W) x 180mm(D) x 12mm(H) PCB mounting tray")
    print("  Material: 6061-T6 Aluminium or PETG (with M3 thread inserts)")


def make_fan_bracket(output_dir: str) -> None:
    """80mm cooling fan mounting plate: 80×80×4 mm."""
    tris = box_triangles(80, 80, 4)
    write_ascii_stl(
        os.path.join(output_dir, "cooling_fan_bracket.stl"),
        tris,
        "aeris_fan_bracket"
    )
    print("  Description: 80mm x 80mm x 4mm fan mounting plate")
    print("  Material: PETG (temperature-resistant)")
    print("  Note: Add 72mm circular cutout for fan airflow in FreeCAD")


def make_front_panel(output_dir: str) -> None:
    """Front panel with connector positions: 300×100×5 mm."""
    tris = box_triangles(300, 100, 5)
    write_ascii_stl(
        os.path.join(output_dir, "front_panel.stl"),
        tris,
        "aeris_front_panel"
    )
    print("  Description: 300mm(W) x 100mm(H) x 5mm(T) front panel")
    print("  Material: 6061-T6 Aluminium")
    print("  Note: Add connector cutouts (SMA, USB, RJ45, XT60) in FreeCAD or EasyEDA")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

PARTS = {
    'enclosure':  make_main_enclosure,
    'panel':      make_antenna_panel,
    'tripod':     make_tripod_mount,
    'tray':       make_electronics_tray,
    'fan':        make_fan_bracket,
    'front':      make_front_panel,
}


def main():
    parser = argparse.ArgumentParser(
        description='AERIS-10P Parametric STL Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: python generate_stl.py --output ./stl_output"
    )
    parser.add_argument('--output', '-o', default='../STL',
                        help='Output directory (default: ../STL)')
    parser.add_argument('--part', '-p', choices=list(PARTS.keys()),
                        help='Generate only one specific part')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List available parts and exit')
    args = parser.parse_args()

    if args.list:
        print("Available parts:")
        for name in PARTS:
            print(f"  {name}")
        return

    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nAERIS-10P STL Generator")
    print(f"Output directory: {output_dir}")
    print()

    if args.part:
        parts_to_generate = {args.part: PARTS[args.part]}
    else:
        parts_to_generate = PARTS

    for name, func in parts_to_generate.items():
        print(f"Generating: {name}")
        func(output_dir)
        print()

    print(f"Done. Generated {len(parts_to_generate)} STL file(s) in {output_dir}/")
    print()
    print("Next steps:")
    print("  1. Open STL files in PrusaSlicer or Bambu Studio")
    print("  2. Print in PETG at 30% infill for prototype")
    print("  3. For production: import into FreeCAD, add cutouts and features, export STEP")
    print("  4. For aluminium: send STEP to Proto Labs or local machine shop")


if __name__ == '__main__':
    main()
