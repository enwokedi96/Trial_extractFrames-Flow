def twoSum(arr=[1,3,5,5], A=4):
    hashTable = {}
    # check each element in array
    for i in range(0, len(arr)):
        print(hashTable)
        
        # calculate A minus current element
        sumMinusElement = A / arr[i]
        # check if this number exists in hash table
        if sumMinusElement in hashTable:
            return True
        
        # add the current number to the hash table
        hashTable[arr[i]] = True

    return False

# string_ = input("Enter string: ")
# print("All people and monsters:", string_)

def extract_smallest_group(str_):
    groups = str_.split("$")
    groups.remove("")
    min_length = float("inf")

    for i in groups:
        group = i.split("@")
        # group.remove("")
        lengths= [len(j) for j in group]
        min_length = min(min(lengths), min_length)
    return min_length

# res = extract_smallest_group(string_)
# print("rsults: ",res)

#-------------------------------------------------
# monster_indices = []

# for idx, i in enumerate(string_):
#     if i == "$" or i == "@":
#         monster_indices.append(idx)

# print("MONSTER INDICES!!: ", monster_indices)

# people = []
# for idx, j in enumerate(monster_indices):
#     if idx==0 and j==0: people.append(string_[1:monster_indices[idx+1]])
#     elif idx==0 and  j!=0: people.append(string_[:j])
#     else:
#         if j==0 and idx==1: continue
#         else: 
#             people.append(string_[monster_indices[idx-1]+1:j])
#             if j==monster_indices[-1] and j<len(string_): 
#                 people.append(string_[j+1:])
# print("people groups include:",people)

# people_lens = [len(i) for i in people]
# print("minimum group size is: ", min(people_lens))
# print(twoSum())

# ------------------------------- #------------------------------

def finndRepeats(n, m):
    repeating_numbers, repeating_count = [], 0

    for i in range(n, m+1):
        str_form = str(i)
        if len(str_form)==2:
            if str_form[0] == str_form[1]: 
                repeating_numbers.append(i)
                repeating_count = repeating_count + 1
        else:
            if str_form[0] == str_form[1] or str_form[0] == str_form[2] or str_form[1] == str_form[2] or str_form[0] == str_form[1] == str_form[2]:
                repeating_numbers.append(i)
                repeating_count = repeating_count + 1

    print("Repeating numbers: ", repeating_numbers)
    print("Repeating numbers count: ", repeating_count)
    print("Non-repeating numbers count: ", m-n+1-repeating_count)

valid_auth_tokens = ["ah37j2ha483u", "safh34ywhOp5", "ba34wyi8t902"]
requests = [["GET", "https://ex.xom/?token=safh34ywhOp5&name=alex&age=meowy"],
            ["GET", "https://ex.xom/?token=safh34ywhOp5&name=sam&sex=male"],
            ["POST", "https://ex.xom/?token=msnnsns&name=alex"],
            ["POST", "https://ex.xom/?token=ah37j2ha483u&name=alex&csrf=123456789"],
            ["POST", "https://ex.xom/?token=ba34wyi8t902&name=sammy&csrf=1MM23456789"]
            ]

capitals = ["A","B","C","D","E","F","G","H","I","J",
            "K","L","M","N","O","P","Q","R","S","T","U",
            "V","W","X","Y","Z"]

def getResponses(valid_auth_tokens=valid_auth_tokens, requests=requests):
    response=[]
    
    for i,request in enumerate(requests):
        params = request[1].split("?")[1]
        split_params = params.split("&")
        correct_response = ""
        if request[0]=="GET":
            param_name, param_value = "", ""
            for j in split_params:
                param_name, param_value = j.split("=")
                if param_name=="token":
                    if param_value in valid_auth_tokens:
                        correct_response = "VALID"
                    else:
                        correct_response = "INVALID"
                        # response.append(correct_response)
                        break
                else:
                    correct_response += "," + param_name + "," + param_value

        elif request[0]=="POST":
            param_name, param_value, correct_response = "", "", ""
            for j in split_params:
                param_name, param_value = j.split("=")
                print(param_name)
                # print(param_name, param_value)
                if param_name=="token":
                    if param_value in valid_auth_tokens:
                        if "VALID" in correct_response: continue
                        correct_response = "VALID"
                    else:
                        correct_response = "INVALID"
                        # response.append(correct_response)
                        break 
                elif param_name=="csrf":
                    checkForCapitalLetter = any(chars in param_value for chars in capitals)
                    if checkForCapitalLetter==True or len(param_value)<=8:
                        correct_response = "INVALID"
                        # response.append(correct_response)
                        break
                    else: 
                        if "VALID" in correct_response: continue
                        correct_response = "VALID"
                else:
                    # print(param_name, param_value)
                    correct_response += "," + param_name + "," + param_value     
        response.append(correct_response)
    print (response)

getResponses()    


