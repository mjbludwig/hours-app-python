import csv
import sys



def main():



    checkForBlanks(fileName)
    global errors
    #print(str(errors))
    if errors == 1:
        sys.exit(1)



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

fileName = str(sys.argv[1])
    #print(fileName)

errors = 0
fileFields = fileName.split('-')
fileYear = fileFields[0]
fileMonth = fileFields[1]
fileDay = fileFields[2]
fileUserName = fileFields[3]
hoursEntryFormat = ['Name', 'Date In', 'Time In', "Date Out", "Time out", "Hours Worked", "Position", "Emergency",\
                        'Billable', 'Comment']

main()
