import h5py
import pandas as pd

with h5py.File('jellyfish.hdf5', 'r') as f:
    subfind_ids = f['Branches_SubfindID'][:].flatten()
    snap_nums = f['Branches_SnapNum'][:].flatten()
    scores = f['Branches_ScoreAdjusted'][:].flatten()
    jelly_flags = f['Branches_JellyfishFlag'][:].flatten()

df = pd.DataFrame({
    'SubfindID': subfind_ids,
    'SnapNum': snap_nums,
    'ScoreAdjusted': scores,
    'JellyfishFlag': jelly_flags
})

# Filtra apenas snapshots entre 68 e 99 e galáxias jellyfish (flag == 1)
df = df[(df['SnapNum'] >= 67) & (df['SnapNum'] <= 99) & (df['JellyfishFlag'] == 1)]

df.to_csv('jellyfish_local.csv', index=False)
print(f"Arquivo 'jellyfish_local.csv' criado com {len(df)} entradas")

