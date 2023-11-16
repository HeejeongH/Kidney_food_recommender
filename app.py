import streamlit as st
import Diagnose as DG
import Nutrientscore as NS
import NutritionCalculator as NC
import pandas as pd

st.title("만성 콩팥병 맞춤 식단 추천")

# User inputs
age = st.number_input('나이를 입력해주세요. (세)',1,100)

gend = st.selectbox('성별을 선택해주세요.', ('여자', '남자'))
gender = 'female' if gend == '여자' else 'male'

heigh = st.number_input('키는 몇 cm인가요?')
height = heigh/100
weight = st.number_input('몸무게는 몇 kg인가요?')

stat = st.selectbox('투석 중인가요?', ('투석 전입니다.', '혈액투석 중입니다.', '복막투석 중입니다.'))
if stat =='투석 전입니다.':
    state = 'CKD' 
    PDk = 0
elif stat == '혈액투석 중입니다.':
    state = 'HD'
    PDk = 0
else:
    state = 'PD' 
    PDk = st.number_input('복막투석 중이라면 투석액 칼로리가 어떻게 되나요?')  # 복막투석 시 투석액 칼로리

st.write('아래 지표들을 입력해주세요.')
eGFR = st.number_input('사구체 여과율') # 사구체 여과율
uACR = st.number_input('소변 알부민 크레아티닌 비율') # 50 
protein_loss = st.number_input('단백뇨') 
albumin = st.number_input('혈중 알부민') #3.4 # 
FBG = st.number_input('공복 혈당') 
OGTT = st.number_input('경구부하혈당')
HbA1c = st.number_input('당화혈색소') #7.1
TG = st.number_input('중성지방') #600
LDL = st.number_input('저밀도 콜레스테롤') #105
SBP = st.number_input('수축기혈압') #130
DBP = st.number_input('이완기혈압') #80
CK = st.number_input('혈중 칼륨 농도') #6
CP = st.number_input('혈중 인 농도') #5
CCa = st.number_input('혈중 칼슘 농도') #4

tab1, tab2, tab3= st.tabs(['내 건강', '영양정보', '맞춤식단'])

with tab1:
    dig = DG.Diagnose(gender, height, weight, state, PDk, eGFR, uACR, protein_loss, albumin, FBG, OGTT, HbA1c, TG, LDL, SBP, DBP, CK, CP, CCa)

    st.subheader("내 건강 정보")

    sw_r, bmi_r, albumin_r, kidney_r, diabetes_r, blood_pressure_r, triglycerides_r, cholesterol_r, K_r, P_r, Ca_r = dig.diagnose()
    st.text('내 건강 요약')
    st.write(f'- BMI: {round(bmi_r,2)}')
    st.write(f'- 알부민 수치: {albumin_r} ({albumin} g/dL)')
    st.write(f"- 콩팥병: {kidney_r}")
    st.write(f'- 당뇨병: {diabetes_r}')
    st.write(f'- 혈압: {blood_pressure_r} ({SBP} mmHg/{DBP} mmHg)')
    st.write(f'- 중성지질: {triglycerides_r} ({TG} mg/dL)')
    st.write(f'- 저밀도 콜레스테롤: {cholesterol_r} ({LDL} mg/dL)')
    st.write(f'- 혈중 칼륨 농도: {K_r} ({CK} mEq/L)')
    st.write(f'- 혈중 인 농도: {P_r} ({CP} mg/dL)')
    st.write(f'- 혈중 칼슘 농도: {Ca_r} ({CCa} mg/dL)')

with tab2:
    st.subheader("영양정보")
    st.text("내가 이 음식을 먹어도되는지 궁금하다면?")
    if 'input' not in st.session_state:
        st.session_state.input = None
    if 'filtered_df' not in st.session_state:
        st.session_state.filtered_df = None
    input = st.text_input('🔍')
    st.session_state.input = input
    all_food = []
    for mealtype in ['메인반찬','단품요리', '간식', '음료']:#
        for foodtype in ['음식']: #,'가공식품'
            FS = NS.FoodScorer(gender, height, weight, state, PDk, eGFR, uACR, protein_loss, albumin, FBG, OGTT, HbA1c, TG, LDL, SBP, DBP, CK, CP, CCa, mealtype, foodtype, 100)
            resulting_diets, total_nutritions = FS.import_diet(mealtype, foodtype) # type: ignore
            diet_scores = []
            for i in range(len(resulting_diets)):
                total_nutrition = total_nutritions[i]
                resulting_diet = resulting_diets[i][0]
                CHOS,ProS,FatS,NaS,SugarS,KS,PS,diet_score = FS.diet_scoring(total_nutrition, mealtype)
                diet_scores.append((resulting_diet[2],resulting_diet[0], total_nutrition[0],total_nutrition[1],total_nutrition[2],total_nutrition[3],
                                    total_nutrition[4],total_nutrition[5], total_nutrition[6],total_nutrition[7],diet_score))
            all_food.extend(diet_scores)

    all_food_df = pd.DataFrame(all_food)
    all_food_df.columns = ['음식명','1회제공량',"칼로리","탄수화물","단백질","지방","나트륨","칼륨","인","당류","총점수"]
    all_food_df['총점수'] = all_food_df['총점수'].astype(int)
    all_food_df['등급'] = pd.cut(all_food_df['총점수'], bins=[-float('inf'), 10, 20, 30, 40, 50, 60, 70, 80, 90, float('inf')],
                    labels=['F', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+'])
    all_food_df['점수, 등급'] = all_food_df['총점수'].astype(str) + '\n' + all_food_df['등급'].astype(str)
    all_food_df = all_food_df.drop('총점수',axis=1).drop('등급',axis=1)
    all_food_df = all_food_df.set_index('점수, 등급')
    st.session_state.filtered_df = all_food_df[all_food_df['음식명'].str.contains(input)]

    st.write(st.session_state.filtered_df)

with tab3:
    if 'mealtype' not in st.session_state:
        st.session_state.mealtype = None
    if 'foodtype' not in st.session_state:
        st.session_state.foodtype = None
    if 'result_df' not in st.session_state:
        st.session_state.result_df = None

    meal = st.selectbox('식사를 원하시나요, 간식을 원하시나요?', ('식단', '간식'))
    st.session_state.mealtype = meal
    food = st.selectbox('직접 요리해드실건가요?', ('음식', '가공식품'))
    st.session_state.foodtype = food
    top_n = 10
    
    st.write('식품 점수를 계산 중입니다...')
    FS = NS.FoodScorer(gender, height, weight, state, PDk, eGFR, uACR, protein_loss, albumin, FBG, OGTT, HbA1c, TG, LDL, SBP, DBP, CK, CP, CCa, st.session_state.mealtype, st.session_state.foodtype, top_n)
    st.session_state.top_diet = FS.top_diets()

    st.subheader('오늘의 추천 식단')
    st.session_state.result_df = FS.diet_ranking(st.session_state.top_diet).sample(n=1).transpose()
    st.write(st.session_state.result_df)

    Ncalc = NC.NutritionCalculator(gender, height, weight, state, PDk, eGFR, uACR, protein_loss, albumin, FBG, OGTT, HbA1c, TG, LDL, SBP, DBP, CK, CP, CCa)

    st.subheader('하루 영양 구성')
    st.text('OOO님의 건강정보를 분석한 결과,\n다음과 같이 하루 권장 섭취 기준을 제안해요.')
    nutrient_criteria, eer, weight = Ncalc.print_nutrient_criteria()
    st.write(f'권장 칼로리는 {eer}kcal 입니다.')
    st.write(nutrient_criteria)
    st.write(f'주의가 필요한 영양소는 {weight}입니다.')