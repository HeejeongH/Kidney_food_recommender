class Diagnose:
    def __init__(self, gender, height, weight, state, PDk, eGFR, uACR, protein_loss, albumin, FBG, OGTT, HbA1c, TG, LDL, SBP, DBP, CK, CP, CCa):
        self.gender = gender # 성별
        self.height = height # 신장
        self.weight = weight # 체중
        self.state = state # NA (일반인), CKD (만성신부전), HD (혈액투석), PD (복막투석)
        self.PDk = PDk # 복막투석 시 투석액 칼로리
        self.eGFR = eGFR # 사구체 여과율
        self.uACR = uACR # 알부민뇨
        #self.protein_loss = protein_loss # 단백뇨
        self.albumin = albumin # 혈중 알부민
        self.FBG = FBG # 공복혈당 (mg/dL)
        self.OGTT = OGTT # 경구당부하 (mg/dL)
        self.HbA1c = HbA1c # 당화혈색소 (%)
        self.TG = TG # 중성지방
        self.LDL = LDL # 저밀도 콜레스테롤
        self.SBP = SBP # 수축기혈압
        self.DBP = DBP # 이완기혈압
        self.CK = CK # 혈중 칼륨 농도
        self.CP = CP # 혈중 인 농도
        self.CCa = CCa # 혈중 칼슘 농도

    def standard_weight(self):
        factor = 22 if self.gender == 'male' else 21
        return self.height * self.height * factor

    def diagnose_bmi(self):
        return self.weight/(self.height*self.height)
    
    def diagnose_kidney(self):
        if self.eGFR >= 90:
            if self.uACR < 30:
                return 'G1, 낮은 위험'
            elif self.uACR < 300:
                return 'G1, 중증도 위험'
            return 'G1, 높은 위험'
        elif 60 <= self.eGFR <= 89:
            if self.uACR < 30:
                return 'G2, 낮은 위험'
            elif self.uACR < 300:
                return 'G2, 중증도 위험'
            return 'G2, 높은 위험'
        elif 45 <= self.eGFR <= 59:
            if self.uACR < 30:
                return 'G3a, 중증도 위험'
            elif self.uACR < 300:
                return 'G3a, 높은 위험'
            return 'G3a, 매우 높은 위험'
        elif 30 <= self.eGFR <= 44:
            if self.uACR < 30:
                return 'G3b, 높은 위험'
            return 'G3b, 매우 높은 위험'
        elif 15 <= self.eGFR <= 29:
            return 'G4, 매우 높은 위험'
        return 'G5, 매우 높은 위험'

    def diagnose_albumin(self):
        return '저알부민혈증' if self.albumin < 3.5 else '정상'
    
    def diagnose_diabetes(self):
        if  126 > self.FBG >= 100 or 200 > self.OGTT >= 140 or 5.7 <= self.HbA1c <= 6.4:
            return '당뇨병 전단계'
        elif self.FBG >= 126 or self.OGTT >=200 or self.HbA1c > 6.5:
            return '당뇨병'
        else:
            return '정상'
        
    def diagnose_triglycerides(self):
        return '높음' if self.TG >= 500 else '정상'

    def diagnose_cholesterol(self):
        return '높음' if self.LDL >= 100 else '정상'
    
    def diagnose_blood_pressure(self):
        if 120 <= self.SBP <= 129 or 80 <= self.DBP <= 84:
            return '고혈압 전단계 1기'
        elif 130 <= self.SBP <= 139 or 85 <= self.DBP <= 89:
            return '고혈압 전단계 2기'
        elif 140 <= self.SBP <= 159 or 90 <= self.DBP <= 99:
            return '고혈압 1기'
        elif 160 <= self.SBP or 100 <= self.DBP:
            return '고혈압 2기'
        elif 140 <= self.SBP and self.DBP < 90:
            return '고립성 수축기 고혈압'
        return '정상'

    def K_blood_concentration(self):
        if self.CK > 5.5 :
            return '높음' 
        elif self.CK <3.5:
            return '낮음'
        else:
            return '정상'
    def P_blood_concentration(self):    
        if self.CP > 4.5 :
            return '높음' 
        elif self.CP <2.5:
            return '낮음'
        else:
            return '정상'
    def Ca_blood_concentration(self):
        if self.CCa > 10.2 :
            return '높음' 
        elif self.CCa <8.4:
            return '낮음'
        else:
            return '정상'
    
    def diagnose(self):
        sw = self.standard_weight()
        bmi = self.diagnose_bmi()
        albumin = self.diagnose_albumin()
        kidney = self.diagnose_kidney()
        diabetes = self.diagnose_diabetes()
        blood_pressure = self.diagnose_blood_pressure()
        triglycerides = self.diagnose_triglycerides()
        cholesterol = self.diagnose_cholesterol()
        K = self.K_blood_concentration()
        P = self.P_blood_concentration()
        Ca = self.Ca_blood_concentration()
        
        return sw, bmi, albumin, kidney, diabetes, blood_pressure, triglycerides, cholesterol, K, P, Ca