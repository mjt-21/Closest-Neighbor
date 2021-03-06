import math
import pyodbc
import time
import functions

# Define a list of available pyodbc drivers
pyodbc_drivers = pyodbc.drivers();

# define server details
driver = '{ODBC Driver 17 for SQL Server}'
server = 'MSI'
db = 'Closest_Neighbor'
table = 'Lat_Longs'

# pyodbc extra details
SQL_ATTR_CONNECTION_TIMEOUT = 113
connection_timeout = 1
timeout = 1

global data

def testConnection(connString):
	try:
		conn = pyodbc.connect(connString, timeout=timeout, attrs_before={SQL_ATTR_CONNECTION_TIMEOUT: connection_timeout})
		conn.close()
		return True
	except:
		return False

def getDatabases(connString):
	if (not testConnection(connString)):
		return 1

	conn = pyodbc.connect(connString, attrs_before={SQL_ATTR_CONNECTION_TIMEOUT: connection_timeout})
	cursor = conn.cursor()
	query = '''SELECT name FROM sys.databases'''
	cursor.execute(query)
	data = cursor.fetchall()
	cursor.close()
	conn.close()

	databases = []
	for i in data:
		# Exclude system databases from results
		if i[0] != "master" and i[0] != "msdb" and i[0] != "model" and i[0] != "Resource" and i[0] != "tempdb":
			databases.append(i[0])

	return databases;
		
def getTables(connString, database):
	if (not testConnection(connString)):
		return 1

	conn = pyodbc.connect(connString, timeout=timeout, attrs_before={SQL_ATTR_CONNECTION_TIMEOUT: connection_timeout})
	cursor = conn.cursor()
	query = f'''SELECT * FROM {database}.sys.tables'''
	cursor.execute(query)
	data = cursor.fetchall()
	cursor.close()
	conn.close()

	tables = []
	for i in data:
		tables.append(i[0])

	return tables;

def getColumns(connString, table):
	if (not testConnection(connString)):
		return 1
	
	conn = pyodbc.connect(connString, timeout=timeout, attrs_before={SQL_ATTR_CONNECTION_TIMEOUT: connection_timeout})
	cursor = conn.cursor()
	query = f'''SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = \'{table}\''''
	cursor.execute(query)
	data = cursor.fetchall()
	cursor.close()
	conn.close()

	columns = []
	for i in data:
		columns.append(i[0])
	
	return columns

def selectAllData(connString, table):
	global data
	# connection string using the details above
	conn = pyodbc.connect(connString, timeout=timeout, attrs_before={SQL_ATTR_CONNECTION_TIMEOUT: connection_timeout})
	# create the connection cursor
	cursor = conn.cursor()
	# define our query
	query = '''SELECT * FROM ''' + table
	# run query
	cursor.execute(query)
	# get column names
	columns = [column[0] for column in cursor.description]
	# get data
	data = cursor.fetchall()
	# close the connection and remove the cursor
	cursor.close()
	conn.close()

	print(data)
	return data

########## Radius METHOD 1 ##########

#t0 = time.time()

#results = []

#for i in range (0, len(data)):
#    if i != centralPoint:
#        d = vincenty((data[centralPoint][0], data[centralPoint][1]), (data[i][0], data[i][1]), miles=True)

#        if d <= radius:
#            results.insert(len(results), (centralPoint, i, d))
			#print((centralPoint + 1, i + 1, d))

#t1 = time.time()
#print("len(results) =", len(results))
#print("\nTime:", t1 - t0)



########## Radius METHOD 2 ##########
### Improvements: Takes into account latitude, ruling out what has too high of a latitude value based on the radius given. ###

#t0 = time.time()

#latPerMile = 0.01428571428 # lat/mile, or 1/70 (70 for ~1.5% error margin)
#upperBound = data[centralPoint][0] + (radius * latPerMile)
#lowerBound = data[centralPoint][0] - (radius * latPerMile)

#results = []
#for i in range (0, len(data)):
#    if i != centralPoint:
#        if data[i][0] >= lowerBound and data[i][0] <= upperBound: #Checks if i'th point is within latitude range of radius
#            d = vincenty((data[centralPoint][0], data[centralPoint][1]), (data[i][0], data[i][1]), miles=True)
   
#            if d <= radius:
#                results.insert(len(results), (centralPoint, i, d))
				#print((centralPoint + 1, i + 1, d))

#t1 = time.time()

#print("len(results) =", len(results))
#print("\nTime:", t1 - t0)



########## Radius METHOD 3 ##########
### Improvements: Now takes into account longitude, ruling out what has too high of a longitude value based on the radius given. Now has a "square radius" with somewhat of an error margin to narrow results down. ###

def inRadius(pointID, radius, fileDestination):
	t0 = time.time()

	centralPoint = functions.linearSearch(pointID, data)

	latPerMile = 0.01459854014 # lat/mile, or 1/68.5 (68.5 for error margin)

	upperBound = data[centralPoint][1] + (radius * latPerMile)
	lowerBound = data[centralPoint][1] - (radius * latPerMile)
	leftBound = data[centralPoint][2] - abs(1/(math.cos(data[centralPoint][1]) * 69.172) * radius)
	rightBound = data[centralPoint][2] + abs(1/(math.cos(data[centralPoint][1]) * 69.172) * radius)

	results = []
	for i in range (0, len(data)):
		if i != centralPoint:
			if data[i][0] >= lowerBound and data[i][1] <= upperBound: # Checks if i'th point is within latitude range of radius
				if data[i][1] >= leftBound and data[i][2] <= rightBound: # Checks if i'th point is within longitude range of radius
					d = functions.vincenty((data[centralPoint][1], data[centralPoint][2]), (data[i][1], data[i][2]), miles=True)

					if d <= radius:
						results.insert(len(results), [data[centralPoint][0], data[centralPoint][1], data[centralPoint][2], data[i][0], data[i][1], data[i][2], functions.vincenty((data[centralPoint][1], data[centralPoint][2]), (data[i][1], data[i][2]), miles=True)])

	t1 = time.time()

	functions.quickSort(results, 0, len(results) - 1, 6)

	print("\nTime:", t1 - t0)
	print(fileDestination + "/output.csv")
	f = open((fileDestination + "/output.csv"), "x")

	f.write("ID1,ID1_Lat,ID1_Long,ID2,ID2_Lat,ID2_Long,Distance\n")

	for i in range(len(results)):
		for j in range(len(results[i])):
			f.write(str(results[i][j]))
			if j != len(results[i]) - 1:
				f.write(",")

		if i != len(results) - 1:
			f.write("\n")

	f.close()

# ########## Closest Neighbors METHOD 1 ##########

results = []

def withinBounds(pointID, radius):
	results = []

	centralPoint = functions.linearSearch(pointID, data)
	latPerMile = 0.01459854014 # lat/mile, or 1/68.5 (68.5 for error margin)

	upperBound = data[centralPoint][1] + (radius * latPerMile)
	lowerBound = data[centralPoint][1] - (radius * latPerMile)
	leftBound = data[centralPoint][2] - abs(1/(math.cos(data[centralPoint][1]) * 69.172) * radius)
	rightBound = data[centralPoint][2] + abs(1/(math.cos(data[centralPoint][1]) * 69.172) * radius)

	for i in range (0, len(data)):
		if i != centralPoint:
			if data[i][1] >= lowerBound and data[i][1] <= upperBound: # Checks if i'th point is within latitude range of radius
				if data[i][2] >= leftBound and data[i][2] <= rightBound: # Checks if i'th point is within longitude range of radius
					results.insert(len(results), [data[centralPoint][0], data[centralPoint][1], data[centralPoint][2], data[i][0], data[i][1], data[i][2], functions.vincenty((data[centralPoint][1], data[centralPoint][2]), (data[i][1], data[i][2]), miles=True)])

	return 0

def closestNeighbor(pointID, neighbors, fileDestination):
	t0 = time.time()

	results = []

	radius = 5

	lastAction = None

	while (len(results) < neighbors) and len(results) != neighbors:
		results = []
		withinBounds(pointID, radius)

		if len(results) == neighbors:
			break
		elif len(results) > neighbors:
			if lastAction and lastAction < 1:
				radius *= lastAction - .25
				lastAction -= .25
			else:
				radius *= .75
				lastAction = .75
		elif len(results) < neighbors:
			if lastAction and lastAction > 1:
				radius *= lastAction + .25
				lastAction += .25
			else:
				radius *= 1.25
				lastAction = 1.25

	functions.quickSort(results, 0, len(results) - 1, 6)
	del results[len(results) - (len(results) - neighbors) : len(results)]

	t1 = time.time()

	print("Time:", t1 - t0)
	print(fileDestination + "/output.csv")
	f = open((fileDestination + "/output.csv"), "x")

	f.write("ID1,ID1_Lat,ID1_Long,ID2,ID2_Lat,ID2_Long,Distance\n")

	for i in range(len(results)):
		for j in range(len(results[i])):
			f.write(str(results[i][j]))
			if j != len(results[i]) - 1:
				f.write(",")

		if i != len(results) - 1:
			f.write("\n")

	f.close()
