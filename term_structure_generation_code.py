from mpmath import mp, mpf
from matplotlib.pyplot import plot, show

# Ustawienie dokładności obliczeń numerycznych:
mp.dps = 100


def get_term_structure_of_spot_interest_rates(date, file):
    # format daty: rrrr.mm.dd,  typ daty: str

    date = [int(ch) for ch in date.split('.')][:2]
    bonds_lst = []

    with open(file, 'r') as f:
        for line in f:
            bond = []
            l = line.split(',')

            # Odczytywanie czasu do wykupu (w miesiącach) obligacji:
            bond_maturity_date = [int(ch) for ch in l[0].split('.')][:2]
            bond_maturity = (bond_maturity_date[0] - date[0]) * 12 + \
                            (bond_maturity_date[1] - date[1])
            bond.append(bond_maturity)

            # Odczytywanie stopy kuponowej obligacji:
            coupon_rate = 0
            if l[1] != '':
                coupon_rate = mp.mpf(l[1]) / 100
            bond.append(coupon_rate)

            # Odczytywanie nominału obligacji:
            face_amount = int(l[3])
            bond.append(face_amount)

            # Odczytywanie ceny brudnej obligacji:
            dirty_price = mp.mpf(l[2]) + mp.mpf(l[11]) / 100 * face_amount
            # cena brudna = odsetki +
            # (cena czysta wyrażona jako % nominału)/100 * nominał
            bond.append(dirty_price)

            # Odczytywanie kodu ISIN obligacji:
            isin_code = l[7]
            bond.append(isin_code)

            bonds_lst.append(bond)

    # Sortowanie względem miesięcy do wykupu:
    bonds_lst = sorted(bonds_lst, key=lambda t: t[0])

    if bonds_lst[0][0] > 12 and bonds_lst[0][2] != 0:
        print('Nie jest możliwe odczytanie struktury terminowej '
              'stóp spot za pomocą metody bootstrapingu.\n'
              'Obligacja o najwcześniejszym terminie wykupu jest '
              'obligacją kuponową o wykupie dłuższym niż 1 rok.')
        return None

    step_term_structure_spot_interest_rates = [0]
    time = 1
    bond_n = 0
    while time <= bonds_lst[-1][0]:
        if time == bonds_lst[bond_n][0]:
            t = bonds_lst[bond_n][0]
            c = bonds_lst[bond_n][1]
            N = bonds_lst[bond_n][2]
            P = bonds_lst[bond_n][3]
            coupons_num = t // 12
            month_mod12 = t % 12
            for i in range(coupons_num):
                P -= (c * N) / (
                        (1 + step_term_structure_spot_interest_rates[
                            12 * i + month_mod12]
                         ) ** (12 * i + month_mod12))
            root = mp.root((1 + c) * N / P, t) - 1
            if isinstance(root, mpf) and root > 0:
                step_term_structure_spot_interest_rates.append(
                    root
                )
                bond_n += 1
            else:
                step_term_structure_spot_interest_rates.append(
                    step_term_structure_spot_interest_rates[-1]
                )
                bonds_lst.pop(bond_n)
        else:
            step_term_structure_spot_interest_rates.append(
                step_term_structure_spot_interest_rates[-1]
            )
        time += 1

    maturity_time_lst = []
    linear_term_structure_spot_interest = []
    for b in bonds_lst:
        maturity_time_lst.append(b[0])
        linear_term_structure_spot_interest.append(
            step_term_structure_spot_interest_rates[b[0]]
        )

    # Zwracamy:
    #    - strukturę stóp terminowych spot tylko dla danych czasów wykupów.
    return maturity_time_lst, linear_term_structure_spot_interest


if __name__ == '__main__':
    x, y = get_term_structure_of_spot_interest_rates('2019.12.23', 'result_table.txt')
    for i in range(len(x)):
        print(x[i], y[i], type(y[i]))
    plot(x, [12*el for el in y])
    show()
