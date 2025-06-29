import requests
import numpy as np
import matplotlib.pyplot as plt
from time import sleep
import pandas as pd
import csv

# Arquivo CSV gerado
arquivo_csv = "jellyfish_local100.csv"

snapshot_range = range(67, 100)  # Snapshots de 68 até 99

# Função para obter a massa estelar via API
BASE_URL = "http://www.tng-project.org/api/TNG100-1"
HEADERS = {"api-key": ""}

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

# Ler CSV e filtrar jellyfish entre snapshots 68 e 99
df = pd.read_csv(arquivo_csv)

jellyfish_df = df[(df['JellyfishFlag'] == 1) & (df['SnapNum'].isin(snapshot_range))]

print(f"Total de galáxias jellyfish entre snaps 67-99: {len(jellyfish_df)}")

jellyfish_ids = list(zip(jellyfish_df['SnapNum'], jellyfish_df['SubfindID']))

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

    if (i + 1) % 50 == 0 or (i + 1) == len(jellyfish_ids):
        print(f"{i + 1}/{len(jellyfish_ids)} processadas")

# Salvar galáxias gêmeas
if gemeas:
    with open("jellyfish_gemeas_massas_TNG100.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["snapshot", "subhalo_id", "log10_stellar_mass"])
        writer.writerows(gemeas)
    print(f"{len(gemeas)} galáxias gêmeas salvas em 'jellyfish_gemeas_massas_TNG100.csv'")
else:
    print("Nenhuma galáxia gêmea encontrada na faixa da massa da F0083.")

# Plot do histograma
plt.figure(figsize=(10, 6))
plt.hist(todas_massas, bins=40, color='skyblue', edgecolor='black')
plt.axvline(F0083_MASS, color='red', linestyle='--', label=f'F0083 (log M* = {F0083_MASS})')
plt.axvspan(F0083_MASS - TOLERANCE, F0083_MASS + TOLERANCE, color='red', alpha=0.2, label=f'F0083 ± {TOLERANCE}')
plt.xlabel('log$_{10}$(M*/M$_\odot$)')
plt.ylabel('Número de galáxias jellyfish')
plt.title('Distribuição de massas estelares das jellyfish no TNG100 (z ≤ 0.5)')
plt.legend()
plt.tight_layout()
plt.savefig("histograma_massas_jellyfish_TNG100.png")
plt.show()

