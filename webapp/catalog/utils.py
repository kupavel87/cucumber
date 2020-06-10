def CatalogModel_for_select(catalog_list, dict_full_catalog=None):
    result = []
    for catalog in catalog_list:
        postfix = ''
        if dict_full_catalog:
            tmp = dict_full_catalog.get(catalog.id, 0)
            if tmp:
                postfix = ' ({})'.format(tmp)
            else:
                continue
        prefix = '--' * catalog.get_level()
        result.append((catalog.id, '{}{}{}'.format(prefix, catalog.name, postfix)))
        if len(catalog.children):
            result.extend(CatalogModel_for_select(catalog.children, dict_full_catalog))
    return result


def Products_to_Dict(products):
    result = {}
    for item in products:
        prod = {'id': item.id, 'name': item.name.replace('\"', '\''), 'code': item.code}
        id = item.catalog_id
        if id in result:
            result[id].append(prod)
        else:
            result[id] = [prod]
    return result


def CatalogChildrenCount(catalog_list, catalog_products_count):
    for catalog in catalog_list:
        result = 0
        if len(catalog.children):
            for child in catalog.children:
                if child.id not in catalog_products_count:
                    CatalogChildrenCount([child], catalog_products_count)
                result += catalog_products_count[child.id]
        else:
            result = len(catalog.products)
        catalog_products_count[catalog.id] = result
