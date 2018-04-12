import csv
import sys



def main():

    checkHourIncrement(fileName)
    checkFileYear(fileName)
    checkForBlanks(fileName)
    nameMatchCheck(fileName)
    global errors
    #print(str(errors))
    if errors == 1:
        sys.exit(1)
    elif errors == 0:
        sys.exit(0)


def checkHourIncrement(fileName):
    with open(fileName, 'r') as csvFile:
        reader = csv.reader(csvFile, delimiter='|')
        rowNum = 1
        for row in reader:
            workTime = str(row[5]).split(':')
            #print(workTime[1])
            if int(workTime[1]) % 15 != 0:
                print("Row #" + str(rowNum) + " is not in 15 minute increments, it reads: " + str(workTime[0]) + ":" + str(workTime[1]))
                global errors
                errors = 1
        rowNum += 1



def nameMatchCheck(fileName):
    global fileUserName
    with open(fileName, 'r') as csvFile:
        reader = csv.reader(csvFile, delimiter='|')
        rowNum = 1
        for row in reader:
            if str(row[0]) != str(fileUserName):
                print("Name field for row #" + str(rowNum) + " does not match file name, it says: " + str(row[0]))
                global errors
                errors = 1
            rowNum += 1
    csvFile.close()

def checkForBlanks(fileName):
    global hoursEntryFormat
    with open(fileName, 'r') as csvFile:
        reader = csv.reader(csvFile, delimiter='|')
        rowNum = 1
        for row in reader:
            for entry in range(len(row)):
                #print(row[entry])
                if len(row[entry]) == 0:
                    print("empty field: " + hoursEntryFormat[entry] + " in row #" + str(rowNum))
                    global errors
                    errors = 1
            rowNum += 1
    csvFile.close()

def checkFileYear(fileName):
    with open(fileName, 'r') as csvFile:
        reader = csv.reader(csvFile, delimiter='|')
        rowNum = 1
        for row in reader:
            #print(row[1])
            entry = str(row[1]).split('-')
            #print(entry)
            global fileYear
            if str(entry[0]) != str(fileYear):
                print("Row #" + str(rowNum) + ", the year in the \"Date In\" field does not match file name, it says: " + str(entry[0]))
                global errors
                errors = 1
            rowNum += 1
    csvFile.close()


fileName = str(sys.argv[1])
    #print(fileName)

errors = 0
actualFileName = fileName.split('/')
fileFields = str(actualFileName[-1]).split('-')
fileYear = fileFields[0]
fileMonth = fileFields[1]
fileDay = fileFields[2]
fileUserName = fileFields[3]
hoursEntryFormat = ['Name', 'Date In', 'Time In', "Date Out", "Time out", "Hours Worked", "Position", "Emergency",\
                        'Billable', 'Comment']

main()
