#!/usr/bin/env python3
import os
import sys
import datetime
import re
import subprocess
import csv

fullFileFunctions = {}
fieldFunctions = {}


def timeFixing(time): #for use in checking for full file overlap
    time = str(time).split(':')
    hour = time[0]
    minutes = time[1]
    if minutes == "15":
        minutes = .25
    elif minutes == "30":
        minutes = .5
    elif minutes == "45":
        minutes = .75
    elif minutes == "00":
        minutes = 0
    time = int(hour) + minutes
    return float(time)

def checkForFileOverlap(fileContents, **kwargs):
    timesInRows = {}
    rowNum = 1
    for row in fileContents:
        row = str(row).split('|')
        timesInRows.setdefault(str(rowNum), []).append([timeFixing(row[2]), timeFixing(row[4])])
        rowNum += 1
    print(timesInRows.values())
    for tester in timesInRows.values():
        for set in timesInRows.values():
            if tester[0] == set[0] and tester[1] == set[1]:
                break
            elif tester[0] < set[1] and tester[1] > set[0]:
                print("There is an overlap in the times: " + str(tester) + " and " + str(set) + " for client: ")
fullFileFunctions["checkForFileOverlap"]=checkForFileOverlap


def checkForBlanks(fileContents, hoursEntryFormat, **kwargs):
    rowNum = 1
    errs = False
    for row in fileContents:
        row = str(row).split('|')
        for entry in range(len(row)):
            if len(row[entry]) == 0:
                errs = True
                print("empty field: " + hoursEntryFormat[entry] + " in row #" + str(rowNum))
                print("Skipping rest of this files checks...")
        rowNum += 1
    if errs is True:
        return "skip"
fieldFunctions["checkForBlanks"]=checkForBlanks

def checkFileDate(fileContents, fileDate, **kwargs):
    rowNum = 1
    errs = False
    for row in fileContents:
        row = str(row).split('|')
        rowDate = row[1].split('-')
        if rowDate[1:] != str(fileDate).split('-')[1:]:
            errs = True
            print(
                "Row #" + str(rowNum) + ", the date in the \"Date In\" field does not match file name, it says: " + str(
                    row[1]))
        elif str(row[3]) != str(fileDate):
            errs = True
            print("Row #" + str(
                rowNum) + ", the date in the \"Date Out\" field does not match file name, it says: " + str(row[3]))
        rowNum += 1
    if errs is True:
        return True
fieldFunctions["checkFileDate"]=checkFileDate

def checkIllegalNums(fileContents, **kwargs):
    rowNum = 1
    errs = False
    for row in fileContents:
        row = str(row).split('|')
        hourIn = str(row[2]).split(':')[0]
        hourOut = str(row[4]).split(':')[0]
        minIn = str(row[2]).split(':')[1]
        minOut = str(row[4]).split(':')[1]
        if float(hourIn) % 1 > 0:
            errs = True
            print("In row #" + str(rowNum) + " the hour in time is a decimal. It reads: " + str(hourIn))
        if float(hourOut) % 1 > 0:
            errs = True
            print(
                "In row #" + str(rowNum) + " the hour out time is a decimal. It reads: " + str(hourOut))
        if float(minIn) % 1 > 0:
            errs = True
            print(
                "In row #" + str(rowNum) + " the minutes in the time in field are a decimal. It reads: " + str(minIn))
        if float(minOut) % 1 > 0:
            errs = True
            print(
                "In row #" + str(rowNum) + " the minutes in the time out field are a decimal. It reads: " + str(minOut))
        if float(hourIn) > 24:
            errs = True
            print(
                "In row #" + str(rowNum) + " the hour in time is greater than 24. It reads: " + str(hourIn))
        elif float(hourIn) < 0:
            errs = True
            print("In row #" + str(rowNum) + " the hour in time is a negative. It reads: " + str(hourIn))
        if float(hourOut) > 24:
            errs = True
            print(
                "In row #" + str(rowNum) + " the hour out time is greater than 24. It reads: " + str(hourOut))
        elif float(hourOut) < 0:
            errs = True
            print(
                "In row #" + str(rowNum) + " the hour out time is a negative. It reads: " + str(hourOut))
        if float(minIn) > 59:
            errs = True
            print(
                "In row #" + str(rowNum) + " the minutes in the time in field are over 59. It reads: " + str(minIn))
        elif float(minIn) < 0:
            errs = True
            print(
                "In row #" + str(rowNum) + " the minutes in the time in field are negative. It reads: " + str(minIn))
        if float(minOut) > 59:
            errs = True
            print(
                "In row #" + str(rowNum) + " the minutes in the time out field are over 59. It reads: " + str(minOut))
        elif float(minOut) < 0:
            errs = True
            print(
                "In row #" + str(rowNum) + " the minutes in the time out field are negative It reads: " + str(minOut))
        rowNum += 1
    if errs is True:
        return True
fieldFunctions["checkIllegalNums"]=checkIllegalNums


def checkIllegalDates(fileContents, fileYear, **kwargs):
    errs = False
    yearToBaseFrom = float(fileYear)
    if str(fileYear).isdecimal() is False:
        errs = True
        print("The year in the file name is not correct. ")
    elif float(fileYear) % 1 > 0:
        errs = True
        print("The year in the file name is a decimal. ")
    else:
        if str(fileYear) != str(datetime.datetime.now().year):
            print(datetime.datetime.now().year)
            userInput = str(input("This file is from a different year than it is currently, it reads: " + str(
                fileYear) + ". Continue? (Y/N) "))
            while userInput != "Y" and userInput != "N":
                userInput = str(input("Enter Y or N "))
            if userInput == "N":
                print("skipping...")
                return
            elif userInput == "Y":
                yearToBaseFrom = float(fileYear)

    rowNum = 1
    for row in fileContents:
        row = str(row).split('|')
        dateIn = str(row[1]).split('-')
        dateOut = str(row[3]).split('-')
        if float(dateIn[0]) != yearToBaseFrom:
            errs = True
            print(
                "In row #" + str(rowNum) + " the year in the \"date in\" field does not match the file name. It reads: " + str(
                    dateIn[0]))
        if float(dateOut[0]) != yearToBaseFrom:
            errs = True
            print(
                "In row #" + str(rowNum) + " the year in the \"date out\" field does not match the file name. It reads: " + str(
                    dateOut[0]))
        if float(dateIn[1]) > 12 or float(dateIn[1]) < 1:
            errs = True
            print(
                "In row #" + str(rowNum) + " the date in month is out of range. It reads: " + str(dateIn[1]))
        if float(dateIn[2]) > 31 or float(dateIn[2]) < 1:
            errs = True
            print(
                "In row #" + str(rowNum) + " the date in day is out of range. It reads: " + str(dateIn[2]))
        if float(dateOut[1]) > 12 or float(dateOut[1]) < 1:
            errs = True
            print(
                "In row #" + str(rowNum) + " the date out month is out of range. It reads: " + str(dateOut[1]))
            errors = 1
        if float(dateOut[2]) > 31 or float(dateOut[2]) < 1:
            errs = True
            print(
                "In row #" + str(rowNum) + " the date out day is out of range. It reads: " + str(dateOut[2]))
        rowNum += 1
    if errs is True:
        return True
fieldFunctions["checkIllegalDates"]=checkIllegalDates


def nameMatchCheck(fileContents, fileUserName, **kwargs):
    rowNum = 1
    errs = False
    for row in fileContents:
        row = str(row).split('|')
        if str(row[0]) != str(fileUserName):
            errs = True
            print(
                "Name field for row #" + str(rowNum) + " does not match file name, it says: " + str(row[0]))
        rowNum += 1
    if errs is True:
        return True
fieldFunctions["nameMatchCheck"]=nameMatchCheck

def checkForOverlapSingleRow(fileContents, **kwargs):
    rowNum = 1
    errs = False
    for row in fileContents:
        row = str(row).split('|')
        timeIn = str(row[2]).split(':')
        timeOut = str(row[4]).split(':')
        hourCheck = float(timeOut[0]) - float(timeIn[0])
        minCheck = float(timeOut[1]) - float(timeIn[1])
        if hourCheck and minCheck < 0 or hourCheck < 0:
            errs = True
            print("in row #" + str(
                rowNum) + " There is an inconsistency with the punch in an out times, it results in a negative.")
        rowNum += 1
    if errs is True:
        return True
fieldFunctions["checkForOverlapSingleRow"]=checkForOverlapSingleRow

def checkHourIncrement(fileContents, **kwargs):
    rowNum = 1
    errs = False
    for row in fileContents:
        row = str(row).split('|')
        try:
            workTime = str(row[5]).split('.')
            if float(workTime[1]) % .25 != 0: # using remainders to check increment
                errs = True
                print(
                    "Row #" + str(rowNum) + ", hours worked time is not in 15 minute increments, it reads: " + str(workTime[0]) + "." + str(
                        workTime[1]))
        except IndexError:
            errs = True
            print("Row #" + str(rowNum) + ", the hours worked time is not formatted correctly, it reads: " + str(row[5]))
        rowNum += 1
    if errs is True:
        return True
fieldFunctions["checkHourIncrement"]=checkHourIncrement

'''
def checkClientName(fileContents, clientList, **kwargs):
    rowNum = 1
    errs = False
    for row in fileContents:
        row = str(row).split('|')
        if not str(row[6]) in clientList:
            errs = True
            print(
                "Row #" + str(rowNum) + ". The client field does not match any current client, it reads: " + str(
                    row[6]))
        rowNum += 1
    if errs is True:
        return True
fieldFunctions["checkClientName"]=checkClientName
'''

"""                 ---- MAIN LOOP ----                         
    the variable "err", when True will leave the script with an exit code of 1 when finished. if it is False it will leave
    with a 0. To utilize this in a function, return a value or True or False depending on the result of the checking function.


"""


for args in sys.argv[1:]:
    err = False
    fileContents = str(subprocess.check_output(["cat", str(args)])).replace('\\n', '\n').strip('\'').strip("b'").strip().split('\n')
    if subprocess.check_call(["test", "-e"]) == 1:
        print("File %s does not exist" % str(args))
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
    hoursEntryFormat = ['Name', 'Date In', 'Time In', "Date Out", "Time out", "Hours Worked", "Client", "Emergency", \
                            'Billable', 'Comment']  # show what field is empty
    #clientList = str(subprocess.check_output(["./projects/clients/bin/projects-show-all"])).split('\n')
    print("\n\033[1;31;41mChecking:\033[0m %s" % str(args))
    for key, func in fieldFunctions.items():
        err = func(fileContents=fileContents, fileDate=fileDate, fileYear=fileYear, fileUserName=fileUserName,
                      hoursEntryFormat=hoursEntryFormat)#, clientList=clientList)
        if err == "skip":
            break
    for key, func in fullFileFunctions.items():
        err = func(fileContents=fileContents, fileDate=fileDate)
    if err is False:
        print("file: %s is all good!" % str(args))

if err is True:
    sys.exit(1)
else:
    sys.exit(0)