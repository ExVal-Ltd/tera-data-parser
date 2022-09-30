from Lib import Tools


def itemsRead(items: dict, debug: bool=False) -> dict:
    print(f"Reading Items...")
    dir = "Item"
    files = Tools.getAllXML(dir)
    itemNo = 0
    for file in files:
        treeItem, rootItem = Tools.loadXML(path=f'./data/{dir}/{file}', debug=debug)
        for item in rootItem.findall('Item'):
            itemNo = itemNo + 1
            itemId = item.get('id')
            # append to dict
            items[itemId] = {}
            items[itemId]['id'] = itemId
            items[itemId]['category'] = item.get('category') if item.get('category') else ''
            items[itemId]['icon'] = item.get('icon') if item.get('icon') else ''
            items[itemId]['name'] = item.get('name') if item.get('name') else ''
            items[itemId]['grade'] = item.get('rareGrade') if item.get('rareGrade') else '0'
            items[itemId]['level'] = item.get('level') if item.get('level') else '1'
            items[itemId]['classes'] = item.get('requiredClass') if item.get('requiredClass') else ''
            items[itemId]['races'] = item.get('requiredRace') if item.get('requiredRace') else ''
            items[itemId]['gender'] = item.get('requiredGender') if item.get('requiredGender') else ''
            items[itemId]['tradable'] = '1' if item.get('tradable') == "True" or item.get('tradable') == "true" else '0'
            items[itemId]['obtainable'] = '1' if item.get('obtainable') == "True" or item.get('obtainable') == "true" else '0'
            items[itemId]['dyeable'] = '1' if item.get('changeColorEnable') == "True" or item.get('changeColorEnable') == "true" else '0'
            items[itemId]['period'] = item.get('periodInMinute') if item.get('periodInMinute') else '0'
            items[itemId]['periodAdmin'] = '1' if item.get('periodByWebAdmin') == "True" or item.get('periodByWebAdmin') == "true" else '0'

    print(f"Reading Items complete: {itemNo}")
    return Tools.sortDictionary(items, debug)


def itemsAddName(items: dict, debug: bool=False) -> dict:
    print(f"Adding Item Names...")
    dir = "StrSheet_Item"
    files = Tools.getAllXML(dir)
    itemNo = 0
    for file in files:
        treeItem, rootItem = Tools.loadXML(path=f'./data/{dir}/{file}', debug=debug)
        for item in rootItem.findall('String'):
            itemId = item.get('id')
            # append to dict
            if itemId in items:
                itemNo = itemNo + 1
                items[itemId]['name_de'] = item.get('string')
                items[itemId]['name_en'] = item.get('string')

    for item, data in items.items():
        if 'name_de' not in data:
            data['name_de'] = ""
            data['name_en'] = ""

    print(f"Adding Item Names complete: {itemNo}")
    return items


def itemsInsertDb(items: dict, link, conn) -> bool:
    print(f"Inserting Items...")
    save = True
    itemNo = 0
    for item, data in items.items():

        id = data['id']
        category = data['category']
        icon = data['icon'].replace('.', '/')
        name = data['name']
        grade = data['grade']
        level = data['level']
        obtainable = data['obtainable']
        tradable = data['tradable']
        dyeable = data['dyeable']
        period = data['period']
        periodAdmin = data['periodAdmin']
        name_de = data['name_de'].replace('"', "'")
        name_en = data['name_en'].replace('"', "'")

        classes = ""
        if data['classes']:
            for typ in data['classes'].split(';'):
                classes = classes + str(Tools.getClassId(typ)) + ";"
            classes = classes[:-1]

        races = ""
        if data['races']:
            for typ in data['races'].split(';'):
                races = races + str(Tools.getRaceId(typ)) + ";"
            races = races[:-1]

        gender = ""
        if data['gender']:
            gender = str(Tools.getGenderId(data['gender']))

        query = f'INSERT INTO items (id, category, icon, name, grade, level, classes, races, gender, obtainable, tradable, dyeable, period, periodByWebAdmin, name_de, name_en) ' \
                f'VALUES ("{id}", "{category}", "{icon}", "{name}", "{grade}", "{level}", "{classes}", "{races}", "{gender}", "{obtainable}", "{tradable}", "{dyeable}", "{period}", "{periodAdmin}", "{name_de}", "{name_en}")'
        try:
            link.execute(query)
            conn.commit()
            itemNo = itemNo + 1
        except:
            save = False
            conn.rollback()
            print("Error while writing into Database!")

    if save: print(f"Inserting Items complete: {itemNo}")
    return save
