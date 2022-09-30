from Lib import Tools


def areasRead(areas: dict, debug: bool=False) -> dict:
    print(f"Reading Areas...")
    dir = "Area"
    files = Tools.getAllXML(dir)
    areaNo = 0
    contNo = 0
    for file in files:
        treeArea, rootArea = Tools.loadXML(path=f'./data/{dir}/{file}', debug=debug)
        for continent in rootArea.findall('Continent'):

            contNo = contNo + 1
            contId = continent.get('id')

            for area in continent.findall('HuntingZone'):
                areaNo = areaNo + 1
                areaId = area.get('id')
                # append to dict
                areas[areaId] = {}
                areas[areaId]['continent'] = contId
                areas[areaId]['huntingzone'] = areaId
                areas[areaId]['type'] = continent.get('channelType') if continent.get('channelType') else 'none'

    print(f"Reading Areas complete: {areaNo} ({contNo})")
    return Tools.sortDictionary(areas, debug)


def areasAddString(areas: dict, debug: bool=False) -> dict:
    print(f"Adding Area Strings...")
    dir = "StrSheet_Area"
    files = Tools.getAllXML(dir)
    areaNo = 0
    names = {}

    for file in files:
        treeArea, rootArea = Tools.loadXML(path=f'./data/{dir}/{file}', debug=debug)
        for area in rootArea.findall('String'):
            areaId = area.get('id')
            names[areaId] = area.get('string')

    for area, data in areas.items():
        if data['huntingzone'] in names:
            areaNo = areaNo + 1
            if data['huntingzone'] == "1":
                data['name'] = names['1002']
            elif data['huntingzone'] == "2":
                data['name'] = names['2001']
            elif data['huntingzone'] == "2000":
                data['name'] = names[f"2000000"]
            elif data['huntingzone'] == "2001":
                data['name'] = names[f"2000001"]
            elif data['huntingzone'] == "2002":
                data['name'] = names[f"2000002"]
            elif data['huntingzone'] == "2003":
                data['name'] = names[f"2000003"]
            elif data['huntingzone'] == "2009":
                data['name'] = names[f"2000104"]
            elif data['huntingzone'] == "2010":
                data['name'] = names[f"{data['huntingzone']}001"]
            elif data['huntingzone'] == "2011":
                data['name'] = names[f"{data['huntingzone']}001"]
            elif data['huntingzone'] == "2012":
                data['name'] = names[f"{data['huntingzone']}001"]
            elif data['huntingzone'] == "2013":
                data['name'] = names[f"{data['huntingzone']}001"]
            elif data['huntingzone'] == "2014":
                data['name'] = names[f"{data['huntingzone']}001"]
            elif data['huntingzone'] == "2015":
                data['name'] = names[f"{data['huntingzone']}001"]
            else:
                data['name'] = names[data['huntingzone']]
        elif f"{data['huntingzone']}000" in names:
            areaNo = areaNo + 1
            data['name'] = names[f"{data['huntingzone']}000"]
        elif f"{data['huntingzone']}001" in names:
            areaNo = areaNo + 1
            data['name'] = names[f"{data['huntingzone']}001"]
        elif data['continent'] in names:
            areaNo = areaNo + 1
            data['name'] = names[data['continent']]
        elif f"{data['continent']}000" in names:
            areaNo = areaNo + 1
            data['name'] = names[f"{data['continent']}000"]
        elif f"{data['continent']}001" in names:
            areaNo = areaNo + 1
            data['name'] = names[f"{data['continent']}001"]
        else:
            data['name'] = ""

    print(f"Adding Area Strings complete: {areaNo}")
    return areas


def areasInsertDb(areas: dict, link, conn) -> bool:
    print(f"Inserting Areas...")
    save = True
    areaNo = 0
    for area, data in areas.items():

        huntingzone = data['huntingzone']
        continent = data['continent']
        name = data['name']
        type = data['type']

        query = f'INSERT INTO areas (huntingzone, continent, name, type) ' \
                f'VALUES ("{huntingzone}", "{continent}", "{name}", "{type}")'
        try:
            link.execute(query)
            conn.commit()
            areaNo = areaNo + 1
        except:
            save = False
            conn.rollback()
            print("Error while writing into Database!")

    if save: print(f"Inserting Areas complete: {areaNo}")
    return save
