import pandas as pd
import random
import string
import numpy as np

n = 2500
N = [int(n*0.9), int(n*1.1)]    # Dataset sizes
num_aois = 5              # Number of Areas of Interest
num_users = 100         # Number of users

def generate_user_id(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_skewed_weights(num_aois, alpha=1.5):
    ranks = np.arange(1, num_aois + 1)
    weights = 1 / (ranks ** alpha)
    return weights / weights.sum()

for n in N:
    records = []

    user_ids = [generate_user_id() for _ in range(num_users)]
    aois = [f"subevent_{i}" for i in range(num_aois)]
    aois_weights = generate_skewed_weights(num_aois)

    for _ in range(n):
        user_id = random.choice(user_ids)
        aoi_hit = random.choices(aois, weights=aois_weights, k=1)[0]
        records.append((user_id, aoi_hit))
        

    df = pd.DataFrame(records, columns=["user_id", "aoi_hit"])
    df.to_excel(f'datasets/aoi-hits-{n}.xlsx', index=False)