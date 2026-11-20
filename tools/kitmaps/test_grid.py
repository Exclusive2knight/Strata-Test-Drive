# a 3 x 3 grid of four-lane streets: intersections joined by 96 + 48 m straights, so every loop closes exactly
N = 3
X = {}
X[0, 0] = K.start("x_city4_4way", 0, 0, 0)
def link(a, leg, back):
    s1 = K.add("city4_st96", a[leg]); s2 = K.add("city4_st48", s1["out"])
    return s2["out"]
for j in range(N):
    for i in range(N):
        if (i, j) not in X:
            if i > 0:
                end = link(X[i - 1, j], "leg_E", "leg_W"); X[i, j] = K.add("x_city4_4way", end, via="leg_W")
            else:
                end = link(X[i, j - 1], "leg_N", "leg_S"); X[i, j] = K.add("x_city4_4way", end, via="leg_S")
# the remaining north-south links between rows (the joints at the far end are checked by K.check)
for j in range(N - 1):
    for i in range(1, N):
        link(X[i, j], "leg_N", "leg_S")
