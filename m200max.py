import requests

def find_max_m200c(sim_name, snapshot, max_attempts=50000):
    headers = {'api-key': ''}
    max_m200c = 0
    max_grnr = None

    for grnr in range(max_attempts):
        halo_url = f"https://www.tng-project.org/api/{sim_name}/snapshots/{snapshot}/halos/{grnr}/info.json"
        response = requests.get(halo_url, headers=headers)

        if response.status_code == 404:
            print(f"Parou no grupo {grnr} (não existe).")
            break
        elif response.status_code != 200:
            print(f"Erro no grupo {grnr}: {response.status_code}")
            continue

        data = response.json()
        m200c = data['Group_M_Crit200']
        if m200c > max_m200c:
            max_m200c = m200c
            max_grnr = grnr

        if grnr % 1000 == 0:
            print(f"Verificado até grupo {grnr}...")

    print(f"Simulação {sim_name} - Snapshot {snapshot}")
    print(f"Maior M200c: {max_m200c:.2f} x10^10 Msol/h (grupo {max_grnr})")
    return max_m200c

snapshot_num = 99
for sim in ['TNG50-1', 'TNG100-1']:
    max_m = find_max_m200c(sim, snapshot_num, max_attempts=50000)
    print(f"Simulação {sim} - Snapshot {snapshot_num} - M200c máximo: {max_m:.2f} x10^10 Msol/h")

