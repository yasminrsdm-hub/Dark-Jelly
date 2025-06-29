import requests
import pandas as pd
import matplotlib.pyplot as plt
import time

BASE_URL = "http://www.tng-project.org/api/TNG50-1"
HEADERS = {"api-key": ""}

def get_group_m200(snapshot, grnr, max_retries=3):
    snapshot = int(snapshot)
    grnr = int(grnr)

    url = f"{BASE_URL}/snapshots/{snapshot}/halos/{grnr}/info.json"

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200:
                print(f"Erro HTTP {response.status_code} para grupo {grnr} no snapshot {snapshot}")
                return None

            data = response.json()
            m200_crit = data.get("Group_M_Crit200")
            if m200_crit is None:
                print(f"Group_M_Crit200 não encontrado para grupo {grnr} no snapshot {snapshot}")
                return None

            return m200_crit  # Mantemos em 10¹⁰ M☉/h

        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição para grupo {grnr} no snapshot {snapshot}: {e}")
        except ValueError as e:
            print(f"Erro ao decodificar JSON para grupo {grnr} no snapshot {snapshot}: {e}")
            print(f"Resposta bruta: {response.text[:300]}")

        print(f"Tentando novamente... ({attempt + 1}/{max_retries})")
        time.sleep(2)

    return None

def main(input_csv, output_csv):
    df = pd.read_csv(input_csv, dtype={"snapshot": int, "subhalo_id": int, "group_number": int})
    masses = []

    print(f"Processando {len(df)} linhas...")

    for idx, row in df.iterrows():
        snapshot = row["snapshot"]
        grnr = row["group_number"]
        m200 = get_group_m200(snapshot, grnr)
        masses.append(m200)
        print(f"Processados {idx+1}/{len(df)} grupos", end="\r")

    df["M200c_10^10Msun/h"] = masses
    df_clean = df.dropna(subset=["M200c_10^10Msun/h"])

    df_clean.to_csv(output_csv, index=False)
    print(f"\nArquivo CSV salvo: {output_csv}")

    plt.figure(figsize=(10,6))
    plt.hist(df_clean["M200c_10^10Msun/h"], bins=30, alpha=0.7, label="Galáxias")
    plt.xlabel(r"$M_{200c}$ [$10^{10} M_\odot/h$]")
    plt.ylabel("Número de galáxias")
    plt.title("Histograma de $M_{200c}$ das galáxias TNG100")
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    input_csv = "gemeas_com_grupos50.csv"
    output_csv = "gemeas_tng50_m200.csv"
    main(input_csv, output_csv)


