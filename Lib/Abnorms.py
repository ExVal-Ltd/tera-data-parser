from Lib import Tools


def abnormsRead(abnorms: dict, debug: bool=False) -> dict:
    print(f"Reading Abnormalities...")
    dir = "Abnormality"
    files = Tools.getAllXML(dir)
    abnormsNo = 0
    for file in files:
        treeAbnorm, rootAbnorm = Tools.loadXML(path=f'./data/{dir}/{file}', debug=debug)
        for abnorm in rootAbnorm.findall('Abnormal'):
            abnormsNo = abnormsNo + 1
            abnormsId = abnorm.get('id')
            # append to dict
            abnorms[abnormsId] = {}
            abnorms[abnormsId]['id'] = abnormsId
            abnorms[abnormsId]['kind'] = abnorm.get('kind') if abnorm.get('kind') else '0'
            abnorms[abnormsId]['level'] = abnorm.get('level') if abnorm.get('level') else '1'
            abnorms[abnormsId]['property'] = abnorm.get('property') if abnorm.get('property') else '1'
            abnorms[abnormsId]['category'] = abnorm.get('category') if abnorm.get('category') else '0'
            abnorms[abnormsId]['skillCategory'] = abnorm.get('bySkillCategory') if abnorm.get('bySkillCategory') else '0'
            abnorms[abnormsId]['time'] = abnorm.get('time') if abnorm.get('time') else '1'
            abnorms[abnormsId]['mobSize'] = abnorm.get('mobSize') if abnorm.get('mobSize') else ''
            abnorms[abnormsId]['priority'] = abnorm.get('priority') if abnorm.get('priority') else '1'
            abnorms[abnormsId]['infinity'] = '1' if abnorm.get('infinity') == "True" or abnorm.get('infinity') == "true" else '0'
            abnorms[abnormsId]['realtime'] = '1' if abnorm.get('realTime') == "True" or abnorm.get('realTime') == "true" else '0'
            abnorms[abnormsId]['isBuff'] = '1' if abnorm.get('isBuff') == "True" or abnorm.get('isBuff') == "true" else '0'
            abnorms[abnormsId]['isShow'] = '1' if abnorm.get('isShow') == "True" or abnorm.get('isShow') == "true" else '0'
            abnorms[abnormsId]['isStance'] = '1' if abnorm.get('isStance') == "True" or abnorm.get('isStance') == "true" else '0'
            abnorms[abnormsId]['group'] = abnorm.get('group') if abnorm.get('group') else ''

    print(f"Reading Abnormalities complete: {abnormsNo}")
    return Tools.sortDictionary(abnorms, debug)


def abnormsAddString(abnorms: dict, debug: bool=False) -> dict:
    print(f"Adding Abnormality Strings...")
    dir = "StrSheet_Abnormality"
    files = Tools.getAllXML(dir)
    abnormsNo = 0
    for file in files:
        treeAbnorm, rootAbnorm = Tools.loadXML(path=f'./data/{dir}/{file}', debug=debug)
        for abnorm in rootAbnorm.findall('String'):
            abnormId = abnorm.get('id')
            # append to dict
            if abnormId in abnorms:
                abnormsNo = abnormsNo + 1
                abnorms[abnormId]['name'] = abnorm.get('name') if abnorm.get('name') else ''
                abnorms[abnormId]['tooltip'] = abnorm.get('tooltip') if abnorm.get('tooltip') else ''

    for item, data in abnorms.items():
        if 'name' not in data:
            data['name'] = ""
        if 'tooltip' not in data:
            data['tooltip'] = ""

    print(f"Adding Abnormality Strings complete: {abnormsNo}")
    return abnorms


def abnormsAddIcon(abnorms: dict, debug: bool=False) -> dict:
    print(f"Adding Abnormality Icons...")
    dir = "AbnormalityIcon"
    files = Tools.getAllXML(dir)
    abnormsNo = 0
    for file in files:
        treeAbnorm, rootAbnorm = Tools.loadXML(path=f'./data/{dir}/{file}', debug=debug)
        for abnorm in rootAbnorm.findall('Icon'):
            abnormId = abnorm.get('abnormalityId')
            # append to dict
            if abnormId in abnorms:
                abnormsNo = abnormsNo + 1
                abnorms[abnormId]['icon'] = abnorm.get('iconName') if abnorm.get('iconName') else ''

    for item, data in abnorms.items():
        if 'icon' not in data:
            data['icon'] = ""

    print(f"Adding Abnormality Icons complete: {abnormsNo}")
    return abnorms


def abnormsInsertDb(abnorms: dict, link, conn) -> bool:
    print(f"Inserting Abnormalities...")
    save = True
    abnormNo = 0
    for abnorm, data in abnorms.items():

        id = data['id']
        kind = data['kind']
        level = data['level']
        property = data['property']
        category = data['category']
        skillCategory = data['skillCategory']
        time = data['time']
        mobSize = data['mobSize']
        priority = data['priority']
        infinity = data['infinity']
        realtime = data['realtime']
        isBuff = data['isBuff']
        isShow = data['isShow']
        isStance = data['isStance']
        group = data['group']

        name = data['name'].replace('"', "'")
        tooltip = data['tooltip'].replace('"', "'")
        icon = data['icon'].replace('.', '/')

        query = f'INSERT INTO abnorms (id, name, tooltip, icon, type, mobSize, kind, level, property, category, skillCategory, time, priority, infinity, realtime, isBuff, isShow, isStance) ' \
                f'VALUES ("{id}", "{name}", "{tooltip}", "{icon}", "{group}", "{mobSize}", "{kind}", "{level}", "{property}", "{category}", "{skillCategory}", "{time}", "{priority}", "{infinity}", "{realtime}", "{isBuff}", "{isShow}", "{isStance}")'
        try:
            link.execute(query)
            conn.commit()
            abnormNo = abnormNo + 1
        except:
            save = False
            conn.rollback()
            print("Error while writing into Database!")

    if save: print(f"Inserting Abnormalities complete: {abnormNo}")
    return save
