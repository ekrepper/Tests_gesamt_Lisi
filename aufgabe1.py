import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as patches

# ----------------------------------------------------------
# 1) Graph (Knoten + Kanten)
# ----------------------------------------------------------
G = nx.DiGraph()

nodes = {
    "Mikrocontroller":        (5, 0),
    "Qwiic-Kabel":            (5, 3),
    "ADC":                    (5, 6),
    "Jumper Kabel":           (5, 9),
    "EMG-Sensor + 4er Kabel": (5, 12),

    "Elektrode Weiß":         (4.48, 15), 
    "Elektrode Rot":          (4.8, 15),
    "Elektrode Schwarz":      (5.7, 15),

    "GND":                    (4.7, 10),
    "3.3V":                   (5.0, 10),
    "A0":                     (5.3, 10),

    "Mikro-USB-Kabel":        (7.5, 0),
}

edges = [
    ("EMG-Sensor + 4er Kabel", "Mikrocontroller"),
    ("Mikrocontroller", "Jumper Kabel"),
    ("EMG-Sensor + 4er Kabel", "GND"),
    ("EMG-Sensor + 4er Kabel", "3.3V"),
    ("EMG-Sensor + 4er Kabel", "A0"),
    ("Elektrode Weiß", "EMG-Sensor + 4er Kabel"),
    ("Elektrode Rot", "EMG-Sensor + 4er Kabel"),
    ("Elektrode Schwarz", "EMG-Sensor + 4er Kabel"),
    ("Mikrocontroller", "Mikro-USB-Kabel"),
    ("Jumper Kabel", "GND"),
    ("Jumper Kabel", "3.3V"),
    ("Jumper Kabel", "A0"),
    ("Qwiic-Kabel", "Mikrocontroller"),
    ("ADC", "Qwiic-Kabel"),
]

G.add_nodes_from(nodes.keys())
G.add_edges_from(edges)

node_colors = {
    "Mikrocontroller":        "lightblue",
    "Qwiic-Kabel":            "purple",
    "ADC":                    "orange",
    "Jumper Kabel":           "gray",
    "EMG-Sensor + 4er Kabel": "tomato",
    "Elektrode Rot":          "red",
    "Elektrode Schwarz":      "black",
    "GND":                    "black",
    "3.3V":                   "red",
    "A0":                     "yellow",
    "Mikro-USB-Kabel":        "gray",
}

node_labels = {
    "Mikrocontroller":         "Mikrocontroller",
    "Qwiic-Kabel":             "Qwiic\nKabel",
    "ADC":                     "ADC",
    "Jumper Kabel":            "Jumper Kabel",
    "EMG-Sensor + 4er Kabel":  "EMG-Sensor\nverbunden mit\n4er Kabel",
    "Elektrode Weiß":          "Elektrode\nWeiß",
    "Elektrode Rot":           "Elektrode\nRot",
    "Elektrode Schwarz":       "Elektrode\nSchwarz",
    "GND":                     "GND",
    "3.3V":                    "3.3V",
    "A0":                      "A0",
    "Mikro-USB-Kabel":         "Mikro-USB\nKabel",
}

plt.figure(figsize=(12, 10))

# 1) Alle außer "Elektrode Weiß"
main_nodes = [n for n in nodes if n not in ["GND", "3.3V", "A0", "Elektrode Weiß"]]

nx.draw_networkx_nodes(
    G,
    nodes,
    nodelist=main_nodes,
    node_color=[node_colors[n] for n in main_nodes],
    node_shape="s",
    node_size=3000
)

# 2) GND, 3.3V, A0 (kleine Kreise)
nx.draw_networkx_nodes(
    G,
    nodes,
    nodelist=["GND", "3.3V", "A0"],
    node_color=[node_colors[n] for n in ["GND", "3.3V", "A0"]],
    node_shape="o",
    node_size=1000
)

# 3) "Elektrode Weiß" separat mit Rahmen
nx.draw_networkx_nodes(
    G,
    nodes,
    nodelist=["Elektrode Weiß"],
    node_color="white",        
    node_shape="s",
    node_size=3000,
    linewidths=1,             
    edgecolors="black"        
)

# Labels
for node, (x, y) in nodes.items():
    text_color = "white" if node in ["Elektrode Schwarz", "GND"] else "black"
    plt.text(
        x, y,
        node_labels[node],
        fontsize=9,
        fontweight="bold",
        ha="center",
        va="center",
        color=text_color
    )

# Kanten
nx.draw_networkx_edges(
    G,
    nodes,
    edgelist=edges,
    arrows=False,
    edge_color="black",
    connectionstyle="arc3,rad=0.0"
)

# ----------------------------------------------------------
# Ellipsen (Oberarm & Unterarm) + Beschriftungen
# ----------------------------------------------------------
ax = plt.gca()

ellipse_oberarm = patches.Ellipse(
    (4.5, 15),
    width=1.1,
    height=1.6,
    angle=0,
    facecolor="#fcd5b5",
    edgecolor="brown",
    linewidth=2,
    alpha=0.8
)
ax.add_patch(ellipse_oberarm)
# Beschriftung Oberarm (z. B. etwas höher als das Ellipsen-Zentrum)
plt.text(
    4.15, 15,  # leicht über dem Mittelpunkt
    "Oberarm",
    fontsize=10,
    fontweight="bold",
    color="brown",
    ha="center",
    va="bottom"
)

ellipse_unterarm = patches.Ellipse(
    (5.39, 15),
    width=0.9,
    height=1.4,
    angle=0,
    facecolor="#fcd5b5",
    edgecolor="brown",
    linewidth=2,
    alpha=0.8
)
ax.add_patch(ellipse_unterarm)
# Beschriftung Unterarm
plt.text(
    5.25, 15,  # leicht über dem Mittelpunkt
    "Unterarm",
    fontsize=10,
    fontweight="bold",
    color="brown",
    ha="center",
    va="bottom"
)

plt.axis("off")
plt.tight_layout()

# 4) Achsen anpassen - HERUNTERZOOMEN
# ----------------------------------------------------------
all_x = [coord[0] for coord in nodes.values()]
all_y = [coord[1] for coord in nodes.values()]

x_min, x_max = min(all_x), max(all_x)
y_min, y_max = min(all_y), max(all_y)

# Wähle z. B. 1.0 als Rand
margin = 1
plt.xlim(x_min - margin, x_max + margin)
plt.ylim(y_min - margin, y_max + margin)

plt.savefig("Tragbares-System-Diagramm.svg", format="svg")
plt.show()
