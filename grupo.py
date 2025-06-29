import requests
import pandas as pd
from json.decoder import JSONDecodeError

BASE_URL = "https://www.tng-project.org/api/TNG100-1"
HEADERS = {"api-key": ""}

def get_group_number(snapshot, subhalo_id):
    url = f"{BASE_URL}/snapshots/{snapshot}/subhalos/{subhalo_id}/"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Erro ao buscar subhalo {subhalo_id} no snapshot {snapshot} (status {response.status_code})")
        print(f"Resposta bruta: {response.text[:500]}")
        return None

    # Se a resposta começar com <!DOCTYPE html>, provavelmente é uma página de erro
    if response.text.strip().startswith("<!DOCTYPE html>"):
        print(f"Resposta inesperada em HTML para subhalo {subhalo_id} no snapshot {snapshot}:")
        print(response.text[:500])
        return None

    try:
        data = response.json()
        return data.get("GroupNumber")
    except JSONDecodeError as e:
        print(f"Erro ao decodificar JSON para subhalo {subhalo_id} no snapshot {snapshot}: {e}")
        print(f"Resposta bruta: {response.text[:500]}")
        return None


def main(input_csv, output_csv):
    df = pd.read_csv(input_csv, dtype={"snapshot": int, "subhalo_id": int})
    halos = []

    for idx, row in df.iterrows():
        snapshot = row["snapshot"]
        subhalo_id = row["subhalo_id"]
        if pd.isna(subhalo_id):
            halos.append(None)
            continue
        
        group_number = get_group_number(snapshot, subhalo_id)
        halos.append(group_number)

    df["GroupNumber"] = halos

    df.to_csv(output_csv, index=False)
    print(f"Arquivo com halos salvo: {output_csv}")

if __name__ == "__main__":
    input_csv = "jellyfish_gemeas_massas_TNG100.csv"  # Seu CSV original com snapshot e subhalo_id
    output_csv = "jellyfish_com_halo.csv"             # CSV novo com a coluna GroupNumber
    main(input_csv, output_csv)

