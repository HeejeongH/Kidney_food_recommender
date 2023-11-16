import pandas as pd
from Diagnose import Diagnose as DG

class NutritionCalculator:
    def __init__(self, gender, height, weight, state, PDk, eGFR, uACR, protein_loss, albumin, FBG, OGTT, HbA1c, TG, LDL, SBP, DBP, CK, CP, CCa):
        self.weight = weight # 체중
        self.state = state # NA (일반인), CKD (만성신부전), HD (혈액투석), PD (복막투석)
        self.PDk = PDk # 복막투석 시 투석액 칼로리
        self.sw, self.bmi, self.albumin, self.kidney, self.diabetes, self.blood_pressure, self.triglycerides, self.cholesterol, self.K, self.P, self.Ca = DG(gender, height, weight, state, PDk, eGFR, uACR, protein_loss, albumin, FBG, OGTT, HbA1c, TG, LDL, SBP, DBP, CK, CP, CCa).diagnose()
        self.EER = self.calculate_eer()
        self.Nutrients = self.calculate_day_nutrient_criteria()

    def calculate_eer(self):      
        if self.bmi > 25:
            eer = self.weight * 30 - 500
        else:
            if self.sw * 1.1 >= self.weight >= self.sw * 0.9:
                eer = self.weight * 30
            else:
                eer = self.sw * 30

        if self.state == 'PD':
            return eer - self.PDk
        else:
            return eer

    def calculate_day_nutrient_criteria(self):
        weight = []

        # 탄수화물
        if self.diabetes == '정상': # 당뇨 없는 환자
            CHO_range = [self.EER * 0.55 / 4, self.EER * 0.65 / 4]
        else: # 당뇨병 환자
            weight.append('Sugar') 
            CHO_range = [self.EER * 0.45 / 4, self.EER * 0.6 / 4]
        Sugar = (self.EER * 0.1) / 4

        # 단백질
        if self.state == 'CKD': # 비투석 만성 콩팥병 환자
            Pro_range = [self.sw * 0.8, self.sw * 0.8]
        elif self.state == 'PD' or self.state == 'HD': # 투석 환자
            Pro_range = [self.sw * 1.0, self.sw * 1.2]
        else: # 비환자
            Pro_range = [self.sw * 0.8, self.sw * 1]

        # 지방        
        if self.triglycerides == '높음' and self.state != 'NA': # 고중성지질 + 신기능 이상 환자
            Fat_range = [self.EER * 0.15 / 9, self.EER * 0.15 / 9]
        else: # 중성지질 정상
            Fat_range = [self.EER * 0.15 / 9, self.EER * 0.3 / 9]

        if self.cholesterol == '높음' and ((self.diabetes != '정상' and self.state == 'CKD') or (59 >= self.eGFR)): 
            weight.append('Cholesterol') # 저밀도 콜레스테롤 높음 & ((당뇨병 & 만성콩팥병) or (만성콩팥병 3단계 이상))

        # 나트륨       
        if self.blood_pressure != '정상' or self.diabetes != '정상' : # 고혈압 or 당뇨병
            Na = 2000
            weight.append('Na')
        else:
            if self.state == 'CKD' or self.state == 'HD':
                Na = 2000
            elif self.state == 'PD':
                Na = 3000
            else:
                Na = 2300

        # 칼륨
        if self.K == '높음': # 고칼륨혈증
            weight.append('K')
            K = 2535 if self.state == 'PD' else 2000 # 복막투석 / 나머지
        else: # 고칼륨혈증이 없을 경우
            if self.state == 'HD': # 혈액투석
                K = 2500 # < 2000~3000
            else:
                K = 3500

        # 인
        if self.P == '높음': # 혈중 인 농도 4.5 이내
            weight.append('P')

        if self.state == 'NA': # 신기능 정상
            P = 1000
        elif self.state == 'CKD': #만성신부전
            P = self.sw * 12 # 8~12mg 이하
        else: # 혈액투석 or 복막투석
            P = self.sw * 17 # 17mg 이하

        return {
            'Nutrients': ['Carbohydrate (g)', 'Protein (g)', 'Fat (g)', 'Na (mg)', 'K (mg)', 'P (mg)', 'Sugar (g)'],
            'min': [round(CHO_range[0],2), round(Pro_range[0],2), round(Fat_range[0],2), '-', '-', '-', '-'],
            'Max': [round(CHO_range[1],2), round(Pro_range[1],2), round(Fat_range[1],2), round(Na,2), round(K,2), round(P,2), round(Sugar,2)],
            'Weight': [weight,'-', '-', '-', '-', '-', '-']}

    def print_nutrient_criteria(self):
        df = pd.DataFrame(self.Nutrients)
        df1 = df[['Nutrients','min','Max']]
        df1.columns=['영양소','최소 권장 섭취량','최대 권장 섭취량']
        df1 = df1.set_index('영양소')
        eer = round(self.EER,2)
        weight_list = df['Weight'][0]
        weight = []
        for w in weight_list:
            temp = w.replace('Sugar','당').replace('Cholesterol','콜레스테롤').replace('Na','나트륨').replace('K','칼륨').replace('P','인')
            weight.append(temp)
        return df1, eer, weight

    def calculate_meal_nutrient_criteria(self, mealtype):
        criteria=self.calculate_day_nutrient_criteria()
        per = 0.1 if (mealtype == "간식" or mealtype == "음료") else 0.3

        EER = self.EER*per
        CHOA=criteria['min'][0]*per
        CHOB=criteria['Max'][0]*per
        ProA=criteria['min'][1]*per
        ProB=criteria['Max'][1]*per
        FatA=criteria['min'][2]*per
        FatB=criteria['Max'][2]*per
        Na=criteria['Max'][3]*per
        K=criteria['Max'][4]*per
        P=criteria['Max'][5]*per
        Sugar=criteria['Max'][6]*per      

        return [EER, CHOA, CHOB, ProA, ProB, FatA, FatB, Na, K, P, Sugar]