import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Carrega os dados do CSV do gás
df = pd.read_csv('gas_mass_evolution.csv')
df = df.sort_values('redshift')

# Transforma o eixo redshift para espalhar visualmente
transformed_z = np.sqrt(df['redshift'])

plt.figure(figsize=(10,6))

plt.plot(transformed_z, df['mass_gas'], marker='o', color='blue', linewidth=2, markersize=6)

plt.xlabel('Raiz Quadrada do Redshift (sqrt(z))', fontsize=12)
plt.ylabel('Massa de Gás [$10^{10} M_\\odot / h$]', fontsize=12)
plt.title('Evolução da Massa de Gás (Eixo z transformado)', fontsize=14)

plt.gca().invert_xaxis()  # Mantém passado (z alto) à esquerda, presente à direita

y_margin = (df['mass_gas'].max() - df['mass_gas'].min()) * 0.1
plt.ylim(df['mass_gas'].min() - y_margin, df['mass_gas'].max() + y_margin)

plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('gas_mass_evolution_sqrt_redshift.png', dpi=300)
plt.show()

