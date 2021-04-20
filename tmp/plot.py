file1 = open('throughput.txt', 'r')
Lines = file1.readlines()

count = 0

lista = []
converted_file = []

for line in Lines:
    lista = line.split()
    converted_file.append(lista)

s1 = []
s2 = []
s3 = []
s4 = []
s5 = []
s6 = []
s7 = []
s8 = []

tmp_value = 0

for time_in_seconds in range(1, len(converted_file)):
    for number_of_switches in range(1, 9):

        if not converted_file[time_in_seconds]:
            pass
        elif converted_file[time_in_seconds][0] == '0{}'.format(number_of_switches) and converted_file[time_in_seconds][1] == '4': 
            tmp_value = float(converted_file[time_in_seconds][2])*0.000007629395
            if number_of_switches == 1:
                s1.append(tmp_value)
            elif number_of_switches == 2:
                s2.append(tmp_value)
            elif number_of_switches == 3:
                s3.append(tmp_value)
            elif number_of_switches == 4:
                s4.append(tmp_value)
            elif number_of_switches == 5:
                s5.append(tmp_value)
            elif number_of_switches == 6:
                s6.append(tmp_value)
            elif number_of_switches == 7:
                s7.append(tmp_value)
            elif number_of_switches == 8:
                s8.append(tmp_value)
  
#vou precisar verificar a porta 3 e a porta 4
print(s1)
print(len(s1))

