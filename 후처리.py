from pathlib import Path

import numpy as np
import pandas as pd

id_cols = ['대학명', '학과명', '전형명']
df = pd.read_json(Path('내신닷컴/results/입결상세.jsonl'), orient='records', lines=True)
df_2025 = pd.read_json(Path('내신닷컴/results/입결상세_2025.jsonl'), orient='records', lines=True)

df = pd.merge(df, df_2025[[*id_cols, '전년도모집인원']], how='left', on=id_cols)

df = df[[
    '대학명',
    '학과명',
    '전형명',
    '모집인원',
    '수능최저',
    '전년도모집인원',
    '경쟁률',
    '추가합격'
]]
df['추가합격'] = np.where(df['추가합격'] == '-', np.nan, df['추가합격'])
for col in df.columns:
    if col not in ['모집인원', '전년도모집인원', '추가합격']:
        continue
    df[col] = df[col].str.extract(r'(\d+)').astype('Int64')

df['경쟁률'] = np.where(df['경쟁률'] == '', np.nan, df['경쟁률'])
df['총지원'] = (df['전년도모집인원'] * df['경쟁률'].astype(float)).astype('Int64')

df['총합격'] = df['전년도모집인원'] + df['추가합격']
df['실경쟁률'] = (df['총지원'] / df['총합격']).round(2)
df = df.astype('string')
df = df.fillna('')

df.to_json(Path('내신닷컴/results/통합.jsonl'), orient='records', lines=True, force_ascii=False)
