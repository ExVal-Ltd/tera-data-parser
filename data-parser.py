from Lib import Tools
from Lib import Abnorms
from Lib import Items
from Lib import Skills
from Lib import Crests
from Lib import Areas


def runReader(config, debug=False):
	# Performance Counter Start
	perfStart = Tools.performance("start")
	# Get attributes
	attributes = Tools.getAttributes("item", debug)
	attributes = Tools.sortIterable(attributes)
	attributes = "\n".join(attributes)
	if Tools.saveTxt('./output/attributes.txt', attributes):
		# Performance Counter End
		perfStop = Tools.performance("end", perfStart)
		print(f"Total elapsed time: {round(perfStop, 3)}s ({round(perfStop / 60, 1)}min)")
	else:
		print("Something went wrong!")


def runParser(config: dict, type: str, debug: bool = False):
	print("*" * 30)
	# Performance Counter Start
	perfStart = Tools.performance("start")
	# Check for database and connect
	link, conn = Tools.dbConnect(config)

	match type:
		case 'items':
			# Gather items and display names
			items = {}
			items = Items.itemsRead(items, debug)
			items = Items.itemsAddName(items, debug)
			# Insert data into database
			if Items.itemsInsertDb(items, link, conn):
				# Performance Counter End
				perfStop = Tools.performance("end", perfStart)
				print(f"Total elapsed time: {round(perfStop, 3)}s ({round(perfStop / 60, 1)}min)")
			else:
				print("Something went wrong!")

		case 'abnormality':
			# Gather abnorms, its icons and display names
			abnorms = {}
			abnorms = Abnorms.abnormsRead(abnorms, debug)
			abnorms = Abnorms.abnormsAddString(abnorms, debug)
			abnorms = Abnorms.abnormsAddIcon(abnorms, debug)
			# Insert data into database
			if Abnorms.abnormsInsertDb(abnorms, link, conn):
				# Performance Counter End
				perfStop = Tools.performance("end", perfStart)
				print(f"Total elapsed time: {round(perfStop, 3)}s ({round(perfStop / 60, 1)}min)")
			else:
				print("Something went wrong!")

		case 'skills':
			# Gather skills, its icons and display names
			skills = {}
			skills = Skills.skillsRead(skills, debug)
			skills = Skills.skillsAddData(skills, debug)
			skills = Skills.skillsAddIcon(skills, debug)
			# Insert data into database
			if Skills.skillsInsertDb(skills, link, conn):
				# Performance Counter End
				perfStop = Tools.performance("end", perfStart)
				print(f"Total elapsed time: {round(perfStop, 3)}s ({round(perfStop / 60, 1)}min)")
			else:
				print("Something went wrong!")

		case 'crests':
			# Gather crests, its icons and display names
			crests = {}
			crests = Crests.crestsRead(crests, debug)
			crests = Crests.crestsAddString(crests, debug)
			crests = Crests.crestsAddIcon(crests, debug)
			# Insert data into database
			if Crests.crestsInsertDb(crests, link, conn):
				# Performance Counter End
				perfStop = Tools.performance("end", perfStart)
				print(f"Total elapsed time: {round(perfStop, 3)}s ({round(perfStop / 60, 1)}min)")
			else:
				print("Something went wrong!")

		case 'areas':
			# Gather areas and display names
			areas = {}
			areas = Areas.areasRead(areas, debug)
			areas = Areas.areasAddString(areas, debug)
			# Insert data into database
			if Areas.areasInsertDb(areas, link, conn):
			# if Tools.saveJson('./test.json', areas, True):
				# Performance Counter End
				perfStop = Tools.performance("end", perfStart)
				print(f"Total elapsed time: {round(perfStop, 3)}s ({round(perfStop / 60, 1)}min)")
			else:
				print("Something went wrong!")

	# Close connection
	conn.close()
	print("*" * 50)



if __name__ == '__main__':
	# get configuration
	config = Tools.readConfig('config.ini')
	debug = True if config['Parser']['debug'] == "True" else False

	# parse items
	runParser(config, 'items', debug)
	# parse abnorms
	runParser(config, 'abnormality', debug)
	# parse skills
	runParser(config, 'skills', debug)
	# parse glyphs
	runParser(config, 'crests', debug)
	# parse areas
	runParser(config, 'areas', debug)
