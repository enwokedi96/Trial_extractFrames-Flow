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

        
    
print(twoSum())