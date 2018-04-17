import csv
import sys



def main():
    csvFile = open(fileName, 'r')
    reader = csv.reader(csvFile, delimiter='|')
    data = list(reader)
    checkForBlanks(data)
    checkForOverlapSingleRow(data)
    checkHourIncrement(data)
    checkFileDate(data)
    nameMatchCheck(data)
    checkIllegalNums(data)
    global errors
    if errors == 1:
        sys.exit(1)
    elif errors == 0:
        sys.exit(0)
    csvFile.close()




def checkHourIncrement(reader):
    rowNum = 1
    for row in reader:
        workTime = str(row[5]).split(':')
        if int(workTime[1]) % 15 != 0:
            print("Row #" + str(rowNum) + " is not in 15 minute increments, it reads: " + str(workTime[0]) + ":" + str(workTime[1]))
            global errors
            errors = 1
    rowNum += 1


def checkForOverlapSingleRow(reader): ####This function needs to be mathmatically rewritten, it does not accurately reflect overlapped times
    rowNum = 1
    for row in reader:
        timeIn = str(row[2]).split(':')
        timeOut = str(row[4]).split(':')
        hourCheck = int(timeOut[0]) - int(timeIn[0])
        minCheck = int(timeOut[1]) - int(timeIn[1])
        #print(hourCheck)
        #print(minCheck)
        if hourCheck and minCheck < 0 or hourCheck < 0:
            print("in entry #" + str(rowNum) + " There is an inconsistency with the punch in an out times, it results in a negative.")
            global errors
            errors = 1
        rowNum += 1


def nameMatchCheck(reader):
    global fileUserName
    rowNum = 1
    for row in reader:
        if str(row[0]) != str(fileUserName):
            print("Name field for row #" + str(rowNum) + " does not match file name, it says: " + str(row[0]))
            global errors
            errors = 1
        rowNum += 1

def checkForBlanks(reader):
    global hoursEntryFormat
    rowNum = 1
    for row in reader:
        for entry in range(len(row)):
            if len(row[entry]) == 0:
                print("empty field: " + hoursEntryFormat[entry] + " in row #" + str(rowNum))
                global errors
                errors = 1
        rowNum += 1

def checkIllegalNums(reader):
    rowNum = 1
    for row in reader:
        hourIn = str(row[2]).split(':')[0]
        hourOut = str(row[4]).split(':')[0]
        print(hourIn)
        print(hourOut)

def checkFileDate(reader):
        rowNum = 1
        for row in reader:
            global fileDate
            global errors
            if str(row[1]) != str(fileDate):
                print("Row #" + str(rowNum) + ", the date in the \"Date In\" field does not match file name, it says: " + str(row[1]))
                errors = 1
            elif str(row[3]) != str(fileDate):
                print("Row #" + str(rowNum) + ", the date in the \"Date Out\" field does not match file name, it says: " + str(row[3]))
                errors = 1
            rowNum += 1


fileName = str(sys.argv[1])

errors = 0
actualFileName = fileName.split('/')
fileFields = str(actualFileName[-1]).split('-')
fileYear = fileFields[0]
fileMonth = fileFields[1]
fileDay = fileFields[2]
fileDate = '-'.join(fileFields[0:-1])
fileUserName = fileFields[3]
hoursEntryFormat = ['Name', 'Date In', 'Time In', "Date Out", "Time out", "Hours Worked", "Position", "Emergency",\
                        'Billable', 'Comment']

main()