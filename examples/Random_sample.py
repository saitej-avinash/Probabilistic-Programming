import random as ran

count = 0

def check2():
    x =ran.randint(0,4)
    y= ran.randint(0,4)
    if x > 1:
        #return 0
        if x > y:
            return 0
        else:
            return 0
    else:
        
        if x==0 :
                
            return 
        else :
            return 1
        
        return False

def check():
    x = ran.randint(1, 5) 
    y = ran.randint(1, 5)  
    #z2= ran.randint(1, 5)

    if x > 1:

        #return 1

        if x > y:

            return 1

            #if  y < z2 :
            
                #return 1
    return 0

def check3():
    x = ran.randint(1,3)
    y= ran.randint(1,3)
    z= ran.randint(1,3)

    if x > 1 : 
        if y > x : 
            if z > 1 :
                return 1



def check4(): 
    x =ran.randint(1,3)
    y= ran.randint(1,3)

    if  x>1 :
        if y>x:
            x=y
        else : 
            x = x+1
    if x>2:
        return 1
    return 0


 
z = 100000  # Number of trials
for _ in range(z):
    if check4():
        count += 1

probability = (count / z) * 100
print(f"Probability of x < y: {probability:.2f}%")
