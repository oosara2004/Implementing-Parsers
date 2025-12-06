from SimpleLR1Builder import LR1

def TokenizeG1(G):
   
    G = G.strip().replace(" ", "").lower()
    tokens = []

    for ch in G:
        if ch in ("a", "b"):
            tokens.append(ch)
        else:
            return None
    return tokens


def TokenizeG2(G):
    
    G = G.strip().replace(" ", "").lower()
    tokens = []
    i = 0
    while i < len(G):
        if G[i:i+2] == "id":
            tokens.append("id")
            i += 2
        elif G[i] in ("*", "="):
            tokens.append(G[i])
            i += 1
        else:
            return None
    return tokens

def Parse_with3(Tokens , Action , GOTO , Productions):

     if not Tokens or Tokens[-1]!="$":
         Tokens=Tokens+["$"] #if string doesnt end with a $ add it OR IF EMPTY add $

     Stack=[0]
     pointer=0 #for input
   
     print(f"{'Stack':<40} {'Input':<40} {'Action':<10}{'Output':<10}")

     while True:
         state=Stack[-1] 
         lookahead=Tokens[pointer]

         if state in Action and lookahead in Action[state]:
           action=Action[state][lookahead]
         else:
           action= None

           #added output after .
         outputString="...."

         if action and action.startswith("r"):
            ProductionNum=int(action[1:])
            LHS2,RHS2=Productions[ProductionNum-1]
              
            if RHS2:
                 rhString="".join(RHS2)
            else:
              rhString="ε"
            outputString=f"{LHS2}->{rhString}"   

         stackString=" ".join(map(str,Stack))
         inputString=" ".join(Tokens[pointer:])#from pointer to the last input
         actionString=action if action else "Error"# check if there is an action if yes assign else if none let it be Error
   
         print(f"{stackString:<40} {inputString:<40} {actionString:<10} {outputString:<10}")
  
         #check if there is an Error
         if action is None or action=="":
            print("Error")
            return False
   
         if action=="acc":
           print("Accepted")
           return True
   
         #Check for what action s,r56as
         if action.startswith("s"):
            nextState=int(action[1:]) #take the # of the next state
            Stack.append(lookahead) #Add lookahead to the stack
            Stack.append(nextState) #and the # of state we are in
            pointer+=1 #Increment the pointer to point to the next input
            continue
     
         if action.startswith("r"):
            ProductionNum=int(action[1:]) 
            LHS,RHS=Productions[ProductionNum-1]
            x=len(RHS)#how many inputs to pop out of stack

            for _ in range(2 * x): #2*x since each symbol has its state
              Stack.pop()
          
            state2=Stack[-1]
          
            if state2 in GOTO and LHS in GOTO[state2]:
                gotoState=GOTO[state2][LHS]
            else:
                gotoState=None
               
            if gotoState is None:
              print("Error")
              return False
          
            Stack.append(LHS) 
            Stack.append(gotoState) 
            continue
         
         print("Error")
         return False
     
 
if __name__ == "__main__":
 b = LR1("G2") 
 C, ACTION, GOTO = b.build()
 productions=b.prods
 tokens=["e","d","i"]
 tokens1=["id","="]
 tokens2=["id","=","id","*","id"]
 

 print("\n _____Parsing using LALR table_____")
 Parse_with3(tokens,ACTION,GOTO,productions)