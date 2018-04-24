#!/usr/bin/env python3
import csv
import sys
import datetime


def main():
    try:
        csvFile = open(fileName, 'r')
    except FileNotFoundError:
        print("\n*********   The file \"%s\" does not exist.   **********\n" % csvFile)
        return 

    reader = csv.reader(csvFile, delimiter='|')
    data = list(reader)
    global errorMessages
    errorMessages = []
    checkForBlanks(data)
    checkForOverlapSingleRow(data)
    checkHourIncrement(data)
    checkFileDate(data)
    nameMatchCheck(data)
    checkIllegalNums(data)
    checkIllegalDates(data)
    if errors == 1:
        print("\n\033[1;31;41m**** There were errors in file #" + str(fileNumber) + ":\033[0m\n")
        for errs in errorMessages:
            print("       => " + errs)
    csvFile.close()




def checkHourIncrement(reader):
    rowNum = 1
    global errorMessages
    for row in reader:
        workTime = str(row[5]).split(':')
        if int(workTime[1]) % 15 != 0:
            errorMessages.append("Row #" + str(rowNum) + " is not in 15 minute increments, it reads: " + str(workTime[0]) + ":" + str(workTime[1]))
            global errors
            errors = 1
        rowNum += 1

def checkForOverlapSingleRow(reader): ####This function needs to be mathmatically rewritten, it does not accurately reflect overlapped times
    rowNum = 1
    global errorMessages
    for row in reader:
        timeIn = str(row[2]).split(':')
        timeOut = str(row[4]).split(':')
        hourCheck = float(timeOut[0]) - float(timeIn[0])
        minCheck = float(timeOut[1]) - float(timeIn[1])
        #print(hourCheck)
        #print(minCheck)
        if hourCheck and minCheck < 0 or hourCheck < 0:
            errorMessages.append("in entry #" + str(rowNum) + " There is an inconsistency with the punch in an out times, it results in a negative.")
            global errors
            errors = 1
        rowNum += 1

def nameMatchCheck(reader):
    global fileUserName
    global errorMessages
    rowNum = 1
    for row in reader:
        if str(row[0]) != str(fileUserName):
            errorMessages.append("Name field for row #" + str(rowNum) + " does not match file name, it says: " + str(row[0]))
            global errors
            errors = 1
        rowNum += 1

def checkForBlanks(reader):
    global hoursEntryFormat
    global errorMessages
    rowNum = 1
    for row in reader:
        for entry in range(len(row)):
            if len(row[entry]) == 0:
                errorMessages.append("empty field: " + hoursEntryFormat[entry] + " in row #" + str(rowNum))
                global errors
                errors = 1
        rowNum += 1

def checkIllegalDates(reader):
    global errors
    global fileDay
    global fileMonth
    global fileYear
    global errorMessages
    if str(fileYear).isdecimal() is False:
        errorMessages.append("The year in the file name is not correct. ")
        errors = 1
    elif float(fileYear) % 1 > 0:
        errorMessages.append("The year in the file name is a decimal. ")
        errors = 1
    else:
        if str(fileYear) != str(datetime.datetime.now().year):
            print(datetime.datetime.now().year)
            userInput = str(input("This file is from a different year than it is currently, it reads: " + str(fileYear) + ". Continue? (Y/N) "))
            while userInput != "Y" and userInput != "N":
                userInput = str(input("Enter Y or N "))
            if userInput == "N":
                print("Quitting...")
                exit()
            elif userInput == "Y":
                yearToBaseFrom = fileYear

    rowNum = 1
    for row in reader:
        dateIn = str(row[1]).split('-')
        dateOut = str(row[3]).split('-')

        if float(dateIn[1]) > 12 or float(dateIn[1]) < 1:
            errorMessages.append("In row #" + str(rowNum) + "The date in month is out of range. It reads: " + str(dateIn[1]))
            errors = 1
        if float(dateIn[2]) > 31 or float(dateIn[2]) < 1:
            errorMessages.append("In row #" + str(rowNum) + "The date in day is out of range. It reads: " + str(dateIn[2]))
        if float(dateOut[1]) > 12 or float(dateOut[1]) < 1:
            errorMessages.append("In row #" + str(rowNum) + "The date out month is out of range. It reads: " + str(dateOut[1]))
            errors = 1
        if float(dateOut[2]) > 31 or float(dateOut[2]) < 1:
            errorMessages.append("In row #" + str(rowNum) + "The date out day is out of range. It reads: " + str(dateOut[2]))
        rowNum += 1


def checkIllegalNums(reader):
    rowNum = 1
    global errors
    global errorMessages
    for row in reader:
        hourIn = str(row[2]).split(':')[0]
        hourOut = str(row[4]).split(':')[0]
        minIn = str(row[2]).split(':')[1]
        minOut = str(row[4]).split(':')[1]
        if float(hourIn) % 1 > 0:
            errorMessages.append("In row #" + str(rowNum) + " the hour in time is a decimal. It reads: " + str(hourIn))
            errors = 1
        if float(hourOut) % 1 > 0:
            errorMessages.append("In row #" + str(rowNum) + " the hour out time is a decimal. It reads: " + str(hourOut))
            errors = 1
        if float(minIn) % 1 > 0:
            errorMessages.append("In row #" + str(rowNum) + " the minutes in the time in field are a decimal. It reads: " + str(minIn))
            errors = 1
        if float(minOut) % 1 > 0:
            errorMessages.append("In row #" + str(rowNum) + " the minutes in the time out field are a decimal. It reads: " + str(minOut))
            errors = 1
        if float(hourIn) > 24:
            errorMessages.append("In row #" + str(rowNum) + " the hour in time is greater than 24. It reads: " + str(hourIn))
            errors = 1
        elif float(hourIn) < 0:
            errorMessages.append("In row #" + str(rowNum) + " the hour in time is a negative. It reads: " + str(hourIn))
            errors = 1
        if float(hourOut) > 24:
            errorMessages.append("In row #" + str(rowNum) + " the hour out time is greater than 24. It reads: " + str(hourOut))
            errors = 1
        elif float(hourOut) < 0:
            errorMessages.append("In row #" + str(rowNum) + " the hour out time is a negative. It reads: " + str(hourOut))
            errors = 1
        if float(minIn) > 59:
            errorMessages.append("In row #" + str(rowNum) + " the minutes in the time in field are over 59. It reads: " + str(minIn))
            errors = 1
        elif float(minIn) < 0:
            errorMessages.append("In row #" + str(rowNum) + " the minutes in the time in field are negative. It reads: " + str(minIn))
            errors = 1
        if float(minOut) > 59:
            errorMessages.append("In row #" + str(rowNum) + " the minutes in the time out field are over 59. It reads: " + str(minOut))
            errors = 1
        elif float(minOut) < 0:
            errorMessages.append("In row #" + str(rowNum) + " the minutes in the time out field are negative It reads: " + str(minOut))
            errors = 1
        rowNum += 1
        #print(hourIn)
        #print(hourOut)

def checkFileDate(reader):
        rowNum = 1
        global errorMessages
        for row in reader:
            global fileDate
            global errors
            if str(row[1]) != str(fileDate):
                errorMessages.append("Row #" + str(rowNum) + ", the date in the \"Date In\" field does not match file name, it says: " + str(row[1]))
                errors = 1
            elif str(row[3]) != str(fileDate):
                errorMessages.append("Row #" + str(rowNum) + ", the date in the \"Date Out\" field does not match file name, it says: " + str(row[3]))
                errors = 1
            rowNum += 1




'''-----------------INITIALISATION AND RUN MAIN()---------------------'''

fileArgs = sys.argv[1:]
fileNumber = 1
#print(str(fileArgs))
for args in fileArgs:
    fileName = args
    errors = 0
    actualFileName = fileName.split('/')
    fileFields = str(actualFileName[-1]).split('-')
    fileYear = fileFields[0]
    fileMonth = fileFields[1]
    fileDay = fileFields[2]
    fileDate = '-'.join(fileFields[0:-1])
    fileUserName = fileFields[3]
    hoursEntryFormat = ['Name', 'Date In', 'Time In', "Date Out", "Time out", "Hours Worked", "Position", "Emergency", \
                        'Billable', 'Comment']
    main()
    fileNumber += 1
print("")
if errors == 1:
    sys.exit(1)
else:
    sys.exit(0)