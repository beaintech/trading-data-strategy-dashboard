from faker import Faker
import pandas as pd
import random

fake = Faker("de_DE")   # 德语环境（德国名字、国籍更真实）
Faker.seed(0)           # 固定随机种子，结果可复现

def generate_fake_users(n=50):
    users = []
    for _ in range(n):
        name = fake.name()
        alter = random.randint(18, 80)   # 年龄 18-70
        geschlecht = random.choice(["Männlich", "Weiblich"])
        nationalität = fake.current_country()   
        email = fake.email()
        
        users.append({
            "Name": name,
            "Alter": alter,
            "Geschlecht": geschlecht,
            "Nationalität": nationalität,
            "E-Mail": email
        })
    
    return pd.DataFrame(users)

df_users = generate_fake_users(50)

print(df_users)
df_users.to_csv("fake_users.csv", index=False, encoding="utf-8-sig")
