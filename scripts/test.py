import numpy as np

U = 30
B = 1.49e-11
L = 500 * 1000
L_r = 1000

c = U - ((B * (L ** 2)) / (4 * np.pi ** 2))
print(c)

c = U - (B / (np.pi ** 2 * ((4 / L ** 2) + (1 / L_r ** 2))))
print(c)


P2 = 50
P1 = 100
T = 273.15
r = 10 / 1000
Tv = T * (1 + 0.61 * r)
a = 29.3

z = a * Tv * np.log(P1 / P2)
print(z, " m")


T = 35 + 273.15
a = 0.61
r = 30 / 1000
rL = 0
ri = 0

Tv = T * (1 + (a * r) - rL - ri)

print("Tv ", Tv - 273.15)


fc = 1.45e-4 * np.sin()

IVP = (tilr + fc) / rho * ()
