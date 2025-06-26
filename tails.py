import requests
import os
import h5py
import numpy as np
import matplotlib.pyplot as plt

# === CONFIGURAÇÕES ===
BASE_URL = "https://www.tng-project.org/api/TNG100-1"
SUBHALO_IDS = [
    107813,
    74123,
    96419,
    70711,
    132263,
    108037,
    125033,
    143888,
    124318,
    139737,
    158854,
    141670,
    130203,
    140404,
    124397,
    168847,
    144300,
    148900,
    227576,
    235696,
    281704,
    314772,
]
SNAPSHOT_INI = 67
SNAPSHOT_FIM = 99
API_KEY = "4ff6dd78476d70518200141e4f2e2268"  # sua chave API TNG
HEADERS = {"api-key": API_KEY}

# === Função para baixar detalhes do subhalo (JSON) ===
def baixar_detalhes_subhalo(snapshot, subhalo_id):
    url = f"{BASE_URL}/snapshots/{snapshot}/subhalos/{subhalo_id}/"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        return r.json()
    else:
        raise RuntimeError(f"Erro ao baixar JSON do subhalo {subhalo_id} snapshot {snapshot}: {r.status_code} {r.text}")

# === Baixar cutout ===
def baixar_cutout(snapshot, subhalo_id, output_path):
    if os.path.exists(output_path):
        # Arquivo já existe, não baixa de novo
        return True
    
    fields = "Coordinates,StarFormationRate"
    url = f"{BASE_URL}/snapshots/{snapshot}/subhalos/{subhalo_id}/cutout.hdf5?gas={fields}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(r.content)
        print(f"✅ Cutout baixado para subhalo {subhalo_id} snapshot {snapshot}.")
        return True
    else:
        print(f"Erro ao baixar cutout subhalo {subhalo_id} snapshot {snapshot}: {r.status_code} {r.text}")
        return False

# === Analisar SFR na cauda ===
def analisar_sfr_na_cauda(caminho_hdf5, centro, limite_disco):
    with h5py.File(caminho_hdf5, "r") as f:
        if "PartType0" not in f:
            print("⚠️ Arquivo HDF5 não contém PartType0 (gás).")
            return 0, 0, np.array([])
        if "Coordinates" not in f["PartType0"] or "StarFormationRate" not in f["PartType0"]:
            print("⚠️ PartType0 não contém os campos necessários.")
            return 0, 0, np.array([])

        coords = f["PartType0/Coordinates"][:]  # [N,3], unidades: ckpc/h
        sfr = f["PartType0/StarFormationRate"][:]  # [N], unidades: M☉/yr

    has_sfr = sfr > 0
    coords_sfr = coords[has_sfr]
    sfr_somente = sfr[has_sfr]

    if len(sfr_somente) == 0:
        return 0, 0, np.array([])  # Nenhuma partícula com SFR

    dist_sfr = np.linalg.norm(coords_sfr - centro, axis=1)
    cauda_mask = dist_sfr > limite_disco
    sfr_cauda = sfr_somente[cauda_mask]
    coords_cauda = coords_sfr[cauda_mask]

    return len(sfr_cauda), sfr_cauda.sum(), coords_cauda

# === Plot da SFR na cauda ===
def plotar_sfr_cauda(coords_cauda, sfr_cauda, limite_disco, snapshot, subhalo_id):
    plt.figure(figsize=(6, 6))
    plt.hexbin(coords_cauda[:, 0], coords_cauda[:, 1], C=sfr_cauda,
               gridsize=50, cmap="plasma", bins="log")
    plt.colorbar(label="SFR [M☉/yr]")
    plt.title(f"Subhalo {subhalo_id} - Formação estelar na cauda (snapshot {snapshot})")
    plt.xlabel("x [ckpc/h]")
    plt.ylabel("y [ckpc/h]")
    plt.tight_layout()
    plt.show()

# === Loop principal para todos subhalos e snapshots ===
def main():
    for subhalo_id in SUBHALO_IDS:
        print(f"\n===== Analisando Subhalo {subhalo_id} =====")
        encontrou = False

        for snap in range(SNAPSHOT_INI, SNAPSHOT_FIM + 1):
            print(f"\n🔍 Checando snapshot {snap} para subhalo {subhalo_id}...")

            try:
                detalhes = baixar_detalhes_subhalo(snap, subhalo_id)
            except RuntimeError as e:
                print(e)
                continue

            # Pula snapshots sem gás ou sem SFR
            if detalhes.get("len_gas", 0) == 0 or detalhes.get("sfr", 0) == 0.0:
                print("⚠️ Snapshot sem gás ou sem SFR, pulando.")
                continue

            centro = np.array([detalhes["pos_x"], detalhes["pos_y"], detalhes["pos_z"]])
            limite_disco = detalhes.get("halfmassrad_dm", 15.0)

            output_hdf5 = f"subhalo_{subhalo_id}_snap{snap}_gas.hdf5"
            sucesso = baixar_cutout(snap, subhalo_id, output_hdf5)
            if not sucesso:
                continue

            n_part, sfr_total, coords_cauda = analisar_sfr_na_cauda(output_hdf5, centro, limite_disco)

            if n_part > 0:
                print(f"✅ Encontrada formação estelar na cauda em snapshot {snap}!")
                print(f"Partículas com SFR na cauda: {n_part}")
                print(f"SFR total na cauda: {sfr_total:.3f} M☉/ano")
                plotar_sfr_cauda(coords_cauda, sfr_total * np.ones_like(coords_cauda[:,0]), limite_disco, snap, subhalo_id)
                encontrou = True
                break
            else:
                print(f"⚠️ Nenhuma formação estelar na cauda neste snapshot.")

        if not encontrou:
            print(f"\n❌ Nenhum snapshot de {SNAPSHOT_INI} a {SNAPSHOT_FIM} teve formação estelar na cauda para o subhalo {subhalo_id}.")

if __name__ == "__main__":
    main()

