import sys
import pandas as pd

print("arguments", sys.argv)

day = int(sys.argv[1])
print(f'Running pipeline for day {day}')

df = pd.DataFrame({
    'A': [1, 2],
    'B': [3, 4]
})

df.to_parquet(f'output_day_{sys.argv[1]}.parquet')

print(f'Job finished successfully for day = {day}')
