import pandas as pd
import matplotlib.pyplot as plt

# Carregar o CSV
csv_file = "gemeas_tng100_m200.csv"  # ou outro nome que esteja usando
df = pd.read_csv(csv_file)


# Scatter plot
plt.figure(figsize=(10, 6))
plt.scatter(df['M200c_10^10Msun/h'], df['log10_stellar_mass'], alpha=0.7, edgecolors='k')

plt.xlabel(r"$M_{200c}$ [$10^{10} M_\odot / h$]")
plt.ylabel(r"$\log_{10}(M_*/M_\odot)$")
plt.title("Dispersão de $M_{200c}$ vs $\log_{10}(M_*)$ - TNG50")

plt.grid(True)
plt.tight_layout()
plt.show()
