import pandas as pd

# 데이터 불러오기
data_set = pd.read_csv('store_data(2).csv')

# 전제 상품과 결과 상품 입력 받기
antecedent_products = input("Enter two antecedent products separated by a comma: ").split(', ')
consequent_product = input("Enter the consequent product: ").strip()

# 상품 이름 앞뒤 공백 제거
antecedent_products = [product.strip() for product in antecedent_products]

# 일치하는 행의 수 초기화
antecedent_count = 0
consequent_count = 0

# 각 행을 순회하며 상품의 존재를 확인
for _, row in data_set.iterrows():
    row_set = set(row.dropna().values)
    
    if all(product in row_set for product in antecedent_products):
        antecedent_count += 1
        
        if consequent_product in row_set:
            consequent_count += 1

# 신뢰도 계산
confidence = consequent_count / antecedent_count if antecedent_count > 0 else 0

# 결과 출력
print(f"Antecedent products: {', '.join(antecedent_products)}")
print(f"Consequent product: {consequent_product}")
print(f"Confidence: {confidence:.2f}")
