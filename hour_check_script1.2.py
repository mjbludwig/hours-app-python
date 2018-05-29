#!/usr/bin/env python3
import os
import sys
import datetime
import re

fullFileFunctions = {}
fieldFunctions = {}

def main(fileName):
    fileContents = os.system('cat s%' % fileName)
    if os.system('test -e; echo $?') == "0":
        print("File s% does not exist" % fileName)

    try:
        actualFileName = fileName.split('/')
        fileFields = str(actualFileName[-1]).split('-')
        fileYear = fileFields[0]
        fileMonth = fileFields[1]
        fileDay = fileFields[2]
        fileDate = '-'.join(fileFields[0:-1])
        fileUserName = fileFields[3]
    except IndexError:
        print("\n\033[1;31;41m" + "This file has an invalid name, skipping...: " + "\033[0m" + " \033[0;30;43m" + str(
            fileName) + "\033[0m\n")




def checkForBlanks(reader):
    global hoursEntryFormat
    global errorMessages
    hoursEntryFormat = ['Name', 'Date In', 'Time In', "Date Out", "Time out", "Hours Worked", "Client", "Emergency", \
                        'Billable', 'Comment']  #show what field is empty
    rowNum = 1
    for row in reader:
        for entry in range(len(row)):
            if len(row[entry]) == 0:
                errorMessages.append("empty field: " + hoursEntryFormat[entry] + " in row #" + str(rowNum))
                global errors
                errors = 1
        rowNum += 1
fieldFunctions["checkForBlanks"]=checkForBlanks


def checkClientName(data, clientList):
    rowNum = 1
    global errorMessages
    global errors
    # print(clientList)
    # print(data)
    for row in data:
        if not str(row[6]) in clientList:
            errorMessages.append(
                "Row #" + str(rowNum) + ". The client field does not match any current client, it reads: " + str(
                    row[6]))
            errors = 1
        rowNum += 1
fieldFunctions["checkClientName"]=checkClientName

def checkHourIncrement(reader):
    rowNum = 1
    global errorMessages
    for row in reader:
        try:
            workTime = str(row[5]).split('.')
            if float(workTime[1]) % .25 != 0: # using remainders to check increment
                errorMessages.append(
                    "Row #" + str(rowNum) + ", hours worked time is not in 15 minute increments, it reads: " + str(workTime[0]) + "." + str(
                        workTime[1]))
                global errors
                errors = 1
        except IndexError:
            errorMessages.append("Row #" + str(rowNum) + ", the hours worked time is not formatted correctly,"
                                                         " it reads: " + str(row[5]))
            errors = 1
        rowNum += 1
fieldFunctions["checkHourIncrement"]=checkHourIncrement


def checkForOverlapSingleRow(reader):
    rowNum = 1
    global errorMessages
    for row in reader:
        timeIn = str(row[2]).split(':')
        timeOut = str(row[4]).split(':')
        hourCheck = float(timeOut[0]) - float(timeIn[0])
        minCheck = float(timeOut[1]) - float(timeIn[1])
        if hourCheck and minCheck < 0 or hourCheck < 0:
            errorMessages.append("in row #" + str(
                rowNum) + " There is an inconsistency with the punch in an out times, it results in a negative.")
            global errors
            errors = 1
        rowNum += 1
fieldFunctions["checkForOverlapSingleRow"]=checkForOverlapSingleRow

def nameMatchCheck(reader):
    global fileUserName
    global errorMessages
    rowNum = 1
    for row in reader:
        if str(row[0]) != str(fileUserName):
            errorMessages.append(
                "Name field for row #" + str(rowNum) + " does not match file name, it says: " + str(row[0]))
            global errors
            errors = 1
        rowNum += 1
fieldFunctions["nameMatchCheck"]=nameMatchCheck

def checkIllegalDates(reader):
    global errors
    global fileDay
    global fileMonth
    global fileYear
    global errorMessages
    yearToBaseFrom = float(fileYear)
    if str(fileYear).isdecimal() is False:
        errorMessages.append("The year in the file name is not correct. ")
        errors = 1
    elif float(fileYear) % 1 > 0:
        errorMessages.append("The year in the file name is a decimal. ")
        errors = 1
    else:
        if str(fileYear) != str(datetime.datetime.now().year):
            print(datetime.datetime.now().year)
            userInput = str(input("This file is from a different year than it is currently, it reads: " + str(
                fileYear) + ". Continue? (Y/N) "))
            while userInput != "Y" and userInput != "N":
                userInput = str(input("Enter Y or N "))
            if userInput == "N":
                print("Quitting...")
                exit()
            elif userInput == "Y":
                yearToBaseFrom = float(fileYear)

    rowNum = 1
    for row in reader:
        dateIn = str(row[1]).split('-')
        dateOut = str(row[3]).split('-')
        if float(dateIn[0]) != yearToBaseFrom:
            errorMessages.append(
                "In row #" + str(rowNum) + " the year in the date in field is not from this year. It reads: " + str(
                    dateIn[0]))
        if float(dateOut[0]) != yearToBaseFrom:
            errorMessages.append(
                "In row #" + str(rowNum) + " the year in the date in field is not from this year. It reads: " + str(
                    dateOut[0]))
        if float(dateIn[1]) > 12 or float(dateIn[1]) < 1:
            errorMessages.append(
                "In row #" + str(rowNum) + " the date in month is out of range. It reads: " + str(dateIn[1]))
            errors = 1
        if float(dateIn[2]) > 31 or float(dateIn[2]) < 1:
            errorMessages.append(
                "In row #" + str(rowNum) + " the date in day is out of range. It reads: " + str(dateIn[2]))
        if float(dateOut[1]) > 12 or float(dateOut[1]) < 1:
            errorMessages.append(
                "In row #" + str(rowNum) + " the date out month is out of range. It reads: " + str(dateOut[1]))
            errors = 1
        if float(dateOut[2]) > 31 or float(dateOut[2]) < 1:
            errorMessages.append(
                "In row #" + str(rowNum) + " the date out day is out of range. It reads: " + str(dateOut[2]))
        rowNum += 1
fieldFunctions["checkIllegalDates"]=checkIllegalDates


def checkIllegalNums(file):
    rowNum = 1
    for row in file:
        hourIn = str(row[2]).split(':')[0]
        hourOut = str(row[4]).split(':')[0]
        minIn = str(row[2]).split(':')[1]
        minOut = str(row[4]).split(':')[1]
        if float(hourIn) % 1 > 0:
            errorMessages.append("In row #" + str(rowNum) + " the hour in time is a decimal. It reads: " + str(hourIn))
            errors = 1
        if float(hourOut) % 1 > 0:
            errorMessages.append(
                "In row #" + str(rowNum) + " the hour out time is a decimal. It reads: " + str(hourOut))
            errors = 1
        if float(minIn) % 1 > 0:
            errorMessages.append(
                "In row #" + str(rowNum) + " the minutes in the time in field are a decimal. It reads: " + str(minIn))
            errors = 1
        if float(minOut) % 1 > 0:
            errorMessages.append(
                "In row #" + str(rowNum) + " the minutes in the time out field are a decimal. It reads: " + str(minOut))
            errors = 1
        if float(hourIn) > 24:
            errorMessages.append(
                "In row #" + str(rowNum) + " the hour in time is greater than 24. It reads: " + str(hourIn))
            errors = 1
        elif float(hourIn) < 0:
            errorMessages.append("In row #" + str(rowNum) + " the hour in time is a negative. It reads: " + str(hourIn))
            errors = 1
        if float(hourOut) > 24:
            errorMessages.append(
                "In row #" + str(rowNum) + " the hour out time is greater than 24. It reads: " + str(hourOut))
            errors = 1
        elif float(hourOut) < 0:
            errorMessages.append(
                "In row #" + str(rowNum) + " the hour out time is a negative. It reads: " + str(hourOut))
            errors = 1
        if float(minIn) > 59:
            errorMessages.append(
                "In row #" + str(rowNum) + " the minutes in the time in field are over 59. It reads: " + str(minIn))
            errors = 1
        elif float(minIn) < 0:
            errorMessages.append(
                "In row #" + str(rowNum) + " the minutes in the time in field are negative. It reads: " + str(minIn))
            errors = 1
        if float(minOut) > 59:
            errorMessages.append(
                "In row #" + str(rowNum) + " the minutes in the time out field are over 59. It reads: " + str(minOut))
            errors = 1
        elif float(minOut) < 0:
            errorMessages.append(
                "In row #" + str(rowNum) + " the minutes in the time out field are negative It reads: " + str(minOut))
        rowNum += 1
fieldFunctions["checkIllegalNums"]=checkIllegalNums


def checkFileDate(fileContents, fileDate):
    rowNum = 1
    for row in fileContents:
        if str(row[1]) != str(fileDate):
            err = True
            print(
                "Row #" + str(rowNum) + ", the date in the \"Date In\" field does not match file name, it says: " + str(
                    row[1]))
        elif str(row[3]) != str(fileDate):
            err = True
            print("Row #" + str(
                rowNum) + ", the date in the \"Date Out\" field does not match file name, it says: " + str(row[3]))
        rowNum += 1
    if err is True:
        return True

fieldFunctions["checkFileDate"]=checkFileDate


for args in sys.argv[1:]:
    err = False
    fileContents = os.system('cat s%' % args)
    if os.system('test -e; echo $?') == "0":
        print("File s% does not exist" % args)
        err = True
        break

    try:
        actualFileName = args.split('/')
        fileFields = str(actualFileName[-1]).split('-')
        fileYear = fileFields[0]
        fileMonth = fileFields[1]
        fileDay = fileFields[2]
        fileDate = '-'.join(fileFields[0:-1])
        fileUserName = fileFields[3]
    except IndexError:
        print("\n\033[1;31;41m" + "This file has an invalid name, skipping...: " + "\033[0m" + " \033[0;30;43m" + str(
            args) + "\033[0m\n")
        err = True
        break
    print("\n\033[1;31;41mChecking:\033[0m %s" % str(args))
    for key, func in fieldFunctions.iteritems():
        result = func(fileContents=fileContents, fileDate=FileDate)
        if result is True:
            err = True

if err is True:
    sys.exit(1)
else:
    sys.exit(0)
