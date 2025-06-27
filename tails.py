import requests
import os
import numpy as np
import h5py
import pandas as pd
import matplotlib.pyplot as plt

BASE_URL = "https://www.tng-project.org/api/TNG50-1"
API_KEY = "4ff6dd78476d70518200141e4f2e2268"  
HEADERS = {"api-key": API_KEY}

# === Lista de subhalos e snapshot final (último snapshot visível de cada galáxia) ===
GALAXIAS = [
    {"final_snap": 76, "id": 81875},
    {"final_snap": 81, "id": 55542},
    {"final_snap": 80, "id": 56443},
    {"final_snap": 79, "id": 56566},
    {"final_snap": 68, "id": 53742},
    {"final_snap": 82, "id": 97770},
    {"final_snap": 95, "id": 99952},
]

SNAP_INICIAL = 67
os.makedirs("cutouts", exist_ok=True)

def get_main_progenitor(subhalo_id, snap):
    url = f"{BASE_URL}/snapshots/{snap}/subhalos/{subhalo_id}/sublink_descendant/"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200 and r.json():
        return r.json()
    return None

def baixar_cutout(snapshot, subhalo_id):
    path = f"cutouts/snap{snapshot}_subhalo{subhalo_id}.hdf5"
    if os.path.exists(path):
        return path

    url = f"{BASE_URL}/snapshots/{snapshot}/subhalos/{subhalo_id}/cutout.hdf5?gas=Coordinates,StarFormationRate"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        with open(path, "wb") as f:
            f.write(r.content)
        return path
    else:
        print(f"Erro no cutout snapshot {snapshot} subhalo {subhalo_id}: {r.status_code}")
        return None

def get_detalhes(snapshot, subhalo_id):
    url = f"{BASE_URL}/snapshots/{snapshot}/subhalos/{subhalo_id}/"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        return r.json()
    return None

def analisar_sfr_cauda(filepath, centro, limite_disco):
    with h5py.File(filepath, "r") as f:
        if "PartType0" not in f:
            return 0.0

        coords = f["PartType0"]["Coordinates"][:]
        sfr = f["PartType0"]["StarFormationRate"][:]

    mask = sfr > 0
    coords = coords[mask]
    sfr = sfr[mask]
    if len(sfr) == 0:
        return 0.0

    dist = np.linalg.norm(coords - centro, axis=1)
    mask_cauda = dist > limite_disco
    return sfr[mask_cauda].sum()

# === LOOP PRINCIPAL ===
dados = []

for gal in GALAXIAS:
    snap = gal["final_snap"]
    subhalo_id = gal["id"]
    gal_id = f"{subhalo_id}_z{snap}"

    caminho = []
    print(f"\n== Rastreamento da galáxia {gal_id} ==")

    while snap >= SNAP_INICIAL:
        detalhes = get_detalhes(snap, subhalo_id)
        if not detalhes:
            break

        centro = np.array([detalhes["pos_x"], detalhes["pos_y"], detalhes["pos_z"]])
        limite_disco = detalhes.get("halfmassrad_dm", 15.0)

        hdf5_path = baixar_cutout(snap, subhalo_id)
        if not hdf5_path:
            break

        sfr_cauda = analisar_sfr_cauda(hdf5_path, centro, limite_disco)
        dados.append({
            "galaxy": gal_id,
            "snapshot": snap,
            "subhalo_id": subhalo_id,
            "sfr_tail": sfr_cauda
        })

        # Busca o progenitor no snapshot anterior
        prog = get_main_progenitor(subhalo_id, snap)
        if not prog:
            break

        subhalo_id = prog["id"]
        snap = prog["snap"]

# === SALVA EM CSV ===
df = pd.DataFrame(dados)
df.sort_values(by=["galaxy", "snapshot"], inplace=True)
csv_path = "sfr_tails_results_real.csv"
df.to_csv(csv_path, index=False)
print(f"\n📁 Resultados salvos em: {csv_path}")

# === PLOT ===
plt.figure(figsize=(10, 6))
for gal_id, grupo in df.groupby("galaxy"):
    plt.plot(grupo["snapshot"], grupo["sfr_tail"], marker="o", label=gal_id)
plt.xlabel("Snapshot")
plt.ylabel("SFR na Cauda [M☉/yr]")
plt.title("Evolução da SFR na Cauda por Galáxia")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("sfr_tails_evolution_real.png")
plt.show()



