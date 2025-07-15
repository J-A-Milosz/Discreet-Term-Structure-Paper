def csv_mod(daily_data, monthly_data):
    fixed_and_zero_rate_bonds = {}
    with open(monthly_data, 'r') as f:
        for line in f:
            l = line.split(';')
            fixed_and_zero_rate_bonds[l[0]] = l[8]
    with open(daily_data, 'r') as f, open('result_table.txt', 'w') as w:
        for line in f:
            l = line.split(';')
            if l[7] in fixed_and_zero_rate_bonds.keys():
                for i in range(len(l)):
                    w.write(l[i])
                    w.write(';')
                w.write(l[23])





if __name__ == '__main__':
    csv_mod('notwania_dzienne.csv', 'statystyki_miesieczne.txt')