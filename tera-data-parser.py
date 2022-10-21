from modules.logger.logger import Logger
from modules.config.config import Config
from modules.database.database import Database

try:
	from Lib.Tools import Tools, performance
	from Lib.Abnorms import Abnorms
	from Lib.Items import Items
	from Lib.Skills import Skills
	from Lib.Crests import Crests
	from Lib.Areas import Areas

except ImportError:
	from .Lib.Tools import Tools, performance
	from .Lib.Abnorms import Abnorms
	from .Lib.Items import Items
	from .Lib.Skills import Skills
	from .Lib.Crests import Crests
	from .Lib.Areas import Areas


BASE = "."
NAME = "tera-data-parser"


class DataParser:
	def __init__(self, logger, config, database, debug):
		self.log = logger
		self.cfg = config
		self.database = database
		self.debug = debug
		self.tools = Tools(self.log, BASE, self.debug)

	def runReader(self):
		# Performance Counter Start
		perfStart = performance("start")
		# Get attributes
		attributes = self.tools.getAttributes("item")
		attributes = self.tools.sortIterable(attributes)
		attributes = "\n".join(attributes)
		if self.tools.saveTxt('./output/attributes.txt', attributes):
			# Performance Counter End
			perfStop = performance("end", perfStart)
			self.log.info(f"Total elapsed time: {round(perfStop, 3)}s ({round(perfStop / 60, 1)}min)")
		else:
			self.log.info("Something went wrong!")

	def runParser(self, entity: str):
		self.log.info("*" * 50)
		# Performance Counter Start
		perfStart = performance("start")
		# Check for database and connect
		link, conn = self.database.connectMysql()
	
		match entity:
			case 'items':
				itemsClass = Items(self.log, self.tools, BASE)
				# Gather items and display names
				items = {}
				items = itemsClass.itemsRead(items)
				items = itemsClass.itemsAddName(items)
				# Insert data into database
				if itemsClass.itemsInsertDb(items, link, conn):
					# Performance Counter End
					perfStop = performance("end", perfStart)
					self.log.info(f"Total elapsed time: {round(perfStop, 3)}s ({round(perfStop / 60, 1)}min)")
				else:
					self.log.info("Something went wrong!")
	
			case 'abnormality':
				abnormsClass = Abnorms(self.log, self.tools, BASE)
				# Gather abnorms, its icons and display names
				abnorms = {}
				abnorms = abnormsClass.abnormsRead(abnorms)
				abnorms = abnormsClass.abnormsAddString(abnorms)
				abnorms = abnormsClass.abnormsAddIcon(abnorms)
				# Insert data into database
				if abnormsClass.abnormsInsertDb(abnorms, link, conn):
					# Performance Counter End
					perfStop = performance("end", perfStart)
					self.log.info(f"Total elapsed time: {round(perfStop, 3)}s ({round(perfStop / 60, 1)}min)")
				else:
					self.log.info("Something went wrong!")
	
			case 'skills':
				skillsClass = Skills(self.log, self.tools, BASE)
				# Gather skills, its icons and display names
				skills = {}
				skills = skillsClass.skillsRead(skills)
				skills = skillsClass.skillsAddData(skills)
				skills = skillsClass.skillsAddIcon(skills)
				# Insert data into database
				if skillsClass.skillsInsertDb(skills, link, conn):
					# Performance Counter End
					perfStop = performance("end", perfStart)
					self.log.info(f"Total elapsed time: {round(perfStop, 3)}s ({round(perfStop / 60, 1)}min)")
				else:
					self.log.info("Something went wrong!")
	
			case 'crests':
				crestsClass = Crests(self.log, self.tools, BASE)
				# Gather crests, its icons and display names
				crests = {}
				crests = crestsClass.crestsRead(crests)
				crests = crestsClass.crestsAddString(crests)
				crests = crestsClass.crestsAddIcon(crests)
				# Insert data into database
				if crestsClass.crestsInsertDb(crests, link, conn):
					# Performance Counter End
					perfStop = performance("end", perfStart)
					self.log.info(f"Total elapsed time: {round(perfStop, 3)}s ({round(perfStop / 60, 1)}min)")
				else:
					self.log.info("Something went wrong!")
	
			case 'areas':
				areasClass = Areas(self.log, self.tools, BASE)
				# Gather areas and display names
				areas = {}
				areas = areasClass.areasRead(areas)
				areas = areasClass.areasAddString(areas)
				# Insert data into database
				if areasClass.areasInsertDb(areas, link, conn):
					# Performance Counter End
					perfStop = performance("end", perfStart)
					self.log.info(f"Total elapsed time: {round(perfStop, 3)}s ({round(perfStop / 60, 1)}min)")
				else:
					self.log.info("Something went wrong!")
	
		# Close connection
		conn.close()
		self.log.info("*" * 50)


def run(logger: any):

	global BASE
	if logger is None:
		BASE = "."
		LOGGER = Logger(name=NAME)
	else:
		BASE = f"./modules/{NAME}"
		LOGGER = logger

	CONFIG = Config(path=f"{BASE}/config.ini").readConfig()
	LOGGER.info(f"Starting {CONFIG['VKore']['name']}")

	DEBUG = True if CONFIG['Settings']['debug'] == "True" or CONFIG['Settings']['debug'] == "true" else False

	DATA = Database(LOGGER, CONFIG)
	DP = DataParser(LOGGER, CONFIG, DATA, DEBUG)

	for entity, enable in CONFIG['Parser'].items():
		if enable == "True" or enable == "true":
			DP.runParser(entity)


if __name__ == '__main__':
	run(None)

	# # parse items
	# runParser(CONFIG, 'items', debug)
	# # parse abnorms
	# runParser(CONFIG, 'abnormality', debug)
	# # parse skills
	# runParser(CONFIG, 'skills', debug)
	# # parse glyphs
	# runParser(CONFIG, 'crests', debug)
	# # parse areas
	# runParser(CONFIG, 'areas', debug)
