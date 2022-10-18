class TradingStats:
    def __init__(self, csv, navTag, operateTag):
        records = csv[(csv[operateTag] == 1) | (csv[operateTag] == 3)][[navTag, operateTag]]

        count_suc = 0
        revenue = 0
        count_fail = 0
        expense = 0
        temp_buy_nav = 0
        temp_sale_nav = 0
        state = 0
        for row in records.iterrows():
            state = row[1][1]
            if state == 1:
                temp_buy_nav = row[1][0]
            elif state == 3:
                temp_sale_nav = row[1][0]
                diff = temp_sale_nav - temp_buy_nav
                if diff > 0:
                    count_suc += 1
                    revenue += diff
                else:
                    count_fail += 1
                    expense += diff

        self.countSuc = count_suc
        self.countFail = count_fail

    def winningTradingCount(self):
        return self.countSuc

    def tradingCount(self):
        return self.countSuc + self.countFail

