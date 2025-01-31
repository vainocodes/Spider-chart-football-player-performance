import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import textwrap


# create a list of excel files
excel_files = ["data/lato.xlsx", "data/kerkez.xlsx", "data/robertson.xlsx"]

# create an empty list for dataframes
dfs = []


# read every excel file and add to the list
for file in excel_files:
    df = pd.read_excel(file)
    df["Player"] = os.path.basename(file).split(".")[0]  # take player name from excel file
    dfs.append(df)

pd.set_option("display.max_rows", None)  # Näyttää kaikki rivit
pd.set_option("display.max_columns", None)  # Näyttää kaikki sarakkeet
pd.set_option("display.width", 1000)  # Estää rivien katkeilua

# add all the player data to one dataframe
df_combined = pd.concat(dfs, ignore_index=True)

# Poistaa rivit, joissa kaikki arvot ovat NaN (paitsi Player-sarake)
df_combined = df_combined.dropna(subset=[col for col in df.columns if col != "Player"], how="all")

# make sure there are numeric values for analysis
# df_combined["Per 90"] = pd.to_numeric(df["Per 90"], errors="coerce")
# df_combined["Percentile"] = pd.to_numeric(df["Percentile"], errors="coerce")


# rename columns to represent 90 minutes and position among players
df_combined = df_combined.rename(columns={"Unnamed: 0": "Statistic", "Unnamed: 1": "Per 90", "Unnamed: 2": "Percentile"})
# print(df_combined.columns)


# print(df.columns)
selected_stats = ["Goals"]

# new "Category" field to map data for spider charts
df_combined["Category"] = np.where(df_combined["Per 90"].isna(), df_combined["Statistic"], np.nan)
df_combined["Category"] = df_combined["Category"].ffill()

# Delete rows not including data we want to use in spider charts
df_combined = df_combined[df_combined["Per 90"].notna()]
df_combined = df_combined[df_combined["Statistic"] != "Statistic"]

# print(df_combined)


def wrap_text(text, width=10):
    """Jakaa pitkän tekstin usealle riville."""
    return "\n".join(textwrap.wrap(text, width))


# !!!!!! creating the SPIDER CHART !!!!!! (this one for 1 player only)
def create_spider_chart(df_combined, player, category):
    # Suodata data valitun pelaajan ja kategorian mukaan
    player_data = df_combined[(df_combined["Player"] == player) & (df_combined["Category"] == category)]

    if player_data.empty:
        print(f"Ei dataa pelaajalle {player} kategoriassa {category}")
        return


    # Ota tilastot ja arvot
    categories = player_data["Statistic"].values
    values = player_data["Percentile"].values

    # make sure the values are correct!
    print(f"Tilastojen määrä: {len(categories)}, Arvojen määrä: {len(values)}")

    # Sulje ympyrä
    num_vars = len(categories)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # Luo Spider Chart
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.fill(angles, values, alpha=0.25, color="blue")
    ax.plot(angles, values, linewidth=2, linestyle="solid", color="blue")


    # Aseta kategoriat ja asteikko
    ax.set_xticks(angles)
    ax.set_xticklabels(categories, fontsize=10)

    # make sure the values are correct!
    print(f"Tilastojen määrä: {len(categories)}, Arvojen määrä: {len(values)}")

    ax.set_yticks(range(0, 101, 20))
    ax.set_yticklabels(["0", "20", "40", "60", "80", "100"], fontsize=10)

    ax.set_title(f"{player} - {category}", size=14, fontweight="bold")



    plt.show()



# create spider cart for many players
def compare_players(dafa, players, category):
    categories = dafa[dafa["Category"] == category]["Statistic"].unique()
    num_vars = len(categories)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles.append(angles[0])  # close the circle

    fig, ax = plt.subplots(figsize=(12, 14), subplot_kw=dict(polar=True))  # **Suurempi kuva**
    fig.subplots_adjust(top=0.75)  # **Lisää tilaa taulukolle**

    colors = {
        "lato": "#ff9800",
        "kerkez": "#8B0000",  # Punainen
        "robertson": "#1f77b4"  # Sininen
    }        # Pelaajakohtaiset värit

    table_data = []  # Tallennetaan taulukon data
    row_colors = []

    for i, player in enumerate(players):
        player_data = dafa[(dafa["Player"] == player) & (dafa["Category"] == category)]

        values = player_data["Percentile"].values
        values = np.append(values, values[0])  # Suljetaan ympyrä

        # Määritetään, missä täyttö alkaa (0 -> 100, mutta ei alle 0)
        masked_values = np.maximum(values, 0)  # Kaikki alle 0 muuttuu 0:ksi

        # **Tallenna taulukkoon**
        table_data.append([player] + list(values[:-1]))  # Poistetaan viimeinen arvo (ylimääräinen kopio)
        row_colors.append(colors[player])  # Lisää pelaajan väri riviin

        ax.scatter(angles, values, color=colors[player], s=50, zorder=3)
        ax.plot(angles, masked_values, linewidth=2, linestyle="solid", label=player, color=colors[player])
        ax.fill(angles, masked_values, alpha=0.25, color=colors[player])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)

    ax.set_ylim(-20, 100)
    ax.set_yticks([-20, 0, 20, 40, 60, 80, 100])
    ax.set_yticklabels(["", "", "", "", "", "", ""], fontsize=10)

    ax.spines['polar'].set_visible(False)
    ax.grid(color="grey", linestyle="--", linewidth=0.8)
    ax.set_facecolor("white")

    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

    ax.yaxis.grid(True, linestyle="dashed", linewidth=0.3, alpha=0.3)

    # **🔹 Lisätään taulukko yläpuolelle**
    col_labels = ["Player"] + [wrap_text(label, width=12) for label in categories]
    table = plt.table(cellText=table_data, colLabels=col_labels, loc="top", cellLoc="center",
                      bbox=[-0.5, 1.10, 2, 0.25])

    for cell in table.get_celld().values():
        cell.set_facecolor("#FFF5F7")
    table.auto_set_font_size(False)
    table.set_fontsize(6.5)
    for key, cell in table.get_celld().items():
        cell.set_linewidth(0)

    # **Värjää taulukon solut pelaajan värin mukaan**
    for row_idx, player in enumerate(players, start=1):  # Aloitetaan rivit indeksistä 1 (otsikko ei värjätä)
        for col_idx in range(len(col_labels)):
            cell = table[row_idx, col_idx]
            cell.set_text_props(color=colors[player])  # Nyt tekstin väri on pelaajan väri

    # background colour
    fig.patch.set_facecolor("#FFFAFA")
    # spider chart colour
    ax.set_facecolor("#FADADD")

    plt.show()

# Kokeile Spider Chartia yhdelle pelaajalle ja yhdelle kategorialle
# create_spider_chart(df_combined, "kerkez", "Passing")

# Testaa useamman pelaajan vertailua kategoriassa "Standard Stats"
compare_players(df_combined, ["lato", "kerkez", "robertson"], "Standard Stats")