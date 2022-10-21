from .Tools import getClassId
from .Tools import getRaceId
from .Tools import getGenderId


class Skills:
    def __init__(self, logger, tools, base):
        self.log = logger
        self.tools = tools
        self.base = base
        
    def skillsRead(self, skills: dict) -> dict:
        self.log.info(f"Reading User Skills...")
        dir = "UserSkill"
        files = self.tools.getAllXML(dir)
        skillsNo = 0
        for file in files:
            sub = {}
            treeSkill, rootSkill = self.tools.loadXML(path=f'{self.base}/data/{dir}/{file}')
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
                skills[skillsClassId] = self.tools.sortDictionary(sub)
    
        self.log.info(f"Reading User Skills complete: {skillsNo}")
        return self.tools.sortDictionary(skills)
    
    def skillsAddData(self, skills: dict) -> dict:
        self.log.info(f"Adding User Skill Data...")
        dir = "StrSheet_UserSkill"
        files = self.tools.getAllXML(dir)
        skillsNo = 0
        infoData = {}
    
        for file in files:
            treeSkill, rootSkill = self.tools.loadXML(path=f'{self.base}/data/{dir}/{file}')
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
    
        self.log.info(f"Adding User Skill Data complete: {skillsNo}")
        return skills
    
    def skillsAddIcon(self, skills: dict) -> dict:
        self.log.info(f"Adding User Skill Icons...")
        dir = "UserSkillIcon"
        files = self.tools.getAllXML(dir)
        skillsNo = 0
        iconData = {}
    
        for file in files:
            treeSkill, rootSkill = self.tools.loadXML(path=f'{self.base}/data/{dir}/{file}')
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
    
        self.log.info(f"Adding User Skill Icons complete: {skillsNo}")
        return skills
    
    def skillsInsertDb(self, skills: dict, link, conn) -> bool:
        self.log.info(f"Inserting User Skills...")
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
    
                query = f'INSERT INTO data_skills (skillId, name, tooltip, icon, charClass, charRace, charGender, type, category, parentId, nextSkill, connectNextSkill, totalAtk, pvpAtkRate, abnormality) ' \
                        f'VALUES ("{skillId}", "{name}", "{tooltip}", "{icon}", "{charClass}", "{charRace}", "{charGender}", "{type}", "{category}", "{parentId}", "{nextSkill}", "{connectNextSkill}", "{totalAtk}", "{pvpAtkRate}", "{abnormality}")'
                try:
                    link.execute(query)
                    conn.commit()
                    skillsNo = skillsNo + 1
                except:
                    save = False
                    conn.rollback()
                    self.log.info("Error while writing into Database!")
    
        if save: self.log.info(f"Inserting User Skills complete: {skillsNo}")
        return save
