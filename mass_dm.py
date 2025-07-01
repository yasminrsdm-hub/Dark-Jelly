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

# --- Galaxy List (snapshot final + subhalo ID) ---
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

# --- Output Directory ---
OUTPUT_DIR = 'mass_dm_evolution_TNG50'
os.makedirs(OUTPUT_DIR, exist_ok=True)


# --- Helper Functions ---
def fetch_json(url):
    """Request JSON data with error handling."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


def get_subhalo_data(snap, subhalo_id):
    url = f'{BASE_URL}/snapshots/{snap}/subhalos/{subhalo_id}/'
    return fetch_json(url)


def get_snapshot_redshift(snap):
    url = f'{BASE_URL}/snapshots/{snap}/'
    data = fetch_json(url)
    return data.get('redshift') if data else None


def track_mass_dm(subhalo_id, final_snap):
    """Track dark matter mass backwards in time (from final_snap to earliest progenitor)."""
    snap = final_snap
    mass_dm, redshifts = [], []

    while snap != -1 and subhalo_id != -1:
        data = get_subhalo_data(snap, subhalo_id)
        if data is None:
            break

        mass_dm.append(data.get('mass_dm', None))
        z = get_snapshot_redshift(snap)
        if z is None:
            break
        redshifts.append(z)

        snap = data.get('prog_snap', -1)
        subhalo_id = data.get('prog_sfid', -1)

    return {
        "mass_dm": mass_dm[::-1],
        "redshift": redshifts[::-1]
    }


def save_to_csv(data, subhalo_id, final_snap):
    df = pd.DataFrame(data)
    path = os.path.join(OUTPUT_DIR, f'{subhalo_id}_z{final_snap}_mass_dm.csv')
    df.to_csv(path, index=False)
    return path


def plot_mass_dm(data, subhalo_id, final_snap):
    plt.figure(figsize=(8, 6))
    plt.plot(data["redshift"], data["mass_dm"], marker='o', color='brown')
    plt.xlabel('Redshift (z)')
    plt.ylabel('Dark Matter Mass [$10^{10} M_\\odot / h$]')
    plt.title(f'Dark Matter Mass Evolution\nGalaxy {subhalo_id} (snapshot {final_snap})')
    plt.gca().invert_xaxis()
    plt.grid(True)
    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, f'{subhalo_id}_z{final_snap}_mass_dm.png')
    plt.savefig(path)
    plt.close()
    return path


# --- Main Loop ---
if __name__ == "__main__":
    for gal in tqdm(GALAXIES, desc="Processing galaxies"):
        snap = gal["final_snap"]
        subhalo_id = gal["id"]

        print(f"\n→ Processing galaxy {subhalo_id} (snapshot {snap})")

        data = track_mass_dm(subhalo_id, snap)
        if not data["mass_dm"]:
            print(f"✗ Failed to retrieve data for {subhalo_id}")
            continue

        csv_file = save_to_csv(data, subhalo_id, snap)
        print(f"✓ CSV saved: {csv_file}")

        png_file = plot_mass_dm(data, subhalo_id, snap)
        print(f"✓ Plot saved: {png_file}")
