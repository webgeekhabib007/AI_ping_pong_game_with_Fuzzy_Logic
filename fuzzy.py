from collections import defaultdict
def fuzzy_rule(ambient_light, user_preference):
    mp = defaultdict(float)
    mp1 = defaultdict(float)

    if(ambient_light <= 0):
        mp["dark"] = 0.0
        mp["dim"] = 0.0
        mp["bright"] = 0.0
    elif 0 <ambient_light <=40:
        mp["dark"] = 1.0
        mp["dim"] = 0.0
        mp["bright"] = 0.0
    elif 40 < ambient_light <=50:
        mp["dark"] = max(0.0,(ambient_light-40)/10)
        mp["dim"] = max(0.0,(50-ambient_light)/10)
        mp["bright"] = 0.0
    elif 50 <ambient_light <=100:
        mp["dark"] = 0.0
        mp["dim"] = 1.0
        mp["bright"] = 0.0
    elif 100 < ambient_light <=150:
        mp["dark"] = 0.0
        mp["dim"] = max(0.0,(ambient_light-100)/50)
        mp["bright"] = max(0.0,(150-ambient_light)/50)
    elif 150 <ambient_light <=500:
        mp["dark"] = 0.0
        mp["dim"] = 0.0
        mp["bright"] = 1.0
    elif 500 <ambient_light :
        mp["dark"] = 0.0
        mp["dim"] = 0.0
        mp["bright"] = 0.0

    if user_preference<=0:
        mp1["dim"] = 0.0
        mp1["low"] = 0.0
        mp1["medium"] = 0.0
        mp1["high"] = 0.0
        mp1["bright"] = 0.0
    elif 0<user_preference<=20:
        mp1["dim"] = 1.0
        mp1["low"] = 0.0
        mp1["medium"] = 0.0
        mp1["high"] = 0.0
        mp1["bright"] = 0.0

    elif 20<user_preference<=30:
        mp1["dim"] = max(0.0,(user_preference-20)/10)
        mp1["low"] = max(0.0,(30-user_preference)/10)
        mp1["medium"] = 0.0
        mp1["high"] = 0.0
        mp1["bright"] = 0.0
    elif 30<user_preference<=40:
        mp1["dim"] = 0.0
        mp1["low"] = 1.0
        mp1["medium"] = 0.0
        mp1["high"] = 0.0
        mp1["bright"] = 0.0

    elif 40<user_preference<=50:
        mp1["dim"] = 1.0
        mp1["low"] = max(0.0,(user_preference-40)/10)
        mp1["medium"] = max(0.0,(50-user_preference)/10)
        mp1["high"] = 0.0
        mp1["bright"] = 0.0
    elif 50<user_preference<=60:
        mp1["dim"] = 0.0
        mp1["low"] = 0.0
        mp1["medium"] = 1.0
        mp1["high"] = 0.0
        mp1["bright"] = 0.0
    elif 60<user_preference<=70:
        mp1["dim"] = 0.0
        mp1["low"] = 1.0
        mp1["medium"] = max(0.0,(user_preference-60)/10)
        mp1["high"] = max(0.0,(70-user_preference)/10)
        mp1["bright"] = 0.0
    elif 70<user_preference<=80:
        mp1["dim"] = 0.0
        mp1["low"] = 0.0
        mp1["medium"] = 0.0
        mp1["high"] = 1.0
        mp1["bright"] = 0.0

    elif 80<user_preference<=90:
        mp1["dim"] = 0.0
        mp1["low"] = 0.0
        mp1["medium"] = 1.0
        mp1["high"] = max(0.0,(user_preference-80)/10)
        mp1["bright"] = max(0.0,(90-user_preference)/10)
    elif 90<user_preference<=100:
        mp1["dim"] = 0.0
        mp1["low"] = 0.0
        mp1["medium"] = 0.0
        mp1["high"] = 0.0
        mp1["bright"] = 1.0

    elif user_preference>100:
        mp1["dim"] = 0.0
        mp1["low"] = 0.0
        mp1["medium"] = 0.0
        mp1["high"] = 0.0
        mp1["bright"] = 0.0


    if mp["dark"]>0 and mp1["dim"]>0 :
        return "dim"
    elif mp["dark"]>0 and mp1["low"]>0:
        return "low"
    elif mp["dim"]>0 and mp1["low"]>0:
        return "dim"
    elif mp["dim"]>0 and mp1["medium"]>0:
        return "medium"
    elif mp["bright"]>0 and mp1["bright"]>0:
        return "bright"
    
    

ambient_light_value = 48  
user_preference_value = 55 

brightness_level = fuzzy_rule(ambient_light_value, user_preference_value)
print(f"Brightness level: {brightness_level}")


