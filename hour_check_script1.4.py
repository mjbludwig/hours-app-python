#!/usr/bin/env python3.1

import csv
import sys
import re
import subprocess
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


def checkIllegalNums(fileRows, **kwargs):
    errs = False
    for index, row in enumerate(fileRows):
        try:
            hourIn = str(row[1]).split(' ')[1].split(':')[0]
            hourOut = str(row[2]).split(' ')[1].split(':')[0]
            minIn = str(row[1]).split(' ')[1].split(':')[1]
            minOut = str(row[2]).split(' ')[1].split(':')[1]
        except IndexError:
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
            rowsToSkip.append(index)
    if errs is True:
        printErrorSeperator()
        return True
    else:
        return False
fieldFunctions["checkIllegalNums"]=checkIllegalNums

def checkFileDate(fileRows, fileDate, rowsToSkip, **kwargs):
    for index, row in enumerate(fileRows):
        if index in rowsToSkip:
            continue
        rowDateIn = str(row[1].split(' ')[0]).split('-')[1:]
        rowDateOut = str(row[2].split(' ')[0]).split('-')[1:]
        fileMonthAndDay = str(fileDate).split('-')[1:]
        if str(rowDateIn[0]) != str(fileMonthAndDay[0]):
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index, highlights=[1]), sep="")
            print(
                "\033[38;5;196m-- The month in the \"Date In\" field does not match file name month, it says:\033[0m " + str(
                    str(rowDateIn[0])))
        elif str(rowDateIn[1]) != str(fileMonthAndDay[1]):
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index, highlights=[1]), sep="")
            print(
                "\033[38;5;196m-- The day in the \"Date In\" field does not match file name day, it says:\033[0m " + str(
                    str(rowDateIn[1])))
        elif str(rowDateOut[0]) != str(fileMonthAndDay[0]):
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index, highlights=[2]), sep="")
            print("\033[38;5;196m-- The month in the \"Date Out\" field does not match file name month, it says:\033[0m " + str(
                rowDateOut[0]))
        elif str(rowDateOut[1]) != str(fileMonthAndDay[1]):
            errs = True
            print("\033[38;5;196mRow #", str(index + 1), ":\033[0m ", printRawLine(index, highlights=[2]), sep="")
            print("\033[38;5;196m-- The day in the \"Date Out\" field does not match file name day, it says:\033[0m " + str(
                rowDateOut[1]))
    if errs is True:
        printErrorSeperator()
        return True
    else:
        return False
fieldFunctions["checkFileDate"]=checkFileDate

################################
## Create the Data Structure ###
################################

for file in sys.argv[1:]:
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
            print("\033[38;5;196m-- Row #%s has an incorrect number of fields: \033[0m" % (index + 1))
            print(printRawLine(index))
            rowsToSkip.append(index)

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
        print(
            "\n\033[38;5;196m" + "-- This file has an illegally formatted name: " + "\033[0m" + " \033[0;30;43m" + str(
                file) + "\033[0m\n")
        # checking file contents against file name cannot be done if the file name has bad formatting

    hoursEntryFormat = ['Name', 'Date In', 'Time In', "Date Out", "Time out", "Hours Worked", "Client", "Emergency", \
                        'Billable', 'Comment']  # show what field is empty
    try:
        clientList = str(subprocess.check_output(["sh", "/projects/clients/bin/projects-show-all"]))[2:].split('\\n')
    except subprocess.CalledProcessError:
        print(
            "\033[38;5;196m-- Could not find \"/projects/clients/bin/projects-show-all\", check location and permissions?\033[0m\n")
        err = True
        break
    fileErrs = []
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





if err is True:
    sys.exit(1)
elif err is False:
    sys.exit(0)