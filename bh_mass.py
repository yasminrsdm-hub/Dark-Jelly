import requests
import matplotlib.pyplot as plt
import pandas as pd
import os

# --- Configuration ---
base_url = 'http://www.tng-project.org/api/TNG100-1'
token = ''  # insert your valid token here

headers = {
    'Accept': 'application/json',
    'api-key': token
}

# --- List of galaxies (final snapshot and subhalo ID at that snapshot) ---
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

# --- Helper functions ---

def get_subhalo_data(snap, subhalo_id):
    url = f'{base_url}/snapshots/{snap}/subhalos/{subhalo_id}/'
    r = requests.get(url, headers=headers, verify=False)
    if r.status_code == 200:
        return r.json()
    else:
        print(f'Error fetching snapshot {snap}, subhalo {subhalo_id}:', r.status_code)
        return None

def get_snapshot_redshift(snap):
    url = f'{base_url}/snapshots/{snap}/'
    r = requests.get(url, headers=headers, verify=False)
    if r.status_code == 200:
        return r.json()['redshift']
    else:
        print(f'Error fetching snapshot {snap}:', r.status_code)
        return None

# --- Output directory ---
output_dir = 'bh_mass_evolution_list'
os.makedirs(output_dir, exist_ok=True)

# --- Main loop for each galaxy ---
for gal in GALAXIES:
    snap = gal['final_snap']
    subhalo = gal['id']

    bh_mass = []
    redshifts = []

    print(f'\nTracking BH mass for galaxy {subhalo} from snapshot {snap} back to 67...')

    while snap != -1 and subhalo != -1 and snap >= 67:
        print(f'  -> Snap {snap}, Subhalo {subhalo}')
        data = get_subhalo_data(snap, subhalo)
        if data is None:
            break

        bh_mass.append(data.get('mass_bhs', None))

        redshift = get_snapshot_redshift(snap)
        if redshift is None:
            break
        redshifts.append(redshift)

        snap = data.get('prog_snap', -1)
        subhalo = data.get('prog_sfid', -1)

    # Reverse to chronological order (high z → low z)
    bh_mass = bh_mass[::-1]
    redshifts = redshifts[::-1]

    # --- Save CSV ---
    df = pd.DataFrame({'redshift': redshifts, 'bh_mass': bh_mass})
    csv_name = os.path.join(output_dir, f'{gal["id"]}_z{gal["final_snap"]}_bh_mass.csv')
    df.to_csv(csv_name, index=False)
    print(f'Saved CSV: {csv_name}')

    # --- Generate plot ---
    plt.figure(figsize=(8,6))
    plt.plot(redshifts, bh_mass, marker='o', color='black')
    plt.xlabel('Redshift (z)')
    plt.ylabel('Central Black Hole Mass [$10^{10} M_\\odot / h$]')
    plt.title(f'Galaxy {gal["id"]} - BH Mass Evolution')
    plt.gca().invert_xaxis()
    plt.grid(True)
    plt.tight_layout()

    png_name = os.path.join(output_dir, f'{gal["id"]}_z{gal["final_snap"]}_bh_mass.png')
    plt.savefig(png_name)
    plt.close()
    print(f'Saved plot: {png_name}')

