import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# 열의 수 제한
max_columns = 20
file_path = 'store_data(2).csv'

# 열의 수 제한을 사용하여 데이터 불러오기
df = pd.read_csv(file_path, header=None, usecols=range(max_columns))

# 데이터를 One-hot 인코딩으로 변환
df_encoded = pd.get_dummies(df.stack(dropna=True)).groupby(level=0).sum()

# 값이 1보다 큰 경우 1로 변경
df_encoded = df_encoded.applymap(lambda x: 1 if x > 1 else x)

# apriori 알고리즘을 사용하여 빈발 아이템셋을 찾기
frequent_itemsets = apriori(df_encoded, min_support=0.015, use_colnames=True)

# 빈발 아이템셋을 바탕으로 연관 규칙 찾기
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.4)

# antecedents 크기가 2인 규칙만 필터링
rules = rules[rules['antecedents'].apply(lambda x: len(x) == 2)]

# interest 계산 추가
rules['interest'] = rules['confidence'] - rules['consequent support']

# 필요한 열만 선택
rules = rules[['antecedents', 'consequents', 'support', 'confidence', 'interest']]

# 연관 규칙 출력
print(rules)
