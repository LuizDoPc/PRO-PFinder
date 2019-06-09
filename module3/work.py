import csv

files = ['archaea', 'gramn', 'gramp', 'proteo']

for file in files:

    for i in range(6, 10):
        num = i
        sheet = 'prn'
        prn = ['A', 'B', 'C', 'D']
        sheet += prn[num-6];

        # 6
        with open(file+'.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            f = open(sheet, 'a');
            for row in readCSV:
                if row[num].strip() != 'A':
                    if '/' in row[num]:
                        for c in row[num].split('/'):
                            if c.strip() != '' and len(c) != 4:
                                f.write(c.strip()+'\n')
                    else:
                        f.write(row[num]+'\n')

            f.close()
