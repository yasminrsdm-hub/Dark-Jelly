import pandas as pd
import matplotlib.pyplot as plt

# Seu dataframe com a coluna 'snapshot'
df = pd.read_csv('gemeas_com_grupos100.csv')

# Dicionário snapshot → redshift baseado na sua tabela
snapshot_to_z = {
    67: 0.50, 68: 0.48, 69: 0.46, 70: 0.44, 71: 0.42, 72: 0.40,
    73: 0.38, 74: 0.36, 75: 0.35, 76: 0.33, 77: 0.31, 78: 0.30,
    79: 0.27, 80: 0.26, 81: 0.24, 82: 0.23, 83: 0.21, 84: 0.20,
    85: 0.18, 86: 0.17, 87: 0.15, 88: 0.14, 89: 0.13, 90: 0.11,
    91: 0.10, 92: 0.08, 93: 0.07, 94: 0.06, 95: 0.05, 96: 0.03,
    97: 0.02, 98: 0.01, 99: 0.00
}

# Criar uma nova coluna no dataframe com o redshift usando o dicionário
df['redshift'] = df['snapshot'].map(snapshot_to_z)

# Agora faça o histograma da contagem de galáxias por redshift
plt.figure(figsize=(10,6))
plt.hist(df['redshift'], bins=len(snapshot_to_z), edgecolor='k', alpha=0.7)
plt.xlabel('Redshift (z)')
plt.ylabel('Número de galáxias')
plt.title('Histograma de galáxias por redshift (snapshots 67 a 99), TNG100')
plt.gca().invert_xaxis()  # Inverter eixo x para mostrar z decrescente (opcional)
plt.show()


