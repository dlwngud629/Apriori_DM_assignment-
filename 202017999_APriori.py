#import pandas as pd
import hashlib
from itertools import combinations

count_all = 0
support = 0.015
confidence = 0.3
word_hash_count = {}
data_set = pd.read_csv('store_data(2).csv')

for row_index, row in data_set.iterrows(): 
    for col_index, cell_value in enumerate(row):
        if isinstance(cell_value, str):
            hasher = hashlib.sha256()
            hasher.update(cell_value.encode())
            word_hash = hasher.hexdigest()
            if word_hash in word_hash_count:
                word_hash_count[word_hash]['count'] += 1
            else:
                word_hash_count[word_hash] = {'word': cell_value, 'count': 1}

filtered_hash = {} # 서포트 이상 원소 추출
for word_hash in word_hash_count:
    if word_hash_count[word_hash]['count'] / data_set.shape[0] >= support: 
        filtered_hash[word_hash] = word_hash_count[word_hash]

#원소로 집합의 크기가 2인 subset구성
hashed_subsets_size_two = {} 
for subset in combinations(filtered_hash.keys(), 2):
    subset_str = ','.join(subset)
    hasher = hashlib.sha256()
    hasher.update(subset_str.encode())
    subset_hash = hasher.hexdigest()
    hashed_subsets_size_two[subset_hash] = subset


#서브셋이 모두 나타난 행의 개수 카운트
subset_counts = {subset_hash: 0 for subset_hash in hashed_subsets_size_two.keys()}
for row_index, row in data_set.iterrows():
    hashed_row = set(hashlib.sha256(str(value).encode()).hexdigest() for value in row if isinstance(value, str))
    for subset_hash, subset in hashed_subsets_size_two.items():
        if set(subset).issubset(hashed_row):
            subset_counts[subset_hash] += 1  

#서브셋이 서포트 이상 출현하는지
filtered_subset_hash = {}
for subset_hash, count in subset_counts.items():
    if count / data_set.shape[0] >= support:  
        filtered_subset_hash[subset_hash] = hashed_subsets_size_two[subset_hash]

# 결과 출력
print('서포트 이상의 부분집합 나열 완료\n')
for subset_hash, subset in filtered_subset_hash.items():
    words = [word_hash_count[word_hash]['word'] for word_hash in subset]
    #print(f'{", ".join(words)}')

# 여기에 triple_subset_hash 생성 코드 추가
triple_subset_hash = {}
for subset1 in filtered_subset_hash.values():
    for subset2 in filtered_subset_hash.values():
        intersection = set(subset1).intersection(set(subset2))
        if len(intersection) == 1:  # 겹치는 원소가 하나일 때
            combined = set(subset1).union(set(subset2))
            if len(combined) == 3:  # 합친 집합의 원소가 총 3개일 때
                combined_str = ','.join(sorted(combined))  # 집합을 문자열로 변환
                hasher = hashlib.sha256()
                hasher.update(combined_str.encode())
                combined_hash = hasher.hexdigest()
                triple_subset_hash[combined_hash] = combined

#triple_subset_hash 출력 코드 추가
for hash_value, subset in triple_subset_hash.items():
    words = [word_hash_count[word_hash]['word'] for word_hash in subset]
    #print(f'{", ".join(words)}')
#print('크기가 3인 부분집합 출력 완료')

triple_subset_counts = {subset_hash: 0 for subset_hash in triple_subset_hash.keys()}

#triple_subset_hash의 튜플이 몇번 포함되어있는지
for row_index, row in data_set.iterrows():
    hashed_row = set(hashlib.sha256(str(value).encode()).hexdigest() for value in row if isinstance(value, str))
    # triple_subset_hash에 대한 카운트 추가
    for subset_hash, subset in triple_subset_hash.items():
        if set(subset).issubset(hashed_row):
            triple_subset_counts[subset_hash] += 1  # 해당 subset이 행에 모두 포함되면 카운트 증가

# support를 넘는 triple_subset_hash 원소만 저장
filtered_triple_subset_hash = {subset_hash: triple_subset_hash[subset_hash] 
                                for subset_hash, count in triple_subset_counts.items() 
                                    if count / data_set.shape[0] >= support}

#서포트 이상의 크기가 3인 부분집합 출력완료
for subset_hash, subset in filtered_triple_subset_hash.items():
    words = [word_hash_count[word_hash]['word'] for word_hash in subset]
    #print(f'{", ".join(words)}')

confidence_subset = {}

for triple_hash, triple_subset in filtered_triple_subset_hash.items():
    for j in triple_subset:
        subset = set(triple_subset) - {j}
        subset_str = ','.join(sorted(subset))
        hasher = hashlib.sha256()
        hasher.update(subset_str.encode())
        subset_hash = hasher.hexdigest()

        if subset_hash in subset_counts and subset_counts[subset_hash] != 0:
            confidence_value = triple_subset_counts[triple_hash] / subset_counts[subset_hash]
            
            if confidence_value >= confidence:
                all_items = list(subset) + [j]  
                combined_str = ','.join(all_items)
                hasher = hashlib.sha256()
                hasher.update(combined_str.encode())
                combined_hash = hasher.hexdigest()
                
                if combined_hash not in confidence_subset:  
                    confidence_subset[combined_hash] = {
                        'subset': subset,
                        'j': j,
                        'confidence': confidence_value
                    }
                    

print('신뢰도 이상의 부분집합 출력')
for hash_value, data in confidence_subset.items():
    subset_words = [word_hash_count[word_hash]['word'] for word_hash in data['subset']]
    j_word = word_hash_count[data['j']]['word']

    pr_j = word_hash_count[data['j']]['count'] / data_set.shape[0]
    interest = abs(data['confidence'] - pr_j)

    print(f"{'{' + ', '.join(subset_words) + '}'} -> {j_word} with confidence {data['confidence']:.2f} and interest {interest:.2f}")

# # filtered_hash 저장
# filtered_hash_df = pd.DataFrame.from_dict(filtered_hash, orient='index', columns=['count'])
# filtered_hash_df['word'] = [word_hash_count[word_hash]['word'] for word_hash in filtered_hash]
# filtered_hash_df.to_excel('filtered_hash.xlsx', index=False)

# # hashed_subsets_size_two 저장
# hashed_subsets_size_two_df = pd.DataFrame([{
#     'subset': ', '.join([word_hash_count[word_hash]['word'] for word_hash in subset])
# } for subset in hashed_subsets_size_two.values()])
# hashed_subsets_size_two_df.to_excel('hashed_subsets_size_two.xlsx', index=False)

# # filtered_subset_hash 저장
# filtered_subset_hash_df = pd.DataFrame([{
#     'subset': ', '.join([word_hash_count[word_hash]['word'] for word_hash in subset])
# } for subset in filtered_subset_hash.values()])
# filtered_subset_hash_df.to_excel('filtered_subset_hash.xlsx', index=False)

# # triple_subset_hash 저장
# triple_subset_hash_df = pd.DataFrame([{
#     'subset': ', '.join([word_hash_count[word_hash]['word'] for word_hash in subset]),
#     'count': triple_subset_counts[subset_hash] 
# } for subset_hash, subset in triple_subset_hash.items()])
# triple_subset_hash_df.to_excel('triple_subset_hash_with_count.xlsx', index=False)

# # filtered_triple_subset_hash 저장
# filtered_triple_subset_hash_df = pd.DataFrame([{
#     'subset': ', '.join([word_hash_count[word_hash]['word'] for word_hash in subset])
# } for subset in filtered_triple_subset_hash.values()])
# filtered_triple_subset_hash_df.to_excel('filtered_triple_subset_hash.xlsx', index=False)
