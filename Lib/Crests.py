from Lib import Tools


def crestsRead(crests: dict, debug: bool=False) -> dict:
    print(f"Reading Crests...")
    dir = "Crest"
    files = Tools.getAllXML(dir)
    crestNo = 0
    for file in files:
        treeCrest, rootCrest = Tools.loadXML(path=f'./data/{dir}/{file}', debug=debug)
        for crest in rootCrest.findall('CrestItem'):
            crestNo = crestNo + 1
            crestId = crest.get('id')
            crestClassId = str(Tools.getClassId(crest.get('class')))
            # append to dict
            crests[crestId] = {}
            crests[crestId]['id'] = crestId
            crests[crestId]['class'] = crestClassId
            crests[crestId]['takePoint'] = crest.get('takePoint') if crest.get('takePoint') else '0'
            crests[crestId]['grade'] = crest.get('grade') if crest.get('grade') else '0'
            crests[crestId]['level'] = crest.get('level') if crest.get('level') else '1'
            crests[crestId]['parentId'] = crest.get('parentId') if crest.get('parentId') else '0'
            crests[crestId]['passivityLink'] = crest.get('passivityLink') if crest.get('passivityLink') else '0'
            crests[crestId]['obsolete'] = '1' if crest.get('obsolete') == "True" or crest.get('obsolete') == "true" else '0'

    print(f"Reading Crests complete: {crestNo}")
    return Tools.sortDictionary(crests, debug)


def crestsAddString(crests: dict, debug: bool=False) -> dict:
    print(f"Adding Crest Strings...")
    dir = "StrSheet_Crest"
    files = Tools.getAllXML(dir)
    crestNo = 0
    for file in files:
        treeCrest, rootCrest = Tools.loadXML(path=f'./data/{dir}/{file}', debug=debug)
        for crest in rootCrest.findall('String'):
            crestId = crest.get('id')
            # append to dict
            if crestId in crests:
                crestNo = crestNo + 1
                crests[crestId]['name'] = crest.get('name')
                crests[crestId]['skillName'] = crest.get('skillName')
                crests[crestId]['tooltip'] = crest.get('tooltip')

    for crest, data in crests.items():
        if 'name' not in data:
            data['name'] = ""
            data['skillName'] = ""
            data['tooltip'] = ""

    print(f"Adding Crest Strings complete: {crestNo}")
    return crests


def crestsAddIcon(crests: dict, debug: bool=False) -> dict:
    print(f"Adding Crest Icons...")
    dir = "CrestIcon"
    files = Tools.getAllXML(dir)
    crestsNo = 0
    for file in files:
        treeCrest, rootCrest = Tools.loadXML(path=f'./data/{dir}/{file}', debug=debug)
        for crest in rootCrest.findall('Icon'):
            crestId = crest.get('crestId')
            # append to dict
            if crestId in crests:
                crestsNo = crestsNo + 1
                crests[crestId]['icon'] = crest.get('iconName') if crest.get('iconName') else ''

    for item, data in crests.items():
        if 'icon' not in data:
            data['icon'] = ""

    print(f"Adding Crest Icons complete: {crestsNo}")
    return crests


def crestsInsertDb(crests: dict, link, conn) -> bool:
    print(f"Inserting Crests...")
    save = True
    crestNo = 0
    for crest, data in crests.items():

        id = data['id']
        name = data['name']
        skillName = data['skillName']
        tooltip = data['tooltip']
        icon = data['icon'].replace('.', '/')
        charClass = data['class']
        takePoint = data['takePoint']
        grade = data['grade']
        level = data['level']
        parentId = data['parentId']
        passivityLink = data['passivityLink']
        obsolete = data['obsolete']

        query = f'INSERT INTO crests (id, name, skillName, tooltip, icon, charClass, takePoint, grade, level, parentId, passivityLink, obsolete) ' \
                f'VALUES ("{id}", "{name}", "{skillName}", "{tooltip}", "{icon}", "{charClass}", "{takePoint}", "{grade}", "{level}", "{parentId}", "{passivityLink}", "{obsolete}")'
        try:
            link.execute(query)
            conn.commit()
            crestNo = crestNo + 1
        except:
            save = False
            conn.rollback()
            print("Error while writing into Database!")

    if save: print(f"Inserting Crests complete: {crestNo}")
    return save
