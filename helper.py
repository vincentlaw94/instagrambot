
def removeElements(array, value):
    ret = []
    for x in array:
        if x != value:
            ret.append(x)

    return ret
