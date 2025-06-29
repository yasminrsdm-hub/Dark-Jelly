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

mass_stars = []
sfrs = []
metallicity = []
half_mass_rad = []
redshifts = []

# --- Loop through progenitors to track properties ---

while snap != -1 and subhalo != -1:
    print(f'Fetching snap {snap}, subhalo {subhalo}')
    data = get_subhalo_data(snap, subhalo)
    if data is None:
        break
    
    mass_stars.append(data.get('mass_stars', None))
    sfrs.append(data.get('sfr', None))
    metallicity.append(data.get('starmetallicity', None))
    half_mass_rad.append(data.get('halfmassrad_stars', None))
    
    redshift = get_snapshot_redshift(snap)
    if redshift is None:
        break
    redshifts.append(redshift)
    
    snap = data.get('prog_snap', -1)
    subhalo = data.get('prog_sfid', -1)

# Reverse the lists (from past to present)
mass_stars = mass_stars[::-1]
sfrs = sfrs[::-1]
metallicity = metallicity[::-1]
half_mass_rad = half_mass_rad[::-1]
redshifts = redshifts[::-1]

# --- Save to CSV ---
df = pd.DataFrame({
    'redshift': redshifts,
    'mass_stars': mass_stars,
    'sfr': sfrs,
    'metallicity': metallicity,
    'half_mass_radius': half_mass_rad
})

csv_filename = 'stellar_evolution.csv'
df.to_csv(csv_filename, index=False)
print(f'Data saved to {csv_filename}')

# --- Plotting ---
fig, axs = plt.subplots(4, 1, figsize=(10, 14), sharex=True)

axs[0].plot(redshifts, mass_stars, marker='o', color='blue')
axs[0].set_ylabel('Stellar Mass\n[$10^{10} M_\\odot / h$]')

axs[1].plot(redshifts, sfrs, marker='o', color='green')
axs[1].set_ylabel('Star Formation Rate\n[$M_\\odot / yr$]')

axs[2].plot(redshifts, metallicity, marker='o', color='orange')
axs[2].set_ylabel('Stellar Metallicity')

axs[3].plot(redshifts, half_mass_rad, marker='o', color='red')
axs[3].set_ylabel('Stellar Half-Mass Radius\n[ckpc/h]')
axs[3].set_xlabel('Redshift (z)')
axs[3].invert_xaxis()

plt.suptitle('Evolution of Galaxy Properties Over Time')
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()
