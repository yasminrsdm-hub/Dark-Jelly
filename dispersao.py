import pandas as pd
import matplotlib.pyplot as plt

# Carregar o CSV
csv_file = "gemeas_tng100_m200.csv"
df = pd.read_csv(csv_file)

# Scatter plot
plt.figure(figsize=(12, 7))

# Todos os pontos
plt.scatter(df['M200c_10^10Msun/h'], df['log10_stellar_mass'], alpha=0.7, edgecolors='k', label='Galáxias')

# Anotar subhalo_id em cada ponto
for idx, row in df.iterrows():
    plt.annotate(str(row['subhalo_id']),
                 (row['M200c_10^10Msun/h'], row['log10_stellar_mass']),
                 textcoords="offset points", xytext=(5,5), ha='left', fontsize=8)

# Linha do A2744
plt.axvline(250000, color='black', linestyle='--', label='A2744')

plt.xlabel(r"$M_{200c}$ [$10^{10} M_\odot / h$]")
plt.ylabel(r"$\log_{10}(M_*/M_\odot)$")
plt.title("Dispersão de $M_{200c}$ vs $\log_{10}(M_*)$ - TNG100")

plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

