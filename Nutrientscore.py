import NutritionCalculator as NC
import pandas as pd
import glob

class FoodScorer:
    def __init__(self, gender, height, weight, state, PDk, eGFR, uACR, protein_loss, albumin, FBG, OGTT, HbA1c, TG, LDL, SBP, DBP, CK, CP, CCa, mealtype, foodtype, top_n):
        self.state=state
        self.eGFR=eGFR
        self.uACR=uACR
        self.mealtype = mealtype #  식단 메인반찬 단품요리 / 간식 간식콤보 음료
        self.foodtype = foodtype
        self.top_n=top_n
        self.Ncalc = NC.NutritionCalculator(gender, height, weight, state, PDk, eGFR, uACR, protein_loss, albumin, FBG, OGTT, HbA1c, TG, LDL, SBP, DBP, CK, CP, CCa)
    
    def import_diet(self, mealtype, foodtype):
        EER, _, _, _, _, _, _, _, _, _, _ = self.Ncalc.calculate_meal_nutrient_criteria(mealtype)
        resulting_diet = []
        total_nutrition = []

        if mealtype == '식단':
            name = 'diet'
        elif mealtype == '메인반찬':
            name = 'main'
        elif mealtype == '단품요리':
            name = 'one' 
        elif mealtype == '간식콤보':
            name = 'snack_combi'
        elif mealtype == '음료':
            name = 'beverage'
        else:
            name = 'snack'
        a='d' if foodtype == '음식' else 'p'
        
        file_list = glob.glob(f'food_DB/processed_DB/{name}/{name}{a}*.txt')
        for file in file_list[:10]:
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                i = 0
                while i < len(lines)-11:
                    diet = eval("["+lines[i].strip().split(": ")[1].replace("(","").replace(")","")+"]")
                    nutritions=[]
                    for j in range(1,9):
                        nutrition = float(lines[i+j].split(" ")[-1].replace("\n",""))
                        nutritions.append(nutrition)
                    if EER*0.5 <= nutritions[0] <= EER*1.5:
                        resulting_diet.append(diet)
                        total_nutrition.append(nutritions)
                    i += 11
        return resulting_diet, total_nutrition

    def diet_scoring(self, total_nutrition, mealtype):
        EER, CHOA, CHOB, ProA, ProB, FatA, FatB, Na, K, P, Sugar = self.Ncalc.calculate_meal_nutrient_criteria(mealtype)
        df = pd.DataFrame(self.Ncalc.calculate_day_nutrient_criteria())
        w=df['Weight'][0]
        
        Naw = 1.5 if 'Na' in w else 1
        Sugarw = 1.5 if 'Sugar' in w else 1
        if self.eGFR < 30 or self.uACR>300 or self.state != 'X':
            Kw = 1.5 if 'K' in w else 1
            Pw = 1.5 if 'P' in w else 1
        else:
            Kw = 0
            Pw = 0

        if total_nutrition[1]<CHOA:
            CHOS = max(1-((total_nutrition[1]-CHOA)/CHOA)**2, -1) *5
        elif total_nutrition[1]>CHOB:
            CHOS = max(1-((total_nutrition[1]-CHOB)/CHOA)**2, -1) *5
        else:
            CHOS = 1

        if total_nutrition[2]<ProA:
            ProS = max(1-((total_nutrition[2]-ProA)/ProA)**2, -1) *5
        elif total_nutrition[2]>ProB:
            ProS = max(1-((total_nutrition[2]-ProB)/ProA)**2, -1) *5
        else:
            ProS = 1

        if total_nutrition[3]<FatA:
            FatS = max(1-((total_nutrition[3]-FatA)/FatA)**2, -1) *5
        elif total_nutrition[3]>FatB:
            FatS = max(1-((total_nutrition[3]-FatB)/FatA)**2, -1) *5
        else:
            FatS = 1
        
        NaS = max(-total_nutrition[4]*Naw/Na, -2) *5
        SugarS = max(-total_nutrition[5]*Sugarw/Sugar, -2) *5
        KS = max(-total_nutrition[6]*Kw/K,-2) *5
        PS = max(-total_nutrition[7]*Pw/P, -2) *5
            
        Total_score = 75+CHOS+ProS+FatS+NaS+SugarS+KS+PS
        
        return CHOS,ProS,FatS,NaS,SugarS,KS,PS,Total_score
    
    def top_diets(self):
        resulting_diets, total_nutritions = self.import_diet(self.mealtype, self.foodtype) # type: ignore
        diet_scores = []
        for i in range(len(resulting_diets)):
            total_nutrition = total_nutritions[i]
            resulting_diet = resulting_diets[i]
            if self.mealtype == '메인반찬':
                resulting_diet = resulting_diets[i][0]
            CHOS,ProS,FatS,NaS,SugarS,KS,PS,diet_score = self.diet_scoring(total_nutrition, self.mealtype)
            diet_scores.append((resulting_diet, total_nutrition[0],total_nutrition[1],total_nutrition[2],total_nutrition[3],total_nutrition[4],total_nutrition[5], total_nutrition[6],total_nutrition[7],
                                CHOS,ProS,FatS,NaS,SugarS,KS,PS,diet_score))

        top_diets = sorted(diet_scores, key=lambda x: x[16], reverse=True)
        return top_diets
    
    def diet_ranking(self, top_diet):
        top_diets = top_diet[:self.top_n]
        results_list = []
        for rank, (diet, Calorie, CHO, Pro, Fat, Na, K, P, Sugar, CHOS,ProS,FatS,NaS,SugarS,KS,PS, score) in enumerate(top_diets, start=1):
            if self.mealtype == '메인반찬':
                comp = str(diet[2]+' '+diet[0]+'g')
            elif self.mealtype == '단품요리' or self.mealtype == '간식' or self.mealtype == '음료':
                diett = diet[0]
                comp = str(diett[2]+' '+diett[0]+'g')
            else:
                comp = ' & '.join(map(str, list(str(name[2]+' '+name[0]+'g') for name in diet)))
            result_dict = {
                "순위": rank,
                "식단 구성": comp,
                "식단 점수": round(score, 2),
                "칼로리": f"{round(Calorie,2)}kcal",
                "탄수화물": f"{round(CHO,2)}g ({round(CHOS,2)})",
                "단백질" : f"{round(Pro,2)}g ({round(ProS,2)})",
                "지방" : f"{round(Fat,2)}g ({round(FatS,2)})",
                "나트륨" : f"{round(Na,2)}mg ({round(NaS,2)})",
                "칼륨" : f"{round(K,2)}mg ({round(KS,2)})",
                "인" : f"{round(P,2)}mg ({round(PS,2)})",
                "당류" : f"{round(Sugar,2)}g ({round(SugarS,2)})"
            }
            results_list.append(result_dict)

        result_df = pd.DataFrame(results_list)
        result_df = result_df.set_index('순위')
        
        return result_df
    
    def find_food(self):
        all_food = []
        for mealtype in ['메인반찬','단품요리', '간식', '음료']:
            for foodtype in ['음식','가공식품']:
                resulting_diets, total_nutritions = self.import_diet(mealtype, foodtype) # type: ignore
                diet_scores = []
                for i in range(len(resulting_diets)):
                    total_nutrition = total_nutritions[i]
                    resulting_diet = resulting_diets[i]
                    if mealtype == '메인반찬':
                        resulting_diet = resulting_diets[i][0]
                    CHOS,ProS,FatS,NaS,SugarS,KS,PS,diet_score = self.diet_scoring(total_nutrition, mealtype)
                    diet_scores.append((resulting_diet, total_nutrition[0],total_nutrition[1],total_nutrition[2],total_nutrition[3],
                                        total_nutrition[4],total_nutrition[5], total_nutrition[6],total_nutrition[7],diet_score))
                    