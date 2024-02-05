import pandas as pd
import numpy as np

def extract_name(value):
    if pd.isnull(value) or '_' not in value:
        return value
    return value.split('_', 1)[1]

def serving_size_to_number(value):
    if pd.isnull(value) or value == '-' or value=='1식':
        return np.nan, np.nan
    elif value == '30-80g':
        return 55, 'g'
    elif 'g' in value:
        return value.replace('g', ''), 'g'
    elif 'ml' in value:
        return value.replace('ml', ''), 'ml'
    else:
        return value, np.nan

def serving_size_na(dff):
    df2=pd.read_csv('raw_DB/가공식품/통합 식품영양성분DB.csv')
    food_df2=df2.loc[:,['식품명','식품대분류','1회제공량','내용량_단위']]
    food_df2['식품명'] = food_df2['식품명'].replace(' ', '', regex=True)
    dff['식품명'] = dff['식품명'].replace(' ', '', regex=True)

    for index, row in dff[dff['영양성분함량기준량'].isna()].iterrows():
        matching_row = food_df2[food_df2['식품명'] == row['식품명']]
        if not matching_row.empty:
            dff.loc[index, '영양성분함량기준량'] = matching_row['1회제공량'].values[0]

def nutrients_100_to_serving(row, nutrients_column, standard_column):
    if not pd.isnull(row[nutrients_column]) and not pd.isnull(row[standard_column]):
        return (float(row[nutrients_column]) * float(row['영양성분함량기준량'])) / 100
    return np.nan

def ingr(d):
    df3=pd.read_csv('raw_DB/가공식품/품목제조보고.csv')
    df3=df3[['식품코드','원재료코드명']]
    merged_df = d.merge(df3, on='식품코드', how='left')
    return merged_df
    
def processed_food():
    df=pd.read_csv('raw_DB/가공식품/전국통합식품영양성분정보(가공식품)표준데이터.csv', low_memory=False)   
    food_df=df.loc[:, ['카테고리','식품코드', '식품명','식품대분류명', '대표식품명', '식품중분류명','식품소분류명','식품세분류명',
                    '영양성분함량기준량', '에너지(kcal)','탄수화물(g)', '단백질(g)','지방(g)','나트륨(mg)','칼륨(mg)','인(mg)', '당류(g)',
                    '1회 섭취참고량', '제조사명', '식품중량']]
    nutrients_columns = ['에너지(kcal)', '탄수화물(g)', '단백질(g)', '지방(g)', '나트륨(mg)', '칼륨(mg)', '인(mg)', '당류(g)']

    food_df['식품명'] = food_df['식품명'].apply(extract_name)
    food_df[['영양성분함량기준량', '1회 섭취참고량 단위']] = food_df['1회 섭취참고량'].apply(serving_size_to_number).apply(pd.Series)
    serving_size_na(food_df)
    for column in nutrients_columns:
        food_df[column] = food_df.apply(nutrients_100_to_serving, args=(column, '영양성분함량기준량'), axis=1)
    
    food_df=ingr(food_df)

    return food_df

def general_food():
    df=pd.read_csv('raw_DB/음식/전국통합식품영양성분정보(음식)표준데이터.csv', low_memory=False)   
    df = df[df['식품기원명'] == '만성콩팥병레시피'] # (df['식품기원명'] == '가정식(분석 함량)') | (df['식품기원명'] == '초등학교급식(재료량 기반 산출 함량)') | (df['식품기원명'] == '중고등학교급식(재료량 기반 산출함량)') | (df['식품기원명'] == '산업체급식(재료량 기반 산출 함량))'
    food_df=df.loc[:, ['카테고리','식품코드', '식품명','식품대분류명', '대표식품명', '식품중분류명','식품소분류명','식품세분류명',
                    '영양성분함량기준량', '에너지(kcal)','탄수화물(g)', '단백질(g)','지방(g)','나트륨(mg)','칼륨(mg)','인(mg)', '당류(g)',
                    '업체명', '식품중량']]
    nutrients_columns = ['에너지(kcal)', '탄수화물(g)', '단백질(g)', '지방(g)', '나트륨(mg)', '칼륨(mg)', '인(mg)', '당류(g)']
    food_df[['영양성분함량기준량', '1회 섭취참고량 단위']] = food_df['식품중량'].apply(serving_size_to_number).apply(pd.Series)
    for column in nutrients_columns:
       food_df[column] = food_df.apply(nutrients_100_to_serving, args=(column, '영양성분함량기준량'), axis=1)
    return food_df