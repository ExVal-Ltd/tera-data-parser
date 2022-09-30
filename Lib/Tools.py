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


def dbConnect(config: dict, debug: bool=False):
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
    if debug: print (f"Database version: {data['VERSION()']}")
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
