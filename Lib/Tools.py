import datetime
import json
import xml.etree.ElementTree as xml
from os.path import exists, isdir
from os import makedirs, listdir
from shutil import copyfile
import codecs


class Tools:
    def __init__(self, logger: any, base, debug: bool=False):
        self.log = logger
        self.debug = debug
        self.base = base
    
    # noinspection PyArgumentList
    def loadXML(self, path: str, comments=False, useBackup=False):
        if not exists(path): raise Exception(f'Path {path} doesn\'t exist!')
        if useBackup: self.backup(path)
        parser = xml.XMLParser(target=xml.TreeBuilder(insert_comments=comments))
        tree = xml.parse(path,parser)
        root = tree.getroot()
        if self.debug: self.log.info(f'Loaded {path}')
        return tree, root
    
    
    def saveXML(self, path: str, tree: xml.ElementTree):
        xml.indent(tree, space='\t')
        tree.write(path, encoding='utf-8-sig',xml_declaration=True)
        string = xml.tostring(tree.getroot(),'unicode').replace('\n','\r\n')
        string = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n{string}"
        with codecs.open(path,'w','utf-8-sig') as file:
            file.write(string)
        if self.debug: self.log.info(f'Saved {path}')
    
    
    def saveTxt(self, path: str, string: str) -> bool:
        with open(path,'w') as file:
            file.write(string)
        if self.debug: self.log.info(f'Saved {path}')
        return True
    
    
    def saveJson(self, path: str, dict: dict, sort: bool=False) -> bool:
        with open(path,'w') as file:
            if sort:
                json.dump(dict, file, sort_keys=True, indent=4)
            else:
                json.dump(dict, file, indent=4)
        if self.debug: self.log.info(f'Saved {path}')
        return True
    
    
    def backup(self, path) -> str:
        bak = path+'.bak'
        if not exists(bak):
            copyfile(path, bak)
            if self.debug: self.log.info(f'Created {bak}')
        else:
            self.log.info(f"{bak} already exists!")
        return bak
    
    
    def getAllXML(self, path: str) -> list:
        files = []
        for file in listdir(f"{self.base}/data/{path}"):
            if file.endswith(".xml"):
                files.append(file)
        return files
    
    
    def sortIterable(self, list: set) -> list:
        if self.debug: self.log.info(f"Sorting Entities...")
        listSorted = sorted(list)
        listNo = len(listSorted)
        if self.debug: self.log.info(f"Sorting Entities complete: {listNo}")
        return listSorted
    
    
    def sortDictionary(self, dict: dict) -> dict:
        if self.debug: self.log.info(f"Sorting Entities...")
        dictSorted = {k: dict[k] for k in sorted(dict)}
        dictNo = len(dictSorted)
        if self.debug: self.log.info(f"Sorting Entities complete: {dictNo}")
        return dictSorted
    
    
    def getAttributes(self, typ: str) -> set:
        self.log.info(f"Getting Attributes...")
        files = self.getAllXML(typ)
        attributes = set()
        for file in files:
            treeItem, rootItem = self.loadXML(path=f'{self.base}/data/{typ}/{file}')
            for item in rootItem.findall('Item'):
                attributes.update(item.attrib.keys())
        # self.log.info(attributes)
        attributesNo = len(attributes)
        self.log.info(f"Getting Attributes complete: {attributesNo}")
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
