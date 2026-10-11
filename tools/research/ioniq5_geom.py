"""Procedural geometry for the Hyundai Ioniq 5 (2025), built from its real dimensions: 4.635 m long, 3.000 m wheelbase,
1.890 m wide, 1.605 m tall, 255/45R20 tyres. Derived from the Strata EV builder.

Everything is built in BeamNG vehicle space: +X = left, +Y = backward, +Z = up,
so the front of the car points toward -Y. Units are meters. Faces are wound
counter-clockwise when seen from outside (right-hand normal points outward).
"""
import numpy as np
from scipy.interpolate import PchipInterpolator

# ----------------------------------------------------------------- dimensions
Y_FRONT, Y_REAR = -2.3175, 2.3175      # overall length 4.635 m
AXLE_F, AXLE_R = -1.4725, 1.5275       # wheelbase 3.000 m, short overhangs
WHEEL_X = 0.819                        # track 1.638 m
TIRE_R = 0.369                         # 255/45R20
TIRE_SECTION = 0.255     # tire section width (m), matches tireWidth in the jbeam
RIM_R = 0.254
WHEEL_Z = TIRE_R
ARCH_R = 0.47
ARCH_ZC = 0.36

# material names (must match main.materials.json)
M_PAINT, M_GLASS, M_TRIM, M_UNDER = "strata_paint", "strata_glass", "strata_trim", "strata_underbody"
M_HEAD, M_TAIL = "strata_headlight", "strata_taillight"
M_INT, M_SEAT = "strata_interior", "strata_seat"
M_RIM, M_RIM_DARK, M_TIRE = "strata_rim", "strata_rim_dark", "strata_tire"
M_CHROME = "strata_chrome"
M_SIG_L, M_SIG_R, M_REV = "strata_signal_L", "strata_signal_R", "strata_reverse"
M_SCREEN, M_BUTTON = "strata_screen", "strata_button"

# clickable dash buttons (id, label, x position); they sit in a row under the centre screen
BUTTON_Y, BUTTON_Z = -0.645, 0.84
BUTTONS = [("lights", "Headlights", 0.150), ("hazard", "Hazard lights", 0.090), ("mode", "Drive mode", 0.030),
           ("crab", "Crab walk", -0.030), ("avas", "Pedestrian sound (AVAS)", -0.090), ("horn", "Horn", -0.150)]


def _pchip(pts):
    a = np.array(pts, dtype=float)
    return PchipInterpolator(a[:, 0], a[:, 1])


Z_FLOOR = _pchip([(-2.3175, 0.40), (-2.20, 0.30), (-2.05, 0.24), (-1.92, 0.205), (-1.78, 0.19),
                  (1.82, 0.19), (1.96, 0.21), (2.10, 0.27), (2.24, 0.36), (2.3175, 0.44)])
# a high, flat beltline that runs straight back to the tail
Z_SH = _pchip([(-2.3175, 0.72), (-2.25, 0.79), (-2.05, 0.86), (-1.6, 0.915), (-1.15, 0.955),
               (0.0, 0.985), (1.0, 0.995), (1.8, 1.005), (2.12, 0.995), (2.26, 0.96), (2.3175, 0.92)])
# clamshell bonnet, steep windscreen, long flat roof, near-vertical hatch: the Ioniq 5's boxy hatchback profile
Z_TOP = _pchip([(-2.3175, 0.74), (-2.28, 0.83), (-2.20, 0.89), (-2.0, 0.94), (-1.6, 0.995), (-1.25, 1.035),
                (-1.12, 1.10), (-0.88, 1.29), (-0.62, 1.46), (-0.38, 1.575), (-0.10, 1.605), (0.8, 1.607),
                (1.50, 1.595), (1.78, 1.565), (1.96, 1.49), (2.10, 1.35), (2.20, 1.20), (2.27, 1.07), (2.3175, 0.99)])

# y ranges for materials on the body loft
WINDSHIELD = (-1.12, -0.36)
REAR_GLASS = (1.80, 2.16)
SIDE_GLASS = (-1.08, 1.98)
PILLARS = [(0.30, 0.40), (1.40, 1.62)]       # blacked-out B and C pillars
HEADLAMP_Y = -2.08
TAILLAMP_Y = 2.20
DOOR_SEAMS = [-1.06, 0.355, 1.40]                # thin dark shut lines on the doors
SEAM_HALF = 0.003
HANDLES = [(0.02, 0.16), (1.10, 1.24)]           # door handles (below the shoulder)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def well_x(y):
    """Inner wall of the wheel well (front wells are wider for steering lock)."""
    return 0.48 if y < 0 else 0.60


def half_width(y):
    w = 0.945 + 0.008 * np.exp(-((y - AXLE_F) / 0.35) ** 2) + 0.016 * np.exp(-((y - AXLE_R) / 0.40) ** 2)
    yf0, wf_end = -2.02, 0.80
    if y < yf0:
        t = (yf0 - y) / (yf0 - Y_FRONT)
        w = wf_end + (w - wf_end) * np.sqrt(max(0.0, 1 - t ** 2))
    yr0, wr_end = 2.06, 0.86
    if y > yr0:
        t = (y - yr0) / (Y_REAR - yr0)
        w = wr_end + (w - wr_end) * np.sqrt(max(0.0, 1 - t ** 2))
    return float(w)


def arch_z(y):
    zf = float(Z_FLOOR(y))
    for ya in (AXLE_F, AXLE_R):
        dy = y - ya
        if abs(dy) < ARCH_R:
            return max(zf, ARCH_ZC + np.sqrt(ARCH_R ** 2 - dy ** 2)), True
    return zf, False


def cabin_factor(y):
    return float(smoothstep(-1.18, -0.42, y) * (1 - smoothstep(2.02, 2.28, y)))


N_HALF = 16   # points per half profile (bottom center .. top center)


def half_profile(y):
    """Left-half cross-section at station y: 16 (x, z) points from bottom center to top center."""
    zf = float(Z_FLOOR(y))
    za, _ = arch_z(y)
    zsh = float(Z_SH(y))
    zt = float(Z_TOP(y))
    w = half_width(y)
    c = cabin_factor(y)
    wx = well_x(y)
    # side-panel heights: fixed lines along the body, pushed up only where the arch needs room
    z5n = zf + 0.12
    nominal = [zf + 0.035, z5n, z5n + 0.45 * (zsh - z5n), z5n + 0.74 * (zsh - z5n), z5n + 0.93 * (zsh - z5n)]
    H = zsh - za
    z5a = za + min(0.12, 0.45 * H)
    arch = [za + min(0.035, 0.30 * H), z5a, z5a + 0.30 * (zsh - z5a), z5a + 0.62 * (zsh - z5a),
            z5a + 0.90 * (zsh - z5a)]
    zs = [max(a, b) for a, b in zip(nominal, arch)]
    for i in range(1, 5):
        zs[i] = max(zs[i], zs[i - 1] + 0.002)
    z4, z5, z6, z7, z8 = [min(z, zsh - 0.002 * (5 - i)) for i, z in enumerate(zs)]
    D = zt - zsh
    wsh = w - 0.035
    g0 = (wsh - 0.040, zsh + min(0.02, 0.25 * D))
    rail_x = (1 - c) * (wsh - 0.12) + c * (0.72 - 0.03 * float(smoothstep(1.5, 2.25, y)))
    g2 = (rail_x, zt - min(0.07, 0.30 * D))
    g1 = (0.5 * (g0[0] + g2[0]) + 0.012 * c, 0.5 * (g0[1] + g2[1]))
    g3 = (rail_x - 0.11, zt - min(0.03, 0.15 * D))
    g4 = (0.55 * g3[0], zt - 0.25 * (zt - g3[1]))
    return [
        (0.0, zf),            # 0 floor center
        (wx, zf),             # 1
        (wx, za),             # 2 wheel-well inner wall top
        (w - 0.030, za),      # 3 sill / arch edge
        (w - 0.006, z4),      # 4
        (w + 0.004, z5),      # 5 cladding top
        (w - 0.002, z6),      # 6 mid side
        (w - 0.008, z7),      # 7 lamp band start
        (w - 0.018, z8),      # 8
        (wsh, zsh),           # 9 shoulder
        g0, g1, g2, g3, g4,   # 10..14 greenhouse / hood edge
        (0.0, zt),            # 15 top center
    ]


SMOOTH_RUNS = [(4, 9), (9, 15)]     # profile point runs rounded off (shoulder stays a crisp line)
SUBDIV = 2


def mesh_profile(y):
    """Smoothed half profile for the visual mesh: list of (x, z, band) where band is the
    original profile band of the segment that starts at the point."""
    hp = half_profile(y)
    out = []
    k = 0
    while k < len(hp) - 1:
        run = next((r for r in SMOOTH_RUNS if r[0] <= k < r[1]), None)
        if run is None:
            out.append((hp[k][0], hp[k][1], k))
            k += 1
            continue
        a, b = run
        pts = [np.array(hp[i], float) for i in range(a, b + 1)]
        for i in range(len(pts) - 1):
            p0 = pts[i - 1] if i > 0 else 2 * pts[0] - pts[1]
            p1, p2 = pts[i], pts[i + 1]
            p3 = pts[i + 2] if i + 2 < len(pts) else 2 * pts[-1] - pts[-2]
            for j in range(SUBDIV):
                t = j / SUBDIV
                q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                           + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
                out.append((float(q[0]), float(q[1]), a + i))
        k = b
    out.append((hp[-1][0], hp[-1][1], len(hp) - 1))
    return out


def in_any(y, ranges):
    return any(a <= y <= b for a, b in ranges)


def band_material(band, y, side=1):
    """Material for the loft face band between profile points band and band+1, at mid-station y."""
    if band == 7 and y < HEADLAMP_Y - 0.10:
        return M_SIG_L if side > 0 else M_SIG_R         # side repeaters wrapping round the front corners
    if band <= 2:
        return M_UNDER
    if band in (3, 4):
        return M_TRIM
    if band == 7:
        if y < HEADLAMP_Y:
            return M_HEAD
        if y > TAILLAMP_Y:
            return M_TAIL
    if band == 8 and y > TAILLAMP_Y:
        return M_TAIL
    if 5 <= band <= 9 and any(abs(y - ys) < SEAM_HALF for ys in DOOR_SEAMS):
        return M_TRIM
    if band == 8 and in_any(y, HANDLES):
        return M_TRIM
    if band in (10, 11):
        if SIDE_GLASS[0] <= y <= SIDE_GLASS[1]:
            return M_TRIM if in_any(y, PILLARS) else M_GLASS
        return M_PAINT
    if band in (13, 14):
        if WINDSHIELD[0] <= y <= WINDSHIELD[1] or REAR_GLASS[0] <= y <= REAR_GLASS[1]:
            return M_GLASS
    return M_PAINT


# ----------------------------------------------------------------- mesh helper
class Mesh:
    def __init__(self, name):
        self.name = name
        self.v = []
        self.f = []          # (i, j, k)
        self.m = []          # material per face

    def add_v(self, p):
        self.v.append(tuple(float(c) for c in p))
        return len(self.v) - 1

    def add_tri(self, a, b, c, mat):
        self.f.append((a, b, c))
        self.m.append(mat)

    def add_quad(self, a, b, c, d, mat):
        """a-b-c-d counter-clockwise seen from the side the face should be visible from."""
        self.add_tri(a, b, c, mat)
        self.add_tri(a, c, d, mat)

    def arrays(self):
        return np.array(self.v, float), np.array(self.f, int).reshape(-1, 3), list(self.m)

    def extend(self, other):
        off = len(self.v)
        self.v.extend(other.v)
        self.f.extend([(a + off, b + off, c + off) for a, b, c in other.f])
        self.m.extend(other.m)


def signed_volume(mesh):
    V, F, _ = mesh.arrays()
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    return float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)


def stations():
    ys = []
    for a, b, n in ((Y_FRONT, -1.96, 26), (1.98, Y_REAR, 24)):
        t = (1 - np.cos(np.linspace(0, np.pi / 2, n)))
        if a == Y_FRONT:
            ys += list(a + (b - a) * (1 - t[::-1]))
        else:
            ys += list(a + (b - a) * t)
    ys += list(np.arange(-1.96, 1.98, 0.045))
    for ya in (AXLE_F, AXLE_R):
        ys += list(ya + np.linspace(-ARCH_R + 0.004, ARCH_R - 0.004, 31))
    ys += [WINDSHIELD[0], WINDSHIELD[1], REAR_GLASS[0], REAR_GLASS[1], SIDE_GLASS[0], SIDE_GLASS[1],
           HEADLAMP_Y, TAILLAMP_Y]
    for a, b in PILLARS + HANDLES:
        ys += [a, b]
    ys = sorted(set(round(float(y), 5) for y in ys if Y_FRONT <= y <= Y_REAR))
    out = []
    for y in ys:
        if not out or y - out[-1] > 0.006:
            out.append(y)
    out[0], out[-1] = Y_FRONT, Y_REAR
    # crisp wheel-arch edges: a pair of stations just outside / inside each edge
    edges = []
    for ya in (AXLE_F, AXLE_R):
        for e in (-ARCH_R, ARCH_R):
            for d in (-0.0012, 0.0012):
                edges.append(round(ya + e + d, 6))
    for ys_ in DOOR_SEAMS:
        edges += [ys_ - SEAM_HALF, ys_ + SEAM_HALF]
    out = [y for y in out if min(abs(y - e) for e in edges) > 0.004] + edges
    return sorted(out)


def loop_points(y):
    mp = mesh_profile(y)
    left = [(x, y, z) for x, z, _ in mp]
    right = [(-x, y, z) for x, z, _ in mp[1:-1]][::-1]
    return left + right                                # CCW seen from the front


def loop_bands():
    mp = mesh_profile(0.0)
    bands = [b for _, _, b in mp[:-1]]                 # band of each left segment
    return bands + bands[::-1]


def loop_sides():
    n = len(mesh_profile(0.0)) - 1
    return [1] * n + [-1] * n


def build_body_shell():
    ys = stations()
    mesh = Mesh("shell")
    loops = []
    for y in ys:
        loops.append([mesh.add_v(p) for p in loop_points(y)])
    bands = loop_bands()
    sides = loop_sides()
    n = len(loops[0])
    for s in range(len(ys) - 1):
        ym = 0.5 * (ys[s] + ys[s + 1])
        A, B = loops[s], loops[s + 1]
        for e in range(n):
            e2 = (e + 1) % n
            mesh.add_quad(A[e], B[e], B[e2], A[e2], band_material(bands[e], ym, sides[e]))
    _cap(mesh, ys[0], front=True)
    _cap(mesh, ys[-1], front=False)
    return mesh, ys


def _cap(mesh, y, front):
    mp = mesh_profile(y)
    ncol = 18
    rows = []
    sel = [p for p in mp if p[2] >= 3]           # rows from the sill up to the top center
    z_lo, z_hi = sel[0][1], sel[-1][1]
    peak = 0.085 if front else 0.060             # rounded nose / tail
    for x, z, k in sel:
        t = (z - z_lo) / max(z_hi - z_lo, 1e-6)
        g = max(0.0, float(np.sin(np.pi * np.clip(0.18 + 0.82 * t, 0, 1)))) ** 0.7
        row = []
        for j in range(ncol + 1):
            xx = -x + 2 * x * j / ncol
            u = min(1.0, (xx / x) ** 2) if x > 1e-6 else 0.0
            bul = peak * g * (1.0 - u) ** 0.85
            yy = y - bul if front else y + bul
            row.append((mesh.add_v((xx, yy, z)), xx, z))
        rows.append((k, row))
    for (k, r0), (_, r1) in zip(rows[:-1], rows[1:]):
        for j in range(ncol):
            a, b = r0[j], r0[j + 1]
            c, d = r1[j + 1], r1[j]
            cx = 0.25 * (a[1] + b[1] + c[1] + d[1])
            mat = _cap_material(k, cx, front)
            if front:   # seen from the front (-Y), +x is to the viewer's right
                mesh.add_quad(a[0], b[0], c[0], d[0], mat)
            else:
                mesh.add_quad(a[0], d[0], c[0], b[0], mat)


def _cap_material(band, x, front):
    sig = M_SIG_L if x > 0 else M_SIG_R          # +X is the car's left
    if band <= 4:
        return M_TRIM                 # bumper bottom
    if band == 5:
        return M_TRIM if abs(x) < (0.50 if front else 0.56) else M_PAINT   # intake / diffuser
    if front:
        if band == 7 and abs(x) > 0.64:
            return sig
        if band == 7 and abs(x) > 0.36:
            return M_HEAD
        return M_PAINT
    if band == 8 and abs(x) > 0.68:
        return sig
    if band == 7 and 0.40 < abs(x) < 0.52:
        return M_REV
    if band in (7, 8) and abs(x) > 0.40:
        return M_TAIL
    return M_PAINT


# ----------------------------------------------------------------- profile queries
def surface_z_at(y, x_abs):
    """Height of the upper body surface (shoulder..top) at |x| for station y."""
    hp = half_profile(y)
    up = hp[9:16]   # shoulder .. top center, x decreasing
    xs = [p[0] for p in up][::-1]
    zs = [p[1] for p in up][::-1]
    return float(np.interp(x_abs, xs, zs))


# ----------------------------------------------------------------- details
def _box(mesh, center, size, mat, taper=None):
    """Box centered at center; optional taper shrinks the +x end in y and z."""
    cx, cy, cz = center
    sx, sy, sz = size
    pts = []
    for dx in (-0.5, 0.5):
        for dy in (-0.5, 0.5):
            for dz in (-0.5, 0.5):
                k = taper if (taper is not None and dx > 0) else 1.0
                pts.append((cx + dx * sx, cy + dy * sy * k, cz + dz * sz * k))
    idx = [mesh.add_v(p) for p in pts]

    def I(ix, iy, iz):
        return idx[ix * 4 + iy * 2 + iz]
    mesh.add_quad(I(0, 0, 0), I(0, 0, 1), I(0, 1, 1), I(0, 1, 0), mat)   # -x
    mesh.add_quad(I(1, 0, 0), I(1, 1, 0), I(1, 1, 1), I(1, 0, 1), mat)   # +x
    mesh.add_quad(I(0, 0, 0), I(1, 0, 0), I(1, 0, 1), I(0, 0, 1), mat)   # -y
    mesh.add_quad(I(0, 1, 0), I(0, 1, 1), I(1, 1, 1), I(1, 1, 0), mat)   # +y
    mesh.add_quad(I(0, 0, 0), I(0, 1, 0), I(1, 1, 0), I(1, 0, 0), mat)   # -z
    mesh.add_quad(I(0, 0, 1), I(1, 0, 1), I(1, 1, 1), I(0, 1, 1), mat)   # +z
    return idx


def _transform_tail(mesh, start, rot, origin_from, origin_to):
    """Rotate vertices [start:] about origin_from by rot (3x3, det +1) and move to origin_to."""
    for i in range(start, len(mesh.v)):
        p = np.array(mesh.v[i]) - np.array(origin_from)
        mesh.v[i] = tuple(np.array(origin_to) + rot @ p)


def _rot_x(deg):
    a = np.radians(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _mirror_x(mesh_src, name):
    m = Mesh(name)
    for x, y, z in mesh_src.v:
        m.v.append((-x, y, z))
    for (a, b, c), mat in zip(mesh_src.f, mesh_src.m):
        m.f.append((a, c, b))
        m.m.append(mat)
    return m


def build_mirrors():
    left = Mesh("mirror")
    _box(left, (0.905, -0.665, 1.035), (0.06, 0.13, 0.03), M_TRIM)                  # sail / base
    _box(left, (0.955, -0.650, 1.060), (0.07, 0.05, 0.030), M_TRIM)                 # stalk
    _box(left, (1.025, -0.640, 1.100), (0.12, 0.085, 0.105), M_PAINT, taper=0.80)   # housing
    _box(left, (1.022, -0.596, 1.100), (0.106, 0.004, 0.088), M_CHROME, taper=0.80)  # mirror glass
    left.extend(_mirror_x(left, "mirror_r"))
    return left


def build_roof_rails():
    m = Mesh("rails")
    ys = np.linspace(-0.06, 1.46, 26)
    xc = 0.56
    for side in (1, -1):
        rings = []
        for y in ys:
            zs = surface_z_at(y, xc)
            edge = min(y + 0.06, 1.46 - y)
            lift = 0.030 * float(np.clip(edge / 0.11, 0.35, 1.0))
            z0 = zs + lift
            ring = [(side * (xc - 0.016), y, z0), (side * (xc + 0.016), y, z0),
                    (side * (xc + 0.016), y, z0 + 0.026), (side * (xc - 0.016), y, z0 + 0.026)]
            rings.append([m.add_v(p) for p in ring])
        for r0, r1 in zip(rings[:-1], rings[1:]):
            for e in range(4):
                e2 = (e + 1) % 4
                if side > 0:       # ring is CCW seen from the front
                    m.add_quad(r0[e], r1[e], r1[e2], r0[e2], M_TRIM)
                else:              # mirrored ring is CW seen from the front
                    m.add_quad(r0[e], r0[e2], r1[e2], r1[e], M_TRIM)
        for r, front in ((rings[0], True), (rings[-1], False)):
            if (side > 0) == front:
                m.add_quad(r[0], r[1], r[2], r[3], M_TRIM)
            else:
                m.add_quad(r[0], r[3], r[2], r[1], M_TRIM)
        for y in (-0.03, 1.43):
            zs = surface_z_at(y, xc)
            _box(m, (side * xc, y, zs + 0.025), (0.034, 0.07, 0.05), M_TRIM)
    return m


def vertex_normals(V, F):
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    vn = np.zeros_like(V)
    for k in range(3):
        np.add.at(vn, F[:, k], fn)
    l = np.linalg.norm(vn, axis=1, keepdims=True)
    l[l < 1e-12] = 1
    return vn / l


def build_interior(shell):
    """Inward-facing trim shell for the cabin, firewall, dashboard, seats and a steering wheel."""
    V, F, M = shell.arrays()
    vn = vertex_normals(V, F)
    m = Mesh("interior")
    remap = {}
    cab0, cab1 = -1.10, 2.40
    for (a, b, c), mat in zip(F, M):
        tri = V[[a, b, c]]
        cy = tri[:, 1].mean()
        if not (cab0 <= cy <= cab1) or mat == M_GLASS:
            continue
        if mat == M_UNDER and np.abs(tri[:, 0]).max() > well_x(cy) - 0.01 and tri[:, 2].min() < 0.30:
            continue      # skip sills / well walls near the floor
        ids = []
        for vi in (a, b, c):
            if vi not in remap:
                remap[vi] = m.add_v(V[vi] - vn[vi] * 0.028)
            ids.append(remap[vi])
        m.add_tri(ids[0], ids[2], ids[1], M_INT)       # flipped: visible from inside
    # firewall (faces backward, toward the cabin)
    fw = [m.add_v(p) for p in ((-0.80, -1.06, 0.23), (0.80, -1.06, 0.23), (0.80, -1.06, 0.80), (-0.80, -1.06, 0.80))]
    m.add_quad(fw[0], fw[3], fw[2], fw[1], M_INT)
    # dashboard: sloped block across the cabin
    prof = [(-1.04, 0.76), (-1.04, 0.935), (-0.90, 0.965), (-0.74, 0.955), (-0.64, 0.88), (-0.68, 0.76)]
    xs = (-0.80, 0.80)
    rings = [[m.add_v((x, yy, zz)) for yy, zz in prof] for x in xs]
    n = len(prof)
    for e in range(n):
        e2 = (e + 1) % n
        m.add_quad(rings[0][e], rings[1][e], rings[1][e2], rings[0][e2], M_INT)
    for side, r in ((-1, rings[0]), (1, rings[1])):
        cen = m.add_v((xs[0] if side < 0 else xs[1], -0.84, 0.86))
        for e in range(n):
            e2 = (e + 1) % n
            if side < 0:
                m.add_tri(cen, r[e], r[e2], M_INT)
            else:
                m.add_tri(cen, r[e2], r[e], M_INT)
    # front seats
    for sx in (0.37, -0.37):
        _box(m, (sx, 0.18, 0.42), (0.50, 0.50, 0.14), M_SEAT)
        k = len(m.v)
        _box(m, (0, 0, 0), (0.48, 0.12, 0.62), M_SEAT)
        _transform_tail(m, k, _rot_x(-14), (0, 0, 0), (sx, 0.48, 0.78))
        _box(m, (sx, 0.55, 1.17), (0.26, 0.10, 0.17), M_SEAT)
    # rear bench (between the rear wheel arches)
    _box(m, (0.0, 0.98, 0.44), (1.16, 0.48, 0.14), M_SEAT)
    k = len(m.v)
    _box(m, (0, 0, 0), (1.14, 0.12, 0.60), M_SEAT)
    _transform_tail(m, k, _rot_x(-16), (0, 0, 0), (0.0, 1.24, 0.78))
    for sx in (0.36, -0.36):
        _box(m, (sx, 1.31, 1.14), (0.24, 0.09, 0.15), M_SEAT)
    # center console
    _box(m, (0.0, -0.15, 0.50), (0.24, 0.60, 0.22), M_INT)   # the sliding Universal Island console
    # centre touchscreen (tilted back toward the driver) and a row of real buttons under it
    k = len(m.v)
    _box(m, (0, 0, 0), (0.92, 0.022, 0.17), M_SCREEN)
    _transform_tail(m, k, _rot_x(8), (0, 0, 0), (0.15, -0.69, 1.04))
    _box(m, (0.0, -0.66, 0.84), (0.40, 0.020, 0.060), M_INT)
    for _, _, bx in BUTTONS:
        _box(m, (bx, BUTTON_Y, BUTTON_Z), (0.044, 0.016, 0.028), M_BUTTON)
    m.extend(_steering_wheel((0.37, -0.50, 0.98), tilt_deg=24))
    return m


def _steering_wheel(center, tilt_deg):
    m = Mesh("sw")
    R, r = 0.185, 0.018
    nu, nv = 28, 8
    t = np.radians(tilt_deg)
    ex = np.array([1.0, 0.0, 0.0])
    ez = np.array([0.0, -np.sin(t), np.cos(t)])
    ax = np.cross(ez, ex)            # wheel axis, pointing toward the driver (+Y, up)
    c0 = np.array(center)
    grid = []
    for i in range(nu):
        u = 2 * np.pi * i / nu
        cdir = np.cos(u) * ex + np.sin(u) * ez
        grid.append([m.add_v(c0 + (R + r * np.cos(2 * np.pi * j / nv)) * cdir
                             + r * np.sin(2 * np.pi * j / nv) * ax) for j in range(nv)])
    for i in range(nu):
        for j in range(nv):
            a, b = grid[i][j], grid[(i + 1) % nu][j]
            c, d = grid[(i + 1) % nu][(j + 1) % nv], grid[i][(j + 1) % nv]
            m.add_quad(a, d, c, b, M_TRIM)
    hub = c0 + ax * 0.02
    k = len(m.v)
    _box(m, (0, 0, 0), (0.11, 0.05, 0.09), M_TRIM)
    _transform_tail(m, k, np.stack([ex, ax, ez], axis=1), (0, 0, 0), hub)
    for ang in (0, 180, 270):
        u = np.radians(ang)
        d = np.cos(u) * ex + np.sin(u) * ez
        side = np.cross(d, ax)
        k = len(m.v)
        _box(m, (0, 0, 0), (R * 0.9, 0.012, 0.03), M_TRIM)
        _transform_tail(m, k, np.stack([d, ax, side], axis=1), (0, 0, 0), c0 + d * (R * 0.5))
    return m


# ----------------------------------------------------------------- wheels
def build_rim(name, center, outward):
    """Five-spoke alloy rim. outward=+1 for left wheels (+X), -1 for right wheels."""
    m = Mesh(name)
    cx, cy, cz = center
    s = outward
    nseg = 60

    def P(r, ang, dx):
        return (cx + s * dx, cy + r * np.cos(ang), cz + r * np.sin(ang))

    def ring(r, dx):
        return [m.add_v(P(r, 2 * np.pi * i / nseg, dx)) for i in range(nseg)]

    def strip(r0, r1, mat):
        for i in range(nseg):
            a, b = r0[i], r0[(i + 1) % nseg]
            c, d = r1[(i + 1) % nseg], r1[i]
            if s > 0:
                m.add_quad(a, b, c, d, mat)
            else:
                m.add_quad(a, d, c, b, mat)
    lip_o = ring(0.245, 0.103)
    lip_i = ring(0.226, 0.108)
    barrel_o = ring(0.226, 0.085)
    barrel_i = ring(0.228, -0.105)
    back_o = ring(0.245, -0.108)
    strip(lip_o, lip_i, M_RIM)
    strip(lip_i, barrel_o, M_RIM_DARK)
    strip(barrel_o, barrel_i, M_RIM_DARK)
    strip(barrel_i, back_o, M_RIM_DARK)
    strip(back_o, lip_o, M_RIM_DARK)
    face_r = [ring(r, 0.030) for r in (0.226, 0.17, 0.10, 0.055)]
    for r0, r1 in zip(face_r[:-1], face_r[1:]):
        strip(r0, r1, M_RIM_DARK)
    cen = m.add_v(P(0.0, 0.0, 0.030))
    for i in range(nseg):
        a, b = face_r[-1][i], face_r[-1][(i + 1) % nseg]
        if s > 0:
            m.add_tri(cen, a, b, M_RIM_DARK)
        else:
            m.add_tri(cen, b, a, M_RIM_DARK)
    for k in range(5):
        a0 = 2 * np.pi * k / 5 + np.pi / 2
        rs = np.linspace(0.06, 0.226, 7)
        prof_dx = 0.098 - 0.022 * np.sin(np.linspace(0, np.pi, 7)) ** 1.2
        hw = np.linspace(0.20, 0.085, 7)
        top_l, top_r, bot_l, bot_r = [], [], [], []
        for r, dx, h in zip(rs, prof_dx, hw):
            top_l.append(m.add_v(P(r, a0 + h, dx)))
            top_r.append(m.add_v(P(r, a0 - h, dx)))
            bot_l.append(m.add_v(P(r, a0 + h * 1.08, 0.028)))
            bot_r.append(m.add_v(P(r, a0 - h * 1.08, 0.028)))
        for i in range(len(rs) - 1):
            if s > 0:
                m.add_quad(top_r[i], top_r[i + 1], top_l[i + 1], top_l[i], M_RIM)
                m.add_quad(bot_l[i], top_l[i], top_l[i + 1], bot_l[i + 1], M_RIM)
                m.add_quad(bot_r[i], bot_r[i + 1], top_r[i + 1], top_r[i], M_RIM)
            else:
                m.add_quad(top_r[i], top_l[i], top_l[i + 1], top_r[i + 1], M_RIM)
                m.add_quad(bot_l[i], bot_l[i + 1], top_l[i + 1], top_l[i], M_RIM)
                m.add_quad(bot_r[i], top_r[i], top_r[i + 1], bot_r[i + 1], M_RIM)
    cap = [m.add_v(P(0.062, 2 * np.pi * i / 20, 0.100)) for i in range(20)]
    cc = m.add_v(P(0.0, 0.0, 0.106))
    for i in range(20):
        a, b = cap[i], cap[(i + 1) % 20]
        if s > 0:
            m.add_tri(cc, a, b, M_RIM)
        else:
            m.add_tri(cc, b, a, M_RIM)
    return m


def build_tire(name, center, outward):
    m = Mesh(name)
    cx, cy, cz = center
    s = outward
    nseg = 48
    base = [(0.240, -0.104), (0.262, -0.116), (0.300, -0.121), (0.334, -0.115), (0.351, -0.103),
            (0.358, -0.084), (0.360, -0.055), (0.360, -0.02), (0.360, 0.02), (0.360, 0.055),
            (0.358, 0.084), (0.351, 0.103), (0.334, 0.115), (0.300, 0.121), (0.262, 0.116),
            (0.240, 0.104)]
    # wide performance tire (255 section): tread and sidewall widen, the bead stays on the rim
    grow = TIRE_SECTION / 0.235 - 1.0
    prof = [(r, dx * (1.0 + grow * min(1.0, max(0.0, (r - 0.240) / 0.060)))) for r, dx in base]
    rings = []
    for i in range(nseg):
        ang = 2 * np.pi * i / nseg
        rings.append([m.add_v((cx + s * dx, cy + r * np.cos(ang), cz + r * np.sin(ang))) for r, dx in prof])
    npf = len(prof)
    for i in range(nseg):
        r0, r1 = rings[i], rings[(i + 1) % nseg]
        for j in range(npf - 1):
            a, b, c, d = r0[j], r0[j + 1], r1[j + 1], r1[j]
            if s > 0:
                m.add_quad(a, d, c, b, M_TIRE)
            else:
                m.add_quad(a, b, c, d, M_TIRE)
    return m


WHEELS = {
    "FL": ((WHEEL_X, AXLE_F, WHEEL_Z), 1),
    "FR": ((-WHEEL_X, AXLE_F, WHEEL_Z), -1),
    "RL": ((WHEEL_X, AXLE_R, WHEEL_Z), 1),
    "RR": ((-WHEEL_X, AXLE_R, WHEEL_Z), -1),
}


def build_all():
    shell, ys = build_body_shell()
    body = Mesh("strata_body")
    body.extend(shell)
    body.extend(build_mirrors())
    body.extend(build_roof_rails())
    body.extend(build_interior(shell))
    objects = [body]
    for wn, (c, s) in WHEELS.items():
        objects.append(build_rim("strata_rim_" + wn, c, s))
        objects.append(build_tire("strata_tire_" + wn, c, s))
    return objects, shell
