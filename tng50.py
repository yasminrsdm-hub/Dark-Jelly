import requests
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from time import sleep
import csv

# Parâmetros
CSV_ARQUIVO = "jellyfish_local50.csv"  # Substitua pelo nome correto do seu CSV
snapshot_range = range(67, 100)  # Snapshots 68 até 99

# Função para obter a massa estelar via API
BASE_URL = "http://www.tng-project.org/api/TNG50-1"
HEADERS = {"api-key": "4ff6dd78476d70518200141e4f2e2268"}  

def get_stellar_mass(snapshot, subhalo_id):
    url = f"{BASE_URL}/snapshots/{snapshot}/subhalos/{subhalo_id}/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        mass_stars = data["mass_stars"] * 1e10  # M☉
        return np.log10(mass_stars)
    except Exception as e:
        print(f"Erro em snapshot {snapshot}, subhalo {subhalo_id}: {e}")
        return None

# Lê a tabela CSV
df = pd.read_csv(CSV_ARQUIVO)

# Filtra apenas snapshots entre 68 e 99 e que são jellyfish
df_jelly = df[(df['SnapNum'] >= 67) & (df['SnapNum'] <= 99) & (df['JellyfishFlag'] == 1)]

# Obtém listas de SnapNum e SubfindID
snaps = df_jelly['SnapNum'].values
ids = df_jelly['SubfindID'].values

print("Total de galáxias jellyfish entre snaps 67-99:", len(ids))
print("Exemplo (snapshot, subhalo_id):")
for i in range(min(5, len(ids))):
    print(snaps[i], ids[i])

jellyfish_ids = list(zip(snaps, ids))

# Parâmetros da F0083
F0083_MASS = 10.25
TOLERANCE = 0.07

todas_massas = []
gemeas = []

print(f"Processando {len(jellyfish_ids)} galáxias jellyfish...")

for i, (snap, sub_id) in enumerate(jellyfish_ids):
    log_mass = get_stellar_mass(snap, sub_id)
    if log_mass is not None:
        todas_massas.append(log_mass)
        if (F0083_MASS - TOLERANCE) <= log_mass <= (F0083_MASS + TOLERANCE):
            gemeas.append((snap, sub_id, log_mass))
    sleep(0.2)  # evitar excesso de requisições

    if (i+1) % 50 == 0 or (i+1) == len(jellyfish_ids):
        print(f"{i+1}/{len(jellyfish_ids)} processadas")

# Salvar gêmeas se houver
if gemeas:
    with open("jellyfish_gemeas_massas.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["snapshot", "subhalo_id", "log10_stellar_mass"])
        writer.writerows(gemeas)
    print(f"{len(gemeas)} galáxias gêmeas salvas em 'jellyfish_gemeas_massas.csv'")
else:
    print("Nenhuma galáxia gêmea encontrada na faixa da massa da F0083.")

# Plot do histograma
plt.figure(figsize=(10, 6))
plt.hist(todas_massas, bins=40, color='skyblue', edgecolor='black')
plt.axvline(F0083_MASS, color='red', linestyle='--', label=f'F0083 (log M* = {F0083_MASS})')
plt.axvspan(F0083_MASS - TOLERANCE, F0083_MASS + TOLERANCE, color='red', alpha=0.2, label=f'F0083 ± {TOLERANCE}')
plt.xlabel('log$_{10}$(M*/M$_\odot$)')
plt.ylabel('Número de galáxias jellyfish')
plt.title('Distribuição de massas estelares das jellyfish no TNG50 (z ≤ 0.5)')
plt.legend()
plt.tight_layout()
plt.savefig("histograma_massas_jellyfish_TNG50.png")
plt.show()

