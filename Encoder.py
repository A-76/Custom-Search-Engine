def encode(str_word): # from 16 bit to 8bit
    result = bytearray()
    for i in range(len(str_word)):
        b = "b'\x00"
        c = ord(str_word[i])
        if (c >= 48 and c <= 57): # 0-9
            result.append(c + 4)
        elif (c >= 65 and c <= 90):# A-Z
            result.append(c - 65)
        elif (c >= 97 and c <= 122):# a-z
            result.append(c - 71)
            #b = (c - 71).to_bytes(1, 'big')
        elif (c == 39):# "'"
            result.append(63)
        elif (c == 44):# "%"
            result.append(64)
        elif (c == 36):# "$"
            result.append(65)
        elif (c == 8364):# "€"
            result.append(66)
        elif (c == 163):# "£"
            result.append(67)
        elif (c == 165):# "¥"
            result.append(68)
        
    print(len(result))
    return result


def decode(data): #byte[] 
    result = ""
    for i in range(len(data)):
        b = data[i]
        if (b == 68):
            result += "¥"
        elif (b == 67):
            result += "£"
        elif (b == 66):
            result += "€"
        elif (b == 65):
            result += "$"
        elif (b == 64):
            result += "%"
        elif (b == 63):
            result += "'"
        elif (b > 51):
            result += chr(b - 4)
        elif (b > 25):
            result += chr(b + 71)
        else:
            result += chr(b + 65)
    print(result)
    return result


decode(encode("abcxyz012789ABCXYZ'¥"))