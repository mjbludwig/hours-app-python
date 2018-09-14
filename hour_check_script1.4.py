#!/usr/bin/env python3.1
import csv
import sys
import re
import subprocess
import datetime
##################################
## dictionaries where functions can be added
#  into the checking loop before file is checked
##################################
fullFileFunctions = {}
fieldFunctions = {}

def printRawLine(row, highlights=None): #concatinates back a row for printing
    if highlights is not None: # if you would like to highlight an entry in a row, pass in the index of the desired
        # highlights as a list. i.e printRawLine(row, highlights=[1,3])
        printFileRow = []
        for index, entry in enumerate(fileRows[row]):
            if index in highlights:
                printFileRow.append(("\033[1;37;41m" + str(entry) + "\033[0m"))
            else:
                printFileRow.append(str(entry))
        return str('|'.join(printFileRow))
    return str('|'.join(fileRows[int(row)]))

def printErrorSeperator():
    print("\033[38;5;33m=======================\033[0m")

def convertToBaseTen(time): #for use in doing math regarding punch in or out times
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

def nameMatchCheck(fileRows, fileUserName, **kwargs):
    errs = False
    for index, row in enumerate(fileRows):
        if str(row[0]) != str(fileUserName):
            errs = True
            print(printRawLine(index, highlights=[0]))# highlight name field
            print(
                "\033[38;5;196m-- Name field for row #" + str(index + 1) + " does not match file name, it says:\033[0m "
                + str(row[0]), "\033[38;5;196mnot\033[0m", str(fileUserName))
    if errs is True:
        printErrorSeperator()
        return True
    else:
        return False
fieldFunctions["nameMatchCheck"]=nameMatchCheck # adds function to field checking dictionary

def checkClientName(fileRows, clientList, **kwargs):
    errs = False
    for index, row in enumerate(fileRows):
        if not str(row[4]) in clientList:
            errs = True
            print(printRawLine(index, highlights=[4]))
            print(
                "\033[38;5;196m-- Row #" + str(index + 1) + ". The client field does not match any current client, it reads:\033[0m " + str(
                    row[4]))
    if errs is True:
        printErrorSeperator()
        return True
    else:
        return False
fieldFunctions["checkClientName"]=checkClientName

def checkIllegalDates(fileRows, fileYear, **kwargs):
    if "checkIllegalDates" in checksToSkip:
        return True
    skipYearCheck = False
    errs = False
    yearToBaseFrom = float(fileYear)
    if str(fileYear).isdecimal() is False:
        errs = True
        skipYearCheck = True
        print(actualFileName)
        print("\033[38;5;196m-- The year in the file name is not correct. \033[0m")
    elif float(fileYear) % 1 > 0:
        errs = True
        skipYearCheck = True
        print(actualFileName)
        print("\033[38;5;196m-- The year in the file name is a decimal. \033[0m")
    else:
        if str(fileYear) != str(datetime.datetime.now().year): # allows script to check hour files from previous years
            print(datetime.datetime.now().year)
            userInput = str(input("This file is from a different year than it is currently, it reads: " + str(
                fileYear) + ". Continue? (Y/N) "))
            while userInput != "Y" and userInput != "N":
                userInput = str(input("Enter Y or N "))
            if userInput == "N":
                print("skipping...")
                return False
            elif userInput == "Y":
                yearToBaseFrom = float(fileYear)

    for index, row in enumerate(fileRows):
        dateIn = str(str(row[1]).split(' ')[0]).split('-')
        dateOut = str(str(row[2]).split(' ')[0]).split('-')
        fileMonthAndDay = str(fileDate).split('-')[1:]
        if float(dateIn[1]) > 12 or float(dateIn[1]) < 1:
            errs = True
            print(printRawLine(index, highlights=[1]))
            print(
                "\033[38;5;196m-- In row #" + str(index + 1) + " the \"Date In\" month is out of range. It reads:\033[0m " + str(dateIn[1]))
        if float(dateIn[2]) > 31 or float(dateIn[2]) < 1:
            errs = True
            print(printRawLine(index, highlights=[1]))
            print(
                "\033[38;5;196m-- In row #" + str(index + 1) + " the \"Date In\" day is out of range. It reads:\033[0m " + str(dateIn[2]))
        if float(dateOut[1]) > 12 or float(dateOut[1]) < 1:
            errs = True
            print(printRawLine(index, highlights=[2]))
            print(
                "\033[38;5;196m-- In row #" + str(index + 1) + " the \"Date Out\" month is out of range. It reads:\033[0m " + str(dateOut[1]))
        if float(dateOut[2]) > 31 or float(dateOut[2]) < 1:
            errs = True
            print(printRawLine(index, highlights=[2]))
            print(
                "\033[38;5;196m-- In row #" + str(index + 1) + " the \"Date Out\" day is out of range. It reads:\033[0m " + str(dateOut[2]))
        if errs is False: # if there are errors in the formatting of the dates, it skips checking if it matches the file name
            if float(dateIn[0]) != yearToBaseFrom and skipYearCheck is True:
                errs = True
                print(printRawLine(index, highlights=[1]))
                print(
                    "\033[38;5;196m-- In row #" + str(index + 1) + " the year in the \"Date In\" field does not match the file name. It reads:\033[0m " + str(
                        dateIn[0]))
            if float(dateOut[0]) != yearToBaseFrom and skipYearCheck is True:
                errs = True
                print(printRawLine(index, highlights=[2]))
                print(
                    "\033[38;5;196m-- In row #" + str(index + 1) + " the year in the \"Date Out\" field does not match the file name. It reads:\033[0m " + str(
                        dateOut[0]))
            if str(dateIn[1]) != str(fileMonthAndDay[0]):
                errs = True
                print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index, highlights=[1]), sep="")
                print(
                    "\033[38;5;196m-- The month in the \"Date In\" field does not match file name month, it says:\033[0m " + str(
                        str(dateIn[1])))
            if str(dateIn[2]) != str(fileMonthAndDay[1]):
                errs = True
                print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index, highlights=[1]), sep="")
                print(
                    "\033[38;5;196m-- The day in the \"Date In\" field does not match file name day, it says:\033[0m " +
                    str(dateIn[2]))
            if str(dateOut[1]) != str(fileMonthAndDay[0]):
                errs = True
                print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index, highlights=[2]), sep="")
                print(
                    "\033[38;5;196m-- The month in the \"Date Out\" field does not match file name month, it says:\033[0m " + str(
                        dateOut[1]))
            if str(dateOut[2]) != str(fileMonthAndDay[1]):
                errs = True
                print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index, highlights=[2]), sep="")
                print(
                    "\033[38;5;196m-- The day in the \"Date Out\" field does not match file name day, it says:\033[0m " + str(
                        dateOut[2]))

    if errs is True:
        printErrorSeperator()
        return True
    else:
        return False
fieldFunctions["checkIllegalDates"]=checkIllegalDates

def checkIllegalNums(fileRows, **kwargs):
    errs = False
    for index, row in enumerate(fileRows):
        try:
            hourIn = str(row[1]).split(' ')[1].split(':')[0]
            hourOut = str(row[2]).split(' ')[1].split(':')[0]
            minIn = str(row[1]).split(' ')[1].split(':')[1]
            minOut = str(row[2]).split(' ')[1].split(':')[1]
        except IndexError: # if the formatting of the punch times in a line is messed up, it cant be checked against the others so
            # this error is given and the line is not processed
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index, highlights=[1, 2]), sep="")
            print("\033[38;5;196m-- The formatting in one or more of the punch times is illegal\033[0m ")
            printErrorSeperator()
            continue
        if float(hourIn) % 1 > 0:
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index), sep="")
            print("\033[38;5;196m-- The hour in time is a decimal. It reads:\033[0m " + str(hourIn))
        if float(hourOut) % 1 > 0:
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index), sep="")
            print(
                "\033[38;5;196m-- The hour out time is a decimal. It reads:\033[0m " + str(hourOut))
        if float(minIn) % 1 > 0:
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index), sep="")
            print(
                "\033[38;5;196m-- The minutes in the time in field are a decimal. It reads:\033[0m " + str(minIn))
        if float(minOut) % 1 > 0:
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index), sep="")
            print(
                "\033[38;5;196m-- The minutes in the time out field are a decimal. It reads:\033[0m " + str(minOut))
        if float(hourIn) > 24:
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index), sep="")
            print(
                "\033[38;5;196m-- The hour in time is greater than 24. It reads:\033[0m " + str(hourIn))
        elif float(hourIn) < 0:
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index), sep="")
            print("\033[38;5;196m-- The hour in time is a negative. It reads:\033[0m " + str(hourIn))
        if float(hourOut) > 24:
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index), sep="")
            print(
                "\033[38;5;196m-- The hour out time is greater than 24. It reads:\033[0m " + str(hourOut))
        elif float(hourOut) < 0:
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index), sep="")
            print(
                "\033[38;5;196m-- The hour out time is a negative. It reads:\033[0m " + str(hourOut))
        if float(minIn) > 59:
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index), sep="")
            print(
                "\033[38;5;196m-- The minutes in the time in field are over 59. It reads:\033[0m " + str(minIn))
        elif float(minIn) < 0:
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index), sep="")
            print(
                "\033[38;5;196m-- The minutes in the time in field are negative. It reads:\033[0m " + str(minIn))
        if float(minOut) > 59:
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index), sep="")
            print(
                "\033[38;5;196m-- The minutes in the time out field are over 59. It reads:\033[0m " + str(minOut))
        elif float(minOut) < 0:
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index), sep="")
            print(
                "\033[38;5;196m-- The minutes in the time out field are negative It reads:\033[0m " + str(minOut))
        if errs is True:
            rowsToSkip.append(index) # if any of these checks report problems then this row cannot be checked by other
            # other functions that rely on accurate parsing.
    if errs is True:
        printErrorSeperator()
        return True
    else:
        return False
fieldFunctions["checkIllegalNums"]=checkIllegalNums

def checkHourIncrement(fileRows, **kwargs):
    errs = False
    for index, row in enumerate(fileRows):
        if len(str(row[3]).split('.')) == 1:
            row[3] = row[3] + ".0"
        try:
            workTime = str(row[3]).split('.')
            if float(workTime[1]) % .25 != 0: # using remainders to check increment
                errs = True
                print(printRawLine(index, highlights=[3]))
                print(
                    "\033[38;5;196m-- Row #" + str(index + 1) + ", hours worked time is not in 15 minute increments, it reads:\033[0m " + str(workTime[0]) + "." + str(
                        workTime[1]))
        except IndexError:
            errs = True
            print(printRawLine(index, highlights=[3]))
            print("\033[38;5;196m-- Row #" + str(index + 1) + ", the hours worked time is not formatted correctly, it reads:\033[0m " + str(row[3]))
    if errs is True:
        checksToSkip.append("checkWorkTime") # cant properly check work time if they are formatted incorrectly
        printErrorSeperator()
        return True
    else:
        return False

fieldFunctions["checkHourIncrement"]=checkHourIncrement

def checkForOverlapSingleRow(fileRows, **kwargs): # making sure the punch out time is not before the punch in time
    errs = False
    for index, row in enumerate(fileRows):
        timeIn = str(row[1]).split(' ')[1].split(':')
        timeOut = str(row[2]).split(' ')[1].split(':')
        hourCheck = float(timeOut[0]) - float(timeIn[0])
        minCheck = float(timeOut[1]) - float(timeIn[1])
        if hourCheck < 0 and minCheck < 0 or hourCheck < 0:
            errs = True
            print(printRawLine(index, highlights=[1, 2]))
            print("\033[38;5;196m-- In row #" + str(
                index + 1) + " There is an inconsistency with the punch in an out times, it results in a negative.\033[0m")
    if errs is True:
        printErrorSeperator()
        return True
    else:
        return False
fieldFunctions["checkForOverlapSingleRow"]=checkForOverlapSingleRow

def checkForFileOverlap(fileRows, **kwargs):
    reducedList = []
    duplicateList = []
    errs = False
    for index, row in enumerate(fileRows):
        timeIn = re.search('..:..', row[1]).group()
        timeOut = re.search('..:..', row[2]).group()
        timeWorked = float(row[3])
        if timeWorked <= 0:
            continue
        if timeIn is None:
            print(printRawLine(index, highlights=[1]))
            print("\033[38;5;196m-- There is an error with the formatting of the punch in time.\033[0m")
            errs = True
            continue
        elif timeOut is None:
            print(printRawLine(index, highlights=[2]))
            print("\033[38;5;196m-- There is an error with the formatting of the punch out time.\033[0m")
            errs = True
            continue
        timeInBase10 = convertToBaseTen(timeIn)
        timeOutBase10 = convertToBaseTen(timeOut)
        reducedList.append(((index), timeInBase10, timeOutBase10, timeWorked)) #narrows the csv file to just the important parts for this check
        if (timeInBase10, timeOutBase10) not in duplicateList:
            duplicateList.append((timeInBase10, timeOutBase10)) # Create list for just what time spans were found more than once

    for set in duplicateList: # now go through the list of known duplicate timespans to find out which lines
        # are duplicate and check to make sure the durations sum to the time span.
        timeSpan = set[1] - set[0]
        errorRows = []
        duration = 0
        for index, row in enumerate(reducedList):
            if set[0] in row and set[1] in row:
                duration = duration + row[3]
                errorRows.append(index)
        if duration != timeSpan:
            for row in errorRows:
                print(printRawLine(row, highlights=[1, 2, 3]))
            print("\033[38;5;196m-- The sum of the durations for the worktime in this/these lines,\n does not match the total timespan.", \
                  "\nThe time span is \033[0m%s" % str(timeSpan), "\033[38;5;196mbut the durations sum to \033[0m%s\n" % str(duration))
            errs = True

    if errs is True:
        printErrorSeperator()
        return True
    else:
        return False
fullFileFunctions["checkForFileOverlap"]=checkForFileOverlap

################################
## Create the Data Structure ###
################################
for file in sys.argv[1:]:
    fileErrs = [] # Stores errors as True values, can be counted later
    ## if there are serious issues with the contents of a file, the err value will flip to
    # True and this script will ultimately return a exit with a 1
    err = False
    # if some of the early file checks fail, certain functions will have to be skipped
    # because they will not have proper variables to check against
    checksToSkip = []
    # if rows have major issues and need to be skipped they will be added here:
    rowsToSkip = []

    try:
        with open(file) as f:
            reader = csv.reader(f, delimiter='|')
            tempFileRows = [r for r in reader]
    except FileNotFoundError:
        print("\033[38;5;196m-- File: %s does not exist\033[0m\n" % str(file))
        err = True
        continue
    for rows in tempFileRows:
        for index, entries in enumerate(rows):
            # Removes any blank space, tab, newline or return character
            if bool(re.match('^\s+$', str(entries))) is True:
                del rows[index]
    # Remove any None lists in the main list
    fileRows = [x for x in tempFileRows if x]

    #remove any empty fields
    for index, rows in enumerate(fileRows):
        fileRows[index] = [x for x in rows if x != '']

    # note if any fields have illegal number of fields that are populated
    for index, rows in enumerate(fileRows):
        if len(rows) != 8:
            print("\033[38;5;196m-- Row #%s has an incorrect number of fields: \033[0m" % (index + 1), str(printRawLine(index)))
            print("\033[38;5;196mCannot continue checks for this row\033[0m")
            fileRows.pop(index)
            printErrorSeperator()
            fileErrs.append(True)

    ## Create variables from file name for use in some checking functions
    try:
        actualFileName = file.split('/')
        fileFields = str(actualFileName[-1]).split('-')
        fileYear = fileFields[0]
        fileMonth = fileFields[1]
        fileDay = fileFields[2]
        fileDate = '-'.join(fileFields[0:-1])
        fileUserName = fileFields[3]
    except IndexError:
        print(actualFileName)
        print(
            "\n\033[38;5;196m" + "-- This file has an illegally formatted name: " + "\033[0m" + " \033[0;30;43m" + str(
                file) + "\033[0m\n")
        fileErrs.append(True)
        # checking file contents against file name cannot be done if the file name has bad formatting
        checksToSkip.append("checkIllegalDates")

    hoursEntryFormat = ['Name', 'Date In Time In', "Date Out Time out", "Hours Worked", "Client", "Emergency", \
                        'Billable', 'Comment']  # show what field is empty
    try:
        clientList = str(subprocess.check_output(["sh", "/projects/clients/bin/projects-show-all"]))[2:].split('\\n')
    except subprocess.CalledProcessError:
        print(
            "\033[38;5;196m-- Could not find \"/projects/clients/bin/projects-show-all\", check location and permissions?\033[0m\n")
        err = True
        break
    for key, func in fullFileFunctions.items():
        err = func(fileRows=fileRows)
        if err is True:
            fileErrs.append(err)
    for key, func in fieldFunctions.items():
        err = func(fileRows=fileRows, fileDate=fileDate, checksToSkip=checksToSkip, rowsToSkip=rowsToSkip, fileYear=fileYear, fileUserName=fileUserName,
                   hoursEntryFormat=hoursEntryFormat, clientList=clientList)
        if err is True:
            fileErrs.append(err)
    if True in fileErrs:
        err = True
        ##### prints seperator line between files if multiple files have errors
        print("\n\033[7;49;91m--------  End of Error Report for %s  ----------\033[0m\n" % str(file))

if err is True:
    sys.exit(1)
elif err is False:
    sys.exit(0)