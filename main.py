import utils


def runReader(config, debug=False):
	# Performance Counter Start
	perfStart = utils.performance("start")
	# Get attributes
	attributes = utils.getAttributes("item", debug)
	attributes = utils.sortIterable(attributes)
	attributes = "\n".join(attributes)
	if utils.saveTxt('./output/attributes.txt', attributes):
		# Performance Counter End
		perfStop = utils.performance("end", perfStart)
		print(f"Total elapsed time: {round(perfStop, 3)}s ({round(perfStop / 60, 1)}min)")
	else:
		print("Something went wrong!")


def runParser(config: dict, type: str, debug: bool = False):
	# Performance Counter Start
	perfStart = utils.performance("start")
	# Check for database and connect
	link, conn = utils.dbConnect(config)

	match type:
		case 'items':
			# Gather items and display names
			items = {}
			items = utils.itemsRead(items, debug)
			items = utils.itemsAddName(items, debug)
			# Insert data into database
			if utils.itemsInsertDb(items, link, conn):
				# Performance Counter End
				perfStop = utils.performance("end", perfStart)
				print(f"Total elapsed time: {round(perfStop, 3)}s ({round(perfStop / 60, 1)}min)")
			else:
				print("Something went wrong!")
		case 'abnormality':
			# Gather items and display names
			abnorms = {}
			abnorms = utils.abnormsRead(abnorms, debug)
			abnorms = utils.abnormsAddString(abnorms, debug)
			abnorms = utils.abnormsAddIcon(abnorms, debug)
			# Insert data into database
			if utils.abnormsInsertDb(abnorms, link, conn):
				# Performance Counter End
				perfStop = utils.performance("end", perfStart)
				print(f"Total elapsed time: {round(perfStop, 3)}s ({round(perfStop / 60, 1)}min)")
			else:
				print("Something went wrong!")

	# Close connection
	conn.close()



if __name__ == '__main__':
	config = utils.readConfig('config.ini')
	debug = True if config['Parser']['debug'] == "True" else False
	runParser(config, 'items', debug)
	runParser(config, 'abnormality', debug)
