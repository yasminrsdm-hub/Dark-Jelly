import pandas as pd

# Lê os dados
df = pd.read_csv("gemeas_tng100_m200.csv")
df_clean = df.dropna(subset=["M200c_10^10Msun/h"])
masses = df_clean["M200c_10^10Msun/h"]

# Define os aglomerados e suas faixas: (nome, (massa central, erro))
aglomerados = {
    "Fornax": (700, 50),
    "Abell 901/2": (2000, 100),
    "Virgo": (4900, 700),
    "Coma": (5000, 1000),
    "Subestrutura F0083": (3160, 670),
}

# Função para determinar quais aglomerados cada galáxia pertence
def identificar_aglomerados(m):
    tags = []
    for nome, (centro, erro) in aglomerados.items():
        if centro - erro <= m <= centro + erro:
            tags.append(nome)
    return ", ".join(tags) if tags else "Nenhum"

# Aplica a função ao DataFrame
df_clean["Aglomerados_Contidos"] = df_clean["M200c_10^10Msun/h"].apply(identificar_aglomerados)

# Salva CSV
df_clean.to_csv("gemeas_tng100_m200_com_aglomerados.csv", index=False)
print("✅ Arquivo salvo: gemeas_tng100_m200_com_aglomerados.csv")

