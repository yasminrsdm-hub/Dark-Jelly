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

# Subhalo e snapshot inicial
snap = 99
subhalo = 227576

bh_mass = []
redshifts = []

while snap != -1 and subhalo != -1:
    print(f'Pegando snap {snap}, subhalo {subhalo}')
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

# Inverte as listas (do passado para o presente)
bh_mass = bh_mass[::-1]
redshifts = redshifts[::-1]

# Salvar CSV
df = pd.DataFrame({
    'redshift': redshifts,
    'bh_mass': bh_mass
})

csv_filename = 'bh_mass_evolution.csv'
df.to_csv(csv_filename, index=False)
print(f'Dados salvos em {csv_filename}')

# Plot
plt.figure(figsize=(8,6))
plt.plot(redshifts, bh_mass, marker='o', color='black')
plt.xlabel('Redshift (z)')
plt.ylabel('Massa do Buraco Negro Central [$10^{10} M_\\odot / h$]')
plt.title('Evolução da Massa do Buraco Negro Central da Galáxia')
plt.gca().invert_xaxis()
plt.grid(True)
plt.tight_layout()
plt.savefig('bh_mass_evolution.png')
plt.show()

print('Gráfico salvo como bh_mass_evolution.png')

