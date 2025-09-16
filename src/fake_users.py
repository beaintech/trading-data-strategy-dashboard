from faker import Faker
import pandas as pd
import random

# 初始化 Faker，可以指定语言环境，比如德语/英语/中文
fake = Faker("de_DE")   # 德语环境（德国名字、国籍更真实）
Faker.seed(0)           # 固定随机种子，结果可复现

def generate_fake_users(n=10):
    users = []
    for _ in range(n):
        name = fake.name()
        alter = random.randint(18, 70)   # 年龄 18-70
        geschlecht = random.choice(["Männlich", "Weiblich"])
        nationalität = fake.current_country()   # 当前国家
        email = fake.email()
        
        users.append({
            "Name": name,
            "Alter": alter,
            "Geschlecht": geschlecht,
            "Nationalität": nationalität,
            "E-Mail": email
        })
    
    return pd.DataFrame(users)

# 生成 10 个用户
df_users = generate_fake_users(10)

print(df_users)
# 保存为 CSV，方便导入 Power BI
df_users.to_csv("fake_users.csv", index=False, encoding="utf-8-sig")
