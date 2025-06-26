import pandas as pd
import matplotlib.pyplot as plt

# Carregar CSVs
df_stars = pd.read_csv('galaxy_evolution.csv')
df_gas = pd.read_csv('gas_mass_evolution.csv')

# Verificar colunas dos arquivos
print('Colunas em galaxy_evolution.csv:', df_stars.columns)
print('Colunas em gas_mass_evolution.csv:', df_gas.columns)

# Supondo que colunas relevantes sejam: 'redshift' e 'mass_stars' em df_stars
# e 'redshift' e 'mass_gas' em df_gas
# Faça merge pelos valores próximos de redshift
df_merged = pd.merge(df_stars, df_gas, on='redshift', how='inner')

# Calcular a razão massa_gas / massa_stars com cuidado para evitar divisão por zero
def safe_ratio(row):
    ms = row.get('mass_stars', None)
    mg = row.get('mass_gas', None)
    if pd.isna(ms) or ms == 0 or pd.isna(mg):
        return None
    return mg / ms

df_merged['gas_to_stars_ratio'] = df_merged.apply(safe_ratio, axis=1)

# Plotar
fig, axs = plt.subplots(3, 1, figsize=(10, 14), sharex=True)

axs[0].plot(df_merged['redshift'], df_merged['mass_stars'], marker='o', color='blue')
axs[0].set_ylabel('Massa Estelar\n[$10^{10} M_\\odot / h$]')

axs[1].plot(df_merged['redshift'], df_merged['mass_gas'], marker='o', color='purple')
axs[1].set_ylabel('Massa de Gás\n[$10^{10} M_\\odot / h$]')

axs[2].plot(df_merged['redshift'], df_merged['gas_to_stars_ratio'], marker='o', color='black')
axs[2].set_ylabel('Razão Massa Gás / Massa Estelar')
axs[2].set_xlabel('Redshift (z)')
axs[2].axhline(1, color='red', linestyle='--', label='Razão = 1')
axs[2].legend()

for ax in axs:
    ax.grid(True)
    ax.invert_xaxis()

plt.suptitle('Evolução das Massas Estelar, Gasosa e Razão Gás/Estrelas')
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('mass_gas_stars_ratio_evolution_merged.png')
plt.show()

print('Gráfico salvo como mass_gas_stars_ratio_evolution_merged.png')

