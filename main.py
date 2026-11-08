import pandas as pd
from statsmodels.stats.proportion import proportions_ztest
import matplotlib.pyplot as plt

users = pd.read_excel(
    "data.xlsx",
    sheet_name="Пользователи"
)

payments = pd.read_excel(
    "data.xlsx",
    sheet_name="Платежи"
)

print("Пользователи:")
print(users.head())

print("\n:")
print(payments.head())

print("\nРазмер таблицы пользователей:")
print(users.shape)

print("\nРазмер таблицы платежей:")
print(payments.shape)

print('-' * 50)

print("\nПропуски в таблице пользователей:")
print(users.isnull().sum())

print("\nПропуски в таблице платежей:")
print(payments.isnull().sum())

print("\nДубликаты пользователей:")
print(users["user_id"].duplicated().sum())

print("\nДубликаты платежей:")
print(payments["payment_id"].duplicated().sum())

print("\nРаспределение пользователей:")
print(users["group"].value_counts(dropna=False))

print("\nМинимальный возраст:", users["age"].min())
print("Максимальный возраст:", users["age"].max())


#Очищаем даннфе
payments_clean = payments.dropna(subset=["user_id"]).copy()
payments_clean["user_id"] = payments_clean["user_id"].astype(int)
payments_clean = payments_clean.drop(columns=["group"])
payments_clean = payments_clean.merge(
    users[["user_id", "group"]],
    on="user_id",
    how="left"
)
payments_clean = payments_clean.dropna(subset=["group"])
print("\nРазмер очищенной таблицы:", payments_clean.shape)
print(payments_clean["group"].value_counts())


#Строим воронку
steps = [
    "step1_opened",
    "step2_entered",
    "step3_confirmed",
    "step4_success"
]
user_funnel = (
    payments_clean
    .groupby(["user_id", "group"])[steps]
    .agg(lambda x: x.notna().any())
    .reset_index()
)
funnel = user_funnel.groupby("group")[steps].sum()
print("\nВоронка оплаты:")
print(funnel)
conversion = (
    funnel["step4_success"] /
    funnel["step1_opened"] * 100
)
print("\nКонверсия:")
print(conversion)


#Проверка гипотезы
#успешная оплата
success_a = 494
success_b = 603

#открывшие форму
total_a = 751
total_b = 750

successes = [success_a, success_b]
totals = [total_a, total_b]

z_stat, p_value = proportions_ztest(
    successes,
    totals,
    alternative="two-sided"
)

print("\nСтаттест")
print("Z-статистика:", z_stat)
print("P-value:", p_value)

alpha = 0.05

if p_value < alpha:
    print("Отвергаем H0: разница статистически значима")
else:
    print("Нет оснований отвергнуть H0")


#Визуализация
#воронка
funnel.T.plot(kind="bar", figsize=(9, 5))

plt.title("Воронка оплаты ЖКХ")
plt.xlabel("Этап")
plt.ylabel("Количество пользователей")
plt.xticks(rotation=15)
plt.legend(title="Группа")
plt.tight_layout()
plt.savefig("funnel.png", dpi=200)
plt.show()

#конверсия
conversion.plot(
    kind="bar",
    figsize=(7, 5),
    ylim=(0, 100)
)

plt.title("Сравнение конверсии")
plt.xlabel("Группа")
plt.ylabel("Конверсия, %")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("conversion.png", dpi=200)
plt.show()