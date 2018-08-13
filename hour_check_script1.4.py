#!/usr/bin/env python3.1
import os
import sys
import datetime
import re
import subprocess
import csv

fullFileFunctions = {}
fieldFunctions = {}


def checkFieldNumber(fileContents, **kwargs):  ###!!!!! LET THIS BE THE FIRST FUNCTION !!!!######
    rowNum = 1
    errs = False
    for row in fileContents:
        row = str(row).split('|')
        if len(row) != 8:
            print("\033[38;5;196mRow #" + str(rowNum) + " is not formatted with correct number of fields.\033[0m")
            errs = True
        rowNum += 1
    if errs is True:
        print("\033[38;5;196m-- There are issues with the formatting of fields in this file...skipping the rest of checks for this file.\033[0m")
        return "skip"
    else:
        return False
fullFileFunctions["checkFieldNumber"]=checkFieldNumber

def convertToBaseTen(time): #for use in checking for full file overlap
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
    errs = False
    for row in fileContents:
        splitrows = str(row).split('|')
        timeIn = re.search('..:..', splitrows[1]).group()
        timeOut = re.search('..:..', splitrows[2]).group()
        if timeIn is None:
            print("\033[38;5;196m-- there is an error with the formatting of the punch in time.\033[0m")
            return "skip"
        elif timeOut is None:
            print("\033[38;5;196m-- there is an error with the formatting of the punch out time.\033[0m")
            return "skip"
        timesInRows[rowNum] = ([convertToBaseTen(timeIn), convertToBaseTen(timeOut)])
        rowNum += 1
    for tester in timesInRows.values():
        for set in timesInRows.values():
            if tester[0] == set[0] and tester[1] == set[1]:
                break
            elif tester[0] < set[1] and tester[1] > set[0]:
                testerRow = [key for key, value in timesInRows.items() if value == tester][0]
                setRow = [key for key, value in timesInRows.items() if value == set][0]
                print("\033[38;5;196m-- There is an overlap in the times: \033[0m" + str(tester[0]) + ", " + str(tester[1]) + " (Row #" +
                      str(testerRow) + ") and " + str(set[0]) + ", " + str(set[1]) + " (Row #" + str(setRow) + ")")
                errs = True
    if errs is True:
        return True
    else:
        return False
fullFileFunctions["checkForFileOverlap"]=checkForFileOverlap


def checkForBlanks(fileContents, hoursEntryFormat, **kwargs):
    rowNum = 1
    errs = False
    for row in fileContents:
        row = str(row).split('|')
        for entry in range(len(row)):
            if len(row[entry]) == 0:
                errs = True
                print("\033[38;5;196m-- Empty field: " + hoursEntryFormat[entry] + " in row #" + str(rowNum))
                print("Skipping rest of this files checks...\033[0m")
        rowNum += 1
    if errs is True:
        return "skip"
    else:
        return False
fieldFunctions["checkForBlanks"]=checkForBlanks

def checkFileDate(fileContents, fileDate, **kwargs):
    rowNum = 1
    errs = False
    for row in fileContents:
        row = str(row).split('|')
        rowDateIn = str(row[1].split(' ')[0]).split('-')[1:]
        rowDateOut = str(row[2].split(' ')[0]).split('-')[1:]
        fileMonthAndDay = str(fileDate).split('-')[1:]
        if str(rowDateIn[0]) != str(fileMonthAndDay[0]):
            errs = True
            print(
                "\033[38;5;196m-- Row #" + str(rowNum) + ", the month in the \"Date In\" field does not match file name month, it says:\033[0m " + str(
                    str(rowDateIn[0])))
        elif str(rowDateIn[1]) != str(fileMonthAndDay[1]):
            errs = True
            print(
                "\033[38;5;196m-- Row #" + str(rowNum) + ", the day in the \"Date In\" field does not match file name day, it says:\033[0m " + str(
                    str(rowDateIn[1])))
        elif str(rowDateOut[0]) != str(fileMonthAndDay[0]):
            errs = True
            print("\033[38;5;196m-- Row #" + str(
                rowNum) + ", the month in the \"Date Out\" field does not match file name month, it says:\033[0m " + str(rowDateOut[0]))
        elif str(rowDateOut[1]) != str(fileMonthAndDay[1]):
            errs = True
            print("\033[38;5;196m-- Row #" + str(
                rowNum) + ", the day in the \"Date Out\" field does not match file name day, it says:\033[0m " + str(rowDateOut[1]))
        rowNum += 1
    if errs is True:
        return True
    else:
        return False
fieldFunctions["checkFileDate"]=checkFileDate

def checkIllegalNums(fileContents, **kwargs):
    rowNum = 1
    errs = False
    for row in fileContents:
        row = str(row).split('|')
        hourIn = str(row[1]).split(' ')[1].split(':')[0]
        hourOut = str(row[2]).split(' ')[1].split(':')[0]
        minIn = str(row[1]).split(' ')[1].split(':')[1]
        minOut = str(row[2]).split(' ')[1].split(':')[1]
        if float(hourIn) % 1 > 0:
            errs = True
            print("\033[38;5;196m-- In row #" + str(rowNum) + " the hour in time is a decimal. It reads:\033[0m " + str(hourIn))
        if float(hourOut) % 1 > 0:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the hour out time is a decimal. It reads:\033[0m " + str(hourOut))
        if float(minIn) % 1 > 0:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the minutes in the time in field are a decimal. It reads:\033[0m " + str(minIn))
        if float(minOut) % 1 > 0:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the minutes in the time out field are a decimal. It reads:\033[0m " + str(minOut))
        if float(hourIn) > 24:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the hour in time is greater than 24. It reads:\033[0m " + str(hourIn))
        elif float(hourIn) < 0:
            errs = True
            print("\033[38;5;196m-- In row #" + str(rowNum) + " the hour in time is a negative. It reads:\033[0m " + str(hourIn))
        if float(hourOut) > 24:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the hour out time is greater than 24. It reads:\033[0m " + str(hourOut))
        elif float(hourOut) < 0:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the hour out time is a negative. It reads:\033[0m " + str(hourOut))
        if float(minIn) > 59:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the minutes in the time in field are over 59. It reads:\033[0m " + str(minIn))
        elif float(minIn) < 0:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the minutes in the time in field are negative. It reads:\033[0m " + str(minIn))
        if float(minOut) > 59:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the minutes in the time out field are over 59. It reads:\033[0m " + str(minOut))
        elif float(minOut) < 0:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the minutes in the time out field are negative It reads:\033[0m " + str(minOut))
        rowNum += 1
    if errs is True:
        return True
    else:
        return False
fieldFunctions["checkIllegalNums"]=checkIllegalNums


def checkIllegalDates(fileContents, fileYear, **kwargs):
    errs = False
    yearToBaseFrom = float(fileYear)
    if str(fileYear).isdecimal() is False:
        errs = True
        print("\033[38;5;196m-- The year in the file name is not correct. \033[0m")
    elif float(fileYear) % 1 > 0:
        errs = True
        print("\033[38;5;196m-- The year in the file name is a decimal. \033[0m")
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
        dateIn = str(str(row[1]).split(' ')[0]).split('-')
        dateOut = str(str(row[2]).split(' ')[0]).split('-')
        if float(dateIn[0]) != yearToBaseFrom:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the year in the \"date in\" field does not match the file name. It reads:\033[0m " + str(
                    dateIn[0]))
        if float(dateOut[0]) != yearToBaseFrom:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the year in the \"date out\" field does not match the file name. It reads:\033[0m " + str(
                    dateOut[0]))
        if float(dateIn[1]) > 12 or float(dateIn[1]) < 1:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the date in month is out of range. It reads:\033[0m " + str(dateIn[1]))
        if float(dateIn[2]) > 31 or float(dateIn[2]) < 1:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the date in day is out of range. It reads:\033[0m " + str(dateIn[2]))
        if float(dateOut[1]) > 12 or float(dateOut[1]) < 1:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the date out month is out of range. It reads:\033[0m " + str(dateOut[1]))
            errors = 1
        if float(dateOut[2]) > 31 or float(dateOut[2]) < 1:
            errs = True
            print(
                "\033[38;5;196m-- In row #" + str(rowNum) + " the date out day is out of range. It reads:\033[0m " + str(dateOut[2]))
        rowNum += 1
    if errs is True:
        return True
    else:
        return False
fieldFunctions["checkIllegalDates"]=checkIllegalDates


def nameMatchCheck(fileContents, fileUserName, **kwargs):
    rowNum = 1
    errs = False
    for row in fileContents:
        row = str(row).split('|')
        if str(row[0]) != str(fileUserName):
            errs = True
            print(
                "\033[38;5;196m-- Name field for row #" + str(rowNum) + " does not match file name, it says:\033[0m " + str(row[0]))
        rowNum += 1
    if errs is True:
        return True
    else:
        return False
fieldFunctions["nameMatchCheck"]=nameMatchCheck

def checkForOverlapSingleRow(fileContents, **kwargs):
    rowNum = 1
    errs = False
    for row in fileContents:
        row = str(row).split('|')
        timeIn = str(row[1]).split(' ')[1].split(':')
        timeOut = str(row[2]).split(' ')[1].split(':')
        hourCheck = float(timeOut[0]) - float(timeIn[0])
        minCheck = float(timeOut[1]) - float(timeIn[1])

        if hourCheck < 0 and minCheck < 0 or hourCheck < 0:
            errs = True
            print("\033[38;5;196m-- In row #" + str(
                rowNum) + " There is an inconsistency with the punch in an out times, it results in a negative.\033[0m")
        rowNum += 1
    if errs is True:
        return True
    else:
        return False
fieldFunctions["checkForOverlapSingleRow"]=checkForOverlapSingleRow

def checkHourIncrement(fileContents, **kwargs):
    rowNum = 1
    errs = False
    for row in fileContents:
        row = str(row).split('|')
        if len(str(row[3]).split('.')) == 1:
            row[3] = row[3] + ".0"
        try:
            workTime = str(row[3]).split('.')
            if float(workTime[1]) % .25 != 0: # using remainders to check increment
                errs = True
                print(
                    "\033[38;5;196m-- Row #" + str(rowNum) + ", hours worked time is not in 15 minute increments, it reads:\033[0m " + str(workTime[0]) + "." + str(
                        workTime[1]))
        except IndexError:
            errs = True
            print("\033[38;5;196m-- Row #" + str(rowNum) + ", the hours worked time is not formatted correctly, it reads:\033[0m " + str(row[3]))
        rowNum += 1
    if errs is True:
        return True
    else:
        return False

fieldFunctions["checkHourIncrement"]=checkHourIncrement


def checkClientName(fileContents, clientList, **kwargs):
    rowNum = 1
    errs = False
    for row in fileContents:
        row = str(row).split('|')
        if not str(row[4]) in clientList:
            errs = True
            print(
                "\033[38;5;196m-- Row #" + str(rowNum) + ". The client field does not match any current client, it reads:\033[0m " + str(
                    row[4]))
        rowNum += 1
    if errs is True:
        return True
    else:
        return False
fieldFunctions["checkClientName"]=checkClientName


"""                 ---- MAIN LOOP ----                         
    the variable "err", when True will leave the script with an exit code of 1 when finished. if it is False it will leave
    with a 0. To utilize this in a function, return a value or True or False depending on the result of the checking function.


"""

err = False
for args in sys.argv[1:]:
    print("\n\033[38;5;226mChecking:\033[0m %s\n" % str(args))
    try:
        fileContents = []
        with open(args, newline='') as f:
            reader = csv.reader(f, quoting=csv.QUOTE_NONE)
            for row in reader:
                fileContents = fileContents + row
        if all((line.isspace() for line in fileContents)):
            print("\033[38;5;226mfile is empty\033[0m\n\n")
            continue
        #filter(None, fileContents)
        for row in fileContents[:]:
            #print(bool(re.match('^\s+$', row)))
            if bool(re.match('^\s+$', str(row))) is True:
                fileContents.remove(row)
        print(fileContents)
        #fileContents = str(subprocess.check_output(["cat", str(args)], stderr=subprocess.DEVNULL)).replace('\\n', '\n').strip('\'').strip("b'").strip().split('\n')
        #print(fileContents)
    except FileNotFoundError:
        print("\033[38;5;196m-- File: %s does not exist\033[0m\n" % str(args))
        err = True
        continue

    try:
        actualFileName = args.split('/')
        fileFields = str(actualFileName[-1]).split('-')
        fileYear = fileFields[0]
        fileMonth = fileFields[1]
        fileDay = fileFields[2]
        fileDate = '-'.join(fileFields[0:-1])
        fileUserName = fileFields[3]

    except IndexError:
        print("\n\033[38;5;196m" + "-- This file has an invalid name, skipping...: " + "\033[0m" + " \033[0;30;43m" + str(
            args) + "\033[0m\n")
        err = True
        continue
    hoursEntryFormat = ['Name', 'Date In', 'Time In', "Date Out", "Time out", "Hours Worked", "Client", "Emergency", \
                            'Billable', 'Comment']  # show what field is empty
    try:
        clientList = str(subprocess.check_output(["sh", "/projects/clients/bin/projects-show-all"]))[2:].split('\\n')
    except subprocess.CalledProcessError:
        print("\033[38;5;196m-- Could not find \"/projects/clients/bin/projects-show-all\", check location and permissions?\033[0m\n")
        err = True
        break
    fileErrs = []
    for key, func in fullFileFunctions.items():
        err = func(fileContents=fileContents, fileDate=fileDate)
        if err == "skip":
            break
        else:
            fileErrs.append(err)
    if err != "skip":
        for key, func in fieldFunctions.items():
            err = func(fileContents=fileContents, fileDate=fileDate, fileYear=fileYear, fileUserName=fileUserName,
                          hoursEntryFormat=hoursEntryFormat, clientList=clientList)
            if err == "skip":
                break
            else:
                fileErrs.append(err)
    if True in fileErrs:
        err = True
    if err is False:
        print("\033[38;5;82m++ File is all set!\033[0m\n")
if err is True:
    print("\n")
    sys.exit(1)
else:
    print("\n")
    sys.exit(0)
