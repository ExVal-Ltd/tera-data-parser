import configparser
import datetime
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
def loadXML(path: str, comments=False, useBackup=False, debug=False):
    if not exists(path): raise Exception(f'Path {path} doesn\'t exist!')
    if useBackup: backup(path, debug)
    parser = xml.XMLParser(target=xml.TreeBuilder(insert_comments=comments))
    tree = xml.parse(path,parser)
    root = tree.getroot()
    if debug: print(f'Loaded {path}')
    return tree, root


def saveXML(path: str, tree: xml.ElementTree, debug=False):
    xml.indent(tree, space='\t')
    tree.write(path, encoding='utf-8-sig',xml_declaration=True)
    string = xml.tostring(tree.getroot(),'unicode').replace('\n','\r\n')
    string = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n{string}"
    if debug: print(f'Saved {path}')
    with codecs.open(path,'w','utf-8-sig') as file:
        file.write(string)


def saveTxt(path: str, string: str):
    with open(path,'w') as file:
        file.write(string)
    return True


def backup(path, debug=False):
    pybak = path+'.bak'
    if not exists(pybak):
        copyfile(path,pybak)
        if debug: print(f'Created {pybak}')
    return pybak


def getAllXML(path: str):
    files = []
    for file in listdir(f"./data/{path}"):
        if file.endswith(".xml"):
            files.append(file)
    return files


def sortIterable(list: set) -> list:
    print(f"Sorting Entities...")
    listSorted = sorted(list)
    listNo = len(listSorted)
    print(f"Sorting Entities complete: {listNo}")
    return listSorted


def getAttributes(typ: str, debug=False) -> set:
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


def itemsRead(items: dict, debug=False):
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
            items[itemId]['tradable'] = '1' if item.get('tradable') == "True" else '0'
            items[itemId]['obtainable'] = '1' if item.get('obtainable') == "True" else '0'
            items[itemId]['dyeable'] = '1' if item.get('changeColorEnable') == "True" else '0'
            items[itemId]['period'] = item.get('periodInMinute') if item.get('periodInMinute') else '0'
            items[itemId]['periodAdmin'] = '1' if item.get('periodByWebAdmin') == "True" else '0'

    print(f"Reading Items complete: {itemNo}")
    return items


def itemsAddName(items: dict, debug=False) -> dict:
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


def abnormsRead(abnorms: dict, debug=False):
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
            abnorms[abnormsId]['infinity'] = '1' if abnorm.get('infinity') == "True" else '0'
            abnorms[abnormsId]['realtime'] = '1' if abnorm.get('realTime') == "True" else '0'
            abnorms[abnormsId]['isBuff'] = '1' if abnorm.get('isBuff') == "True" else '0'
            abnorms[abnormsId]['isShow'] = '1' if abnorm.get('isShow') == "True" else '0'
            abnorms[abnormsId]['isStance'] = '1' if abnorm.get('isStance') == "True" else '0'
            abnorms[abnormsId]['group'] = abnorm.get('group') if abnorm.get('group') else ''

    print(f"Reading Abnormalities complete: {abnormsNo}")
    return abnorms


def abnormsAddString(abnorms: dict, debug=False) -> dict:
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


def abnormsAddIcon(abnorms: dict, debug=False) -> dict:
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

        query = f'INSERT INTO data_abnorms (id, name, tooltip, icon, type, mobSize, kind, level, property, category, skillCategory, time, priority, infinity, realtime, isBuff, isShow, isStance) ' \
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
