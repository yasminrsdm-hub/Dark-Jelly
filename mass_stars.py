import requests
import matplotlib.pyplot as plt
import pandas as pd
import os
from tqdm import tqdm

# --- API Configuration ---
BASE_URL = 'https://www.tng-project.org/api/TNG100-1'
API_TOKEN = ''

HEADERS = {
    'Accept': 'application/json',
    'api-key': API_TOKEN
}

# --- Galaxy list ---
GALAXIES = [
    {"final_snap": 67, "id": 107813},
    {"final_snap": 67, "id": 74123},
    {"final_snap": 72, "id": 96419},
    {"final_snap": 72, "id": 70711},
    {"final_snap": 84, "id": 132263},
    {"final_snap": 99, "id": 108037},
    {"final_snap": 99, "id": 125033},
    {"final_snap": 99, "id": 143888},
    {"final_snap": 91, "id": 124318},
    {"final_snap": 91, "id": 139737},
    {"final_snap": 99, "id": 158854},
    {"final_snap": 91, "id": 141670},
    {"final_snap": 84, "id": 130203},
    {"final_snap": 84, "id": 140404},
    {"final_snap": 78, "id": 124397},
    {"final_snap": 91, "id": 168847},
    {"final_snap": 84, "id": 144300},
    {"final_snap": 78, "id": 148900},
    {"final_snap": 99, "id": 227576},
    {"final_snap": 99, "id": 235696},
    {"final_snap": 99, "id": 281704},
    {"final_snap": 99, "id": 314772}
]

OUTPUT_DIR = 'stellar_properties_evolution'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_json(url):
    """Fetch JSON data with error handling."""
    try:
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


def get_subhalo_data(snap, subhalo_id):
    return fetch_json(f'{BASE_URL}/snapshots/{snap}/subhalos/{subhalo_id}/')


def get_snapshot_redshift(snap):
    data = fetch_json(f'{BASE_URL}/snapshots/{snap}/')
    return data.get('redshift') if data else None


def track_galaxy(subhalo_id, final_snap):
    """Track galaxy backward in time through progenitors."""
    snap = final_snap
    stellar_mass, sfr, metallicity, half_mass_radius, redshifts = [], [], [], [], []

    while snap != -1 and subhalo_id != -1:
        data = get_subhalo_data(snap, subhalo_id)
        if data is None:
            break

        stellar_mass.append(data.get('mass_stars'))
        sfr.append(data.get('sfr'))
        metallicity.append(data.get('starmetallicity'))
        half_mass_radius.append(data.get('halfmassrad_stars'))

        z = get_snapshot_redshift(snap)
        if z is None:
            break
        redshifts.append(z)

        snap = data.get('prog_snap', -1)
        subhalo_id = data.get('prog_sfid', -1)

    # Invert to chronological order
    return {
        "redshift": redshifts[::-1],
        "stellar_mass": stellar_mass[::-1],
        "sfr": sfr[::-1],
        "metallicity": metallicity[::-1],
        "half_mass_radius": half_mass_radius[::-1]
    }


def save_data_to_csv(data, subhalo_id, snap):
    df = pd.DataFrame(data)
    path = os.path.join(OUTPUT_DIR, f'{subhalo_id}_z{snap}_stellar_properties.csv')
    df.to_csv(path, index=False)
    return path


def plot_properties(data, subhalo_id, snap):
    fig, axs = plt.subplots(4, 1, figsize=(10, 14), sharex=True)

    axs[0].plot(data["redshift"], data["stellar_mass"], 'o-', color='blue')
    axs[0].set_ylabel('Stellar Mass\n[$10^{10} M_\\odot / h$]')
    axs[0].grid(True)

    axs[1].plot(data["redshift"], data["sfr"], 'o-', color='green')
    axs[1].set_ylabel('Star Formation Rate\n[$M_\\odot / yr$]')
    axs[1].grid(True)

    axs[2].plot(data["redshift"], data["metallicity"], 'o-', color='orange')
    axs[2].set_ylabel('Stellar Metallicity')
    axs[2].grid(True)

    axs[3].plot(data["redshift"], data["half_mass_radius"], 'o-', color='red')
    axs[3].set_ylabel('Half-Mass Radius\n[ckpc/h]')
    axs[3].set_xlabel('Redshift (z)')
    axs[3].invert_xaxis()
    axs[3].grid(True)

    plt.suptitle(f'Evolution of Galaxy Properties\nSubhalo {subhalo_id} (Final snapshot: {snap})')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig_path = os.path.join(OUTPUT_DIR, f'{subhalo_id}_z{snap}_stellar_properties.png')
    plt.savefig(fig_path)
    plt.close()
    return fig_path


# --- Main Loop ---
if __name__ == "__main__":
    for gal in tqdm(GALAXIES, desc="Processing galaxies"):
        subhalo_id = gal["id"]
        snap = gal["final_snap"]

        print(f"\n→ Galaxy {subhalo_id} (Snapshot {snap})")

        data = track_galaxy(subhalo_id, snap)
        if not data["redshift"]:
            print(f"✗ Failed to track galaxy {subhalo_id}")
            continue

        csv_file = save_data_to_csv(data, subhalo_id, snap)
        print(f"✓ Saved CSV: {csv_file}")

        plot_file = plot_properties(data, subhalo_id, snap)
        print(f"✓ Saved plot: {plot_file}")
