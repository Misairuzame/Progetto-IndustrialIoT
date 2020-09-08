import math

x = [
0,
1,
2,
3,
4,
5,
6,
7,
8,
9,
10,
11,
12,
13,
14,
15,
16,
17,
18,
19,
20,
21,
22,
23,
24
]

y = [
0.5,
0.5,
0.45,
0.4,
0.38,
0.36,
0.38,
0.58,
1,
1.18,
0.58,
0.38,
0.36,
0.35,
0.34,
0.32,
0.37,
0.4,
0.72,
1.22,
1.7,
1.72,
1.17,
0.75,
0.5
]

def consumption_function(x):
    """
    La funzione assume i valori di interesse nel dominio [0,12].
    Visto che le ore del giorno sono 24, se si vuole passare alla
    funzione un valore compreso fra 0 e 24 (l'ora del giorno),
    basterà poi dividere quel valore per 2, in modo da ottenere
    dei risultati significativi (fuori dal dominio la funzione
    restituisce valori completamente insensati).
    """
    if 0 <= x <= 24:
        return y[round(x)] # Massimo: 1.72
    return "Unsupported"
    


def solar_power_function(x):
    if 0 <= x <= 24:
        x = x/2
        return (12 / math.sqrt(((2 * math.pi) * 1.06**2)) * math.exp(((-(x - 6)**(2))) / ((2 * 1.06**(2)))))
        # Il massimo è circa uguale a 4.5
    return "Unsupported"