import configparser
import datetime
import json
import urllib.error
import xml.etree.ElementTree as xml
from os.path import exists, isdir
from os import makedirs, listdir
from shutil import copyfile
import codecs
import pymysql


def dbConnect(config: dict):
    host = config['Parser']['db_host']
    user = config['Parser']['db_user']
    password = config['Parser']['db_pass']
    database = config['Parser']['db_base']
    charset = 'utf8mb4'
    cursorclass = pymysql.cursors.DictCursor

    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        charset=charset,
        cursorclass=cursorclass
    )

    link = conn.cursor()
    link.execute("SELECT VERSION()")
    data = link.fetchone()
    print (f"Database version: {data['VERSION()']}")
    return link, conn


def readConfig(ini: str) -> dict:
    """ Read config, check for errors and store values

    :param ini: Path to config_wa_gw.ini
    :return: Config as dict
    """
    # Read config
    config = configparser.ConfigParser()
    config.read(ini)
    # Check debug mode
    if config['Parser']['debug'] == "True":
        print("Debug Mode Enabled")
    return config


# noinspection PyArgumentList
def loadXML(path: str, comments=False, useBackup=False, debug: bool=False):
    if not exists(path): raise Exception(f'Path {path} doesn\'t exist!')
    if useBackup: backup(path, debug)
    parser = xml.XMLParser(target=xml.TreeBuilder(insert_comments=comments))
    tree = xml.parse(path,parser)
    root = tree.getroot()
    if debug: print(f'Loaded {path}')
    return tree, root


def saveXML(path: str, tree: xml.ElementTree, debug: bool=False):
    xml.indent(tree, space='\t')
    tree.write(path, encoding='utf-8-sig',xml_declaration=True)
    string = xml.tostring(tree.getroot(),'unicode').replace('\n','\r\n')
    string = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n{string}"
    with codecs.open(path,'w','utf-8-sig') as file:
        file.write(string)
    if debug: print(f'Saved {path}')


def saveTxt(path: str, string: str, debug: bool=False) -> bool:
    with open(path,'w') as file:
        file.write(string)
    if debug: print(f'Saved {path}')
    return True


def saveJson(path: str, dict: dict, sort: bool=False, debug: bool=False) -> bool:
    with open(path,'w') as file:
        if sort:
            json.dump(dict, file, sort_keys=True, indent=4)
        else:
            json.dump(dict, file, indent=4)
    if debug: print(f'Saved {path}')
    return True


def backup(path, debug: bool=False) -> str:
    bak = path+'.bak'
    if not exists(bak):
        copyfile(path, bak)
        if debug: print(f'Created {bak}')
    else:
        print(f"{bak} already exists!")
    return bak


def getAllXML(path: str) -> list:
    files = []
    for file in listdir(f"./data/{path}"):
        if file.endswith(".xml"):
            files.append(file)
    return files


def sortIterable(list: set, debug: bool=False) -> list:
    if debug: print(f"Sorting Entities...")
    listSorted = sorted(list)
    listNo = len(listSorted)
    if debug: print(f"Sorting Entities complete: {listNo}")
    return listSorted


def sortDictionary(dict: dict, debug: bool=False) -> dict:
    if debug: print(f"Sorting Entities...")
    dictSorted = {k: dict[k] for k in sorted(dict)}
    dictNo = len(dictSorted)
    if debug: print(f"Sorting Entities complete: {dictNo}")
    return dictSorted


def getAttributes(typ: str, debug: bool=False) -> set:
    print(f"Getting Attributes...")
    files = getAllXML(typ)
    attributes = set()
    for file in files:
        treeItem, rootItem = loadXML(path=f'./data/{typ}/{file}', debug=debug)
        for item in rootItem.findall('Item'):
            attributes.update(item.attrib.keys())
    # print(attributes)
    attributesNo = len(attributes)
    print(f"Getting Attributes complete: {attributesNo}")
    return attributes


def itemsRead(items: dict, debug: bool=False) -> dict:
    print(f"Reading Items...")
    dir = "Item"
    files = getAllXML(dir)
    itemNo = 0
    for file in files:
        treeItem, rootItem = loadXML(path=f'./data/{dir}/{file}', debug=debug)
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
    return sortDictionary(items, debug)


def itemsAddName(items: dict, debug: bool=False) -> dict:
    print(f"Adding Item Names...")
    dir = "StrSheet_Item"
    files = getAllXML(dir)
    itemNo = 0
    for file in files:
        treeItem, rootItem = loadXML(path=f'./data/{dir}/{file}', debug=debug)
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
                classes = classes + str(getClassId(typ)) + ";"
            classes = classes[:-1]

        races = ""
        if data['races']:
            for typ in data['races'].split(';'):
                races = races + str(getRaceId(typ)) + ";"
            races = races[:-1]

        gender = ""
        if data['gender']:
            gender = str(getGenderId(data['gender']))

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


def abnormsRead(abnorms: dict, debug: bool=False) -> dict:
    print(f"Reading Abnormalities...")
    dir = "Abnormality"
    files = getAllXML(dir)
    abnormsNo = 0
    for file in files:
        treeAbnorm, rootAbnorm = loadXML(path=f'./data/{dir}/{file}', debug=debug)
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
    return sortDictionary(abnorms, debug)


def abnormsAddString(abnorms: dict, debug: bool=False) -> dict:
    print(f"Adding Abnormality Strings...")
    dir = "StrSheet_Abnormality"
    files = getAllXML(dir)
    abnormsNo = 0
    for file in files:
        treeAbnorm, rootAbnorm = loadXML(path=f'./data/{dir}/{file}', debug=debug)
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
    files = getAllXML(dir)
    abnormsNo = 0
    for file in files:
        treeAbnorm, rootAbnorm = loadXML(path=f'./data/{dir}/{file}', debug=debug)
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


def skillsRead(skills: dict, debug: bool=False) -> dict:
    print(f"Reading User Skills...")
    dir = "UserSkill"
    files = getAllXML(dir)
    skillsNo = 0
    for file in files:
        sub = {}
        treeSkill, rootSkill = loadXML(path=f'./data/{dir}/{file}', debug=debug)
        for skill in rootSkill.findall('Skill'):
            skillsNo = skillsNo + 1
            skillsId = str(skill.get('id'))
            skillsClassId = str(int(skill.get('templateId').replace('110', '')) - 1)
            # append to sub dict
            sub[skillsId] = {}
            sub[skillsId]['id'] = skillsId
            sub[skillsId]['class'] = skillsClassId
            sub[skillsId]['type'] = skill.get('type') if skill.get('type') else 'n/a'
            sub[skillsId]['category'] = skill.get('category').split(',')[0] if skill.get('category') else '0'
            sub[skillsId]['parentId'] = skill.get('parentId') if skill.get('parentId') else '0'
            sub[skillsId]['nextSkill'] = skill.get('nextSkill') if skill.get('nextSkill') else '0'
            sub[skillsId]['connectNextSkill'] = skill.get('connectNextSkill') if skill.get('connectNextSkill') else '0'
            sub[skillsId]['totalAtk'] = skill.get('totalAtk') if skill.get('totalAtk') else '0'
            sub[skillsId]['pvpAtkRate'] = skill.get('pvpAtkRate') if skill.get('pvpAtkRate') else '0'
            sub[skillsId]['abnormality'] = skill.get('abnormalityOnShot') if skill.get('abnormalityOnShot') else '0'
            # append to dict
            skills[skillsClassId] = {}
            skills[skillsClassId] = sortDictionary(sub, debug)

    print(f"Reading User Skills complete: {skillsNo}")
    return sortDictionary(skills, debug)


def skillsAddData(skills: dict, debug: bool=False) -> dict:
    print(f"Adding User Skill Data...")
    dir = "StrSheet_UserSkill"
    files = getAllXML(dir)
    skillsNo = 0
    infoData = {}

    for file in files:
        treeSkill, rootSkill = loadXML(path=f'./data/{dir}/{file}', debug=debug)
        for skill in rootSkill.findall('String'):
            skillsId = str(skill.get('id'))
            skillsClassId = str(getClassId(skill.get('class')))

            # append to dict
            if skillsClassId in skills:
                if skillsId in skills[skillsClassId]:
                    skillsNo = skillsNo + 1
                    skills[skillsClassId][skillsId]['name'] = skill.get('name') if skill.get('name') else ''
                    skills[skillsClassId][skillsId]['tooltip'] = skill.get('tooltip') if skill.get('tooltip') else ''
                    skills[skillsClassId][skillsId]['race'] = str(getRaceId(skill.get('race')))
                    skills[skillsClassId][skillsId]['gender'] = str(getGenderId(skill.get('gender')))

                    infoKey = f"{skillsClassId}-{skills[skillsClassId][skillsId]['category']}"
                    infoData[f"{infoKey}-name"] = skill.get('name') if skill.get('name') else ''
                    infoData[f"{infoKey}-tooltip"] = skill.get('tooltip') if skill.get('tooltip') else ''
                    infoData[f"{infoKey}-race"] = str(getRaceId(skill.get('race')))
                    infoData[f"{infoKey}-gender"] = str(getGenderId(skill.get('gender')))


    for classKey, classVal in skills.items():
        for skillKey, skillVal in classVal.items():
            if 'name' not in skillVal:
                infoKey = f"{skillVal['class']}-{skillVal['category']}"
                if f"{infoKey}-name" in infoData:
                    skillsNo = skillsNo + 1
                    skillVal['name'] = infoData[f"{infoKey}-name"]
                    skillVal['tooltip'] = infoData[f"{infoKey}-tooltip"]
                    skillVal['race'] = infoData[f"{infoKey}-race"]
                    skillVal['gender'] = infoData[f"{infoKey}-gender"]
                else:
                    skillVal['name'] = ""
                    skillVal['tooltip'] = ""
                    skillVal['race'] = ""
                    skillVal['gender'] = ""

    print(f"Adding User Skill Data complete: {skillsNo}")
    return skills


def skillsAddIcon(skills: dict, debug: bool=False) -> dict:
    print(f"Adding User Skill Icons...")
    dir = "UserSkillIcon"
    files = getAllXML(dir)
    skillsNo = 0
    iconData = {}

    for file in files:
        treeSkill, rootSkill = loadXML(path=f'./data/{dir}/{file}', debug=debug)
        for skill in rootSkill.findall('Icon'):
            skillsId = str(skill.get('skillId'))
            skillsClassId = str(getClassId(skill.get('class')))
            # append to dict
            if skillsClassId in skills:
                if skillsId in skills[skillsClassId]:
                    skillsNo = skillsNo + 1
                    skills[skillsClassId][skillsId]['icon'] = skill.get('iconName') if skill.get('iconName') else ''
                    iconData[f"{skillsClassId}-{skills[skillsClassId][skillsId]['category']}"] = skill.get('iconName')

    for classKey, classVal in skills.items():
        for skillKey, skillVal in classVal.items():
            if 'icon' not in skillVal:
                iconKey = f"{skillVal['class']}-{skillVal['category']}"
                if iconKey in iconData:
                    skillsNo = skillsNo + 1
                    skillVal['icon'] = iconData[iconKey]
                else:
                    skillVal['icon'] = ""

    print(f"Adding User Skill Icons complete: {skillsNo}")
    return skills


def skillsInsertDb(skills: dict, link, conn) -> bool:
    print(f"Inserting User Skills...")
    save = True
    skillsNo = 0
    for classId, classSkills in skills.items():
        for skillId, skillData in classSkills.items():

            skillId = skillData['id']
            name = skillData['name']
            tooltip = skillData['tooltip']
            icon = skillData['icon'].replace('.', '/')
            charClass = skillData['class']
            charRace = skillData['race']
            charGender = skillData['gender']
            type = skillData['type']
            category = skillData['category']
            parentId = skillData['parentId']
            nextSkill = skillData['nextSkill']
            connectNextSkill = skillData['connectNextSkill']
            totalAtk = skillData['totalAtk']
            pvpAtkRate = skillData['pvpAtkRate']
            abnormality = skillData['abnormality']

            query = f'INSERT INTO skills (skillId, name, tooltip, icon, charClass, charRace, charGender, type, category, parentId, nextSkill, connectNextSkill, totalAtk, pvpAtkRate, abnormality) ' \
                    f'VALUES ("{skillId}", "{name}", "{tooltip}", "{icon}", "{charClass}", "{charRace}", "{charGender}", "{type}", "{category}", "{parentId}", "{nextSkill}", "{connectNextSkill}", "{totalAtk}", "{pvpAtkRate}", "{abnormality}")'
            try:
                link.execute(query)
                conn.commit()
                skillsNo = skillsNo + 1
            except:
                save = False
                conn.rollback()
                print("Error while writing into Database!")

    if save: print(f"Inserting User Skills complete: {skillsNo}")
    return save


def performance(stage: str, time=False) -> datetime:
    match stage:
        case "start":
            return datetime.datetime.now()
        case "end":
            return (datetime.datetime.now() - time).total_seconds()


def getGenderId(name: str) -> int:
    match name.lower():
        case "male":
            return 0
        case "female":
            return 1
        case "common":
            return 9


def getRaceId(name: str) -> int:
    match name.lower():
        case "human":
            return 0
        case "highelf":
            return 1
        case "aman":
            return 2
        case "castanic":
            return 3
        case "popori":
            return 4
        case "baraka":
            return 5
        case "common":
            return 9


def getClassId(name: str) -> int:
    match name.lower():
        case "warrior":
            return 0
        case "lancer":
            return 1
        case "slayer":
            return 2
        case "berserker":
            return 3
        case "sorcerer":
            return 4
        case "archer":
            return 5
        case "priest":
            return 6
        case "elementalist":  # mystic
            return 7
        case "soulless":  # reaper
            return 8
        case "engineer":  # gunner
            return 9
        case "fighter":  # brawler
            return 10
        case "assassin":  # ninja
            return 11
        case "glaiver":  # valkyrie
            return 12
        case "common":  # all
            return 99

# itemSearch = item.get('searchable')
# itemCombatType = item.get('combatItemType')
# itemCombatSubType = item.get('combatItemSubType')
# itemRank = item.get('rank')
# itemConversion = item.get('conversion')
# itemSortNumber = item.get('sortingNumber')
# itemDropType = item.get('dropType')
# itemBuyPrice = item.get('buyPrice')
# itemSellPrice = item.get('sellPrice')
# itemTerritory = item.get('useOnlyTerritory')
# itemDivide = item.get('divide')
# itemUseCount = item.get('itemUseCount')
# itemDropMax = item.get('maxDropUnit')
# itemStackMax = item.get('maxStack')
# itemSlotLimit = item.get('slotLimit')
# itemCooldownGroup = item.get('coolTimeGroup')
# itemCooldown = item.get('coolTime')
# itemStorable = item.get('warehouseStorable')
# itemStorableGuild = item.get('guildWarehouseStorable')
# itemBoundType = item.get('boundType')
# itemDestroy = item.get('destroyable')
# itemDismantle = item.get('dismantlable')
# itemSellMerchant = item.get('storeSellable')
# itemRelocate = item.get('relocatable')
# itemArtisan = item.get('artisanable')
# itemEnchant = item.get('enchantEnable')
# itemGradeUnknown = item.get('unidentifiedItemGrade')
# itemMasterpieceRate = item.get('masterpieceRate')
# itemLinkEquipId = item.get('linkEquipmentId')
# itemLinkLookId = item.get('linkLookInfoId')
# itemChangeLook = item.get('changeLook')
# itemExtractLook = item.get('extractLook')
