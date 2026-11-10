import pandas as pd

orders = pd.read_csv("dados/brutos/olist_orders_dataset.csv")
reviews = pd.read_csv("dados/brutos/olist_order_reviews_dataset.csv")

# 1. Limpeza
entregues = orders[orders["order_status"] == "delivered"].copy()
entregues = entregues.dropna(subset=["order_delivered_customer_date"])

entregues["order_delivered_customer_date"] = pd.to_datetime(
    entregues["order_delivered_customer_date"])
entregues["order_estimated_delivery_date"] = pd.to_datetime(
    entregues["order_estimated_delivery_date"])

entregues["dias_atraso"] = (
    entregues["order_delivered_customer_date"]
    - entregues["order_estimated_delivery_date"]
).dt.days
entregues["atrasado"] = entregues["dias_atraso"] > 0

# 2. Um pedido pode ter mais de uma avaliação: ficar com a média por pedido
notas = reviews.groupby("order_id")["review_score"].mean().reset_index()

# 3. Juntar pedidos e notas
df = entregues.merge(notas, on="order_id", how="left")
print("Pedidos sem nota:", df["review_score"].isna().sum())
df = df.dropna(subset=["review_score"])

# 4. A pergunta do projeto: atrasados têm nota pior?
print()
print(df.groupby("atrasado")["review_score"].agg(["mean", "count"]))

import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs("relatorios", exist_ok=True)
sns.set_theme(style="whitegrid")

# Gráfico 1: nota média, no prazo vs. atrasado
plt.figure(figsize=(6, 5))
media = df.groupby("atrasado")["review_score"].mean()
plt.bar(["No prazo", "Atrasado"], media.values, color=["#4C9F70", "#D9534F"])
plt.title("Nota média: pedidos no prazo vs. atrasados")
plt.ylabel("Nota média (1 a 5)")
plt.ylim(0, 5)
plt.tight_layout()
plt.savefig("relatorios/grafico1_nota_prazo.png")
plt.close()

# Gráfico 2: nota média por faixa de atraso
faixas = pd.cut(
    df["dias_atraso"],
    bins=[-1000, 0, 3, 7, 15, 1000],
    labels=["No prazo", "1 a 3 dias", "4 a 7 dias", "8 a 15 dias", "Mais de 15 dias"],
)
media_faixa = df.groupby(faixas, observed=True)["review_score"].mean()

plt.figure(figsize=(8, 5))
plt.bar(media_faixa.index.astype(str), media_faixa.values, color="#5B8DB8")
plt.title("Nota média por faixa de atraso")
plt.ylabel("Nota média (1 a 5)")
plt.ylim(0, 5)
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("relatorios/grafico2_faixa_atraso.png")
plt.close()

print()
print(media_faixa)
print("Gráficos salvos em relatorios/")