import requests
import matplotlib.pyplot as plt
import pandas as pd

base_url = 'http://www.tng-project.org/api/TNG100-1'
token = '4ff6dd78476d70518200141e4f2e2268'  # seu token válido

headers = {
    'Accept': 'application/json',
    'api-key': token
}

def get_subhalo_data(snap, subhalo_id):
    url = f'{base_url}/snapshots/{snap}/subhalos/{subhalo_id}/'
    r = requests.get(url, headers=headers, verify=False)
    if r.status_code == 200:
        return r.json()
    else:
        print(f'Erro na requisição snap {snap} id {subhalo_id}:', r.status_code)
        return None

def get_snapshot_redshift(snap):
    url = f'{base_url}/snapshots/{snap}/'
    r = requests.get(url, headers=headers, verify=False)
    if r.status_code == 200:
        return r.json()['redshift']
    else:
        print(f'Erro na requisição snapshot {snap}:', r.status_code)
        return None

snap = 99
subhalo = 227576

mass_stars = []
sfrs = []
metallicity = []
half_mass_rad = []
redshifts = []

while snap != -1 and subhalo != -1:
    print(f'Pegando snap {snap}, subhalo {subhalo}')
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

mass_stars = mass_stars[::-1]
sfrs = sfrs[::-1]
metallicity = metallicity[::-1]
half_mass_rad = half_mass_rad[::-1]
redshifts = redshifts[::-1]

df = pd.DataFrame({
    'redshift': redshifts,
    'mass_stars': mass_stars,
    'sfr': sfrs,
    'metallicity': metallicity,
    'half_mass_radius': half_mass_rad
})

csv_filename = 'stellar_evolution.csv'
df.to_csv(csv_filename, index=False)
print(f'Dados salvos em {csv_filename}')

fig, axs = plt.subplots(4, 1, figsize=(10, 14), sharex=True)

axs[0].plot(redshifts, mass_stars, marker='o', color='blue')
axs[0].set_ylabel('Massa Estelar\n[$10^{10} M_\\odot / h$]')

axs[1].plot(redshifts, sfrs, marker='o', color='green')
axs[1].set_ylabel('Taxa Formação Estelar\n[$M_\\odot / yr$]')

axs[2].plot(redshifts, metallicity, marker='o', color='orange')
axs[2].set_ylabel('Metalicidade Estelar')

axs[3].plot(redshifts, half_mass_rad, marker='o', color='red')
axs[3].set_ylabel('Raio Meia Massa Estelar\n[ckpc/h]')
axs[3].set_xlabel('Redshift (z)')
axs[3].invert_xaxis()

plt.suptitle('Evolução de Propriedades da Galáxia ao Longo do Tempo')
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()

