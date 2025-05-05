import pandas as pd
import matplotlib.pyplot as plt
import os

csv_path = 'datasets/aoi-hits-750.csv'
df = pd.read_csv(csv_path)

aoi_counts = df['aoi_hit'].value_counts().sort_index()

# Plotting the AOI distribution
plt.figure(figsize=(10, 6))
aoi_counts.plot(kind='bar', color='skyblue', edgecolor='black')
plt.title('Cantidad de AOI Hits por Tipo')
plt.xlabel('AOI')
plt.ylabel('Frecuencia')
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig('figures/aoi_hits_distribution.png')
plt.show()