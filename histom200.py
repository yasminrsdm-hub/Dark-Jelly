import pandas as pd
import matplotlib.pyplot as plt

# Lê o CSV com as massas M200c
df = pd.read_csv("gemeas_tng50_m200.csv")

# Remove valores inválidos
df_clean = df.dropna(subset=["M200c_10^10Msun/h"])
masses = df_clean["M200c_10^10Msun/h"]

# Define massas de referência dos aglomerados (em unidades 10¹⁰ M☉/h)
aglomerados = {
    "Subestrutura F0083": (3160, 670),                   # erro aproximado
}

# Classificação: qual galáxia cai em qual aglomerado
def classificar_m200(m):
    for nome, (centro, erro) in aglomerados.items():
        if centro - erro <= m <= centro + erro:
            return nome
    return "Fora dos intervalos"

df_clean["Aglomerado_Associado"] = df_clean["M200c_10^10Msun/h"].apply(classificar_m200)

# Salva o novo CSV com classificação
df_clean.to_csv("gemeas_tng50_m200.csv", index=False)

# Plot do histograma com faixas marcadas
plt.figure(figsize=(10, 6))
plt.hist(masses, bins=30, color="skyblue", edgecolor="black", alpha=0.7, label="Galáxias")

# Marcação dos aglomerados
for nome, (m_central, m_erro) in aglomerados.items():
    plt.axvline(m_central, linestyle="--", linewidth=2, label=f"{nome}: {m_central:.0f}", color="red")
    plt.fill_betweenx(
        y=[0, plt.ylim()[1]],
        x1=m_central - m_erro,
        x2=m_central + m_erro,
        alpha=0.2,
        label=f"{nome} ± erro"
    )

plt.xlabel(r"$M_{200c}$ [$10^{10} M_\odot/h$]")
plt.ylabel("Número de galáxias")
plt.title("Histograma de $M_{200c}$ com marcações de aglomerados TNG50")
plt.legend()
plt.tight_layout()
plt.savefig("histograma_m200_aglomerados.png")
plt.show()

