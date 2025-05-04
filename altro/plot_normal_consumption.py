import plotille

# Ore della giornata
hours = list(range(24))

# Consumo simulato in kWh
consumption = [
    0.4,
    0.3,
    0.3,
    0.3,
    0.4,
    0.6,  # 0–5
    0.8,
    1.2,
    1.0,
    0.6,
    0.5,
    0.4,  # 6–11
    0.3,
    0.3,
    0.4,
    0.5,
    0.7,
    1.5,  # 12–17
    2.0,
    2.2,
    1.8,
    1.2,
    0.8,
    0.5,  # 18–23
]

# old values
# consumption = [
#     0.5,
#     0.5,
#     0.45,
#     0.4,
#     0.38,
#     0.36,
#     0.38,
#     0.58,
#     1,
#     1.18,
#     0.58,
#     0.38,
#     0.36,
#     0.35,
#     0.34,
#     0.32,
#     0.37,
#     0.4,
#     0.72,
#     1.22,
#     1.7,
#     1.72,
#     1.17,
#     0.75,
# ]

fig = plotille.Figure()
fig.width = 80
fig.height = 20
fig.x_labels = [str(h) for h in hours]
fig.set_x_limits(min_=0, max_=23)
fig.set_y_limits(min_=0, max_=2.5)
fig.color_mode = "byte"
fig.plot(hours, consumption, label="Consumo kWh")

print(fig.show(legend=True))
