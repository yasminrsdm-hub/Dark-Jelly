import requests
import matplotlib.pyplot as plt
import pandas as pd

# --- Configuration ---

base_url = 'http://www.tng-project.org/api/TNG50-1'
token = '4ff6dd78476d70518200141e4f2e2268'  # your valid API token

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

snap = 68
subhalo = 53742

mass_dm = []
redshifts = []

# --- Loop through progenitors to track dark matter mass evolution ---

while snap != -1 and subhalo != -1:
    print(f'Fetching snap {snap}, subhalo {subhalo}')
    data = get_subhalo_data(snap, subhalo)
    if data is None:
        break
    
    mass_dm.append(data.get('mass_dm', None))
    
    redshift = get_snapshot_redshift(snap)
    if redshift is None:
        break
    redshifts.append(redshift)
    
    snap = data.get('prog_snap', -1)
    subhalo = data.get('prog_sfid', -1)

# Reverse the lists (from past to present)
mass_dm = mass_dm[::-1]
redshifts = redshifts[::-1]

# --- Save to CSV ---
df = pd.DataFrame({
    'redshift': redshifts,
    'mass_dm': mass_dm
})

csv_filename = 'dm_mass_evolution.csv'
df.to_csv(csv_filename, index=False)
print(f'Data saved to {csv_filename}')

# --- Plotting ---
plt.figure(figsize=(8,6))
plt.plot(redshifts, mass_dm, marker='o', color='brown')
plt.xlabel('Redshift (z)')
plt.ylabel('Dark Matter Mass [$10^{10} M_\\odot / h$]')
plt.title('Evolution of Dark Matter Mass of the Galaxy')
plt.gca().invert_xaxis()
plt.grid(True)
plt.tight_layout()
plt.savefig('dm_mass_evolution.png')
plt.show()


