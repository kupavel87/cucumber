def Purchase_to_Dict(purchases):
    result = {}
    for item in purchases:
        purchase = (item.id, item.fp)
        id = item.author_id
        if id in result:
            result[id].append(purchase)
        else:
            result[id] = [purchase]
    return result
