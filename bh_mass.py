import requests
import matplotlib.pyplot as plt
import pandas as pd

# --- Configuration ---

base_url = 'http://www.tng-project.org/api/TNG100-1'
token = ''  # your valid API token

headers = {
    'Accept': 'application/json',
    'api-key': token
}

# --- Functions to access data ---

def get_subhalo_data(snap, subhalo_id):
    """Fetches data for a specific subhalo at a given snapshot."""
    url = f'{base_url}/snapshots/{snap}/subhalos/{subhalo_id}/'
    r = requests.get(url, headers=headers, verify=False)
    if r.status_code == 200:
        return r.json()
    else:
        print(f'Error fetching snapshot {snap}, subhalo {subhalo_id}:', r.status_code)
        return None

def get_snapshot_redshift(snap):
    """Fetches the redshift of a given snapshot."""
    url = f'{base_url}/snapshots/{snap}/'
    r = requests.get(url, headers=headers, verify=False)
    if r.status_code == 200:
        return r.json()['redshift']
    else:
        print(f'Error fetching snapshot {snap}:', r.status_code)
        return None

# --- Initial subhalo and snapshot ---

snap = 99
subhalo = 227576

bh_mass = []
redshifts = []

# --- Loop through progenitors to track black hole mass evolution ---

while snap != -1 and subhalo != -1:
    print(f'Fetching snap {snap}, subhalo {subhalo}')
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

# Reverse the lists (from past to present)
bh_mass = bh_mass[::-1]
redshifts = redshifts[::-1]

# --- Save to CSV ---
df = pd.DataFrame({
    'redshift': redshifts,
    'bh_mass': bh_mass
})

csv_filename = 'bh_mass_evolution.csv'
df.to_csv(csv_filename, index=False)
print(f'Data saved to {csv_filename}')

# --- Plotting ---
plt.figure(figsize=(8,6))
plt.plot(redshifts, bh_mass, marker='o', color='black')
plt.xlabel('Redshift (z)')
plt.ylabel('Central Black Hole Mass [$10^{10} M_\\odot / h$]')
plt.title('Evolution of Central Black Hole Mass of the Galaxy')
plt.gca().invert_xaxis()
plt.grid(True)
plt.tight_layout()
plt.savefig('bh_mass_evolution.png')
plt.show()

print('Plot saved as bh_mass_evolution.png')


