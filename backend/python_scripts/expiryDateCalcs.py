import datetime

class ExpiryCalculator:
    @staticmethod
    def get_last_thursday_of_month(year, month):
        last_day = datetime.date(year, month, 1) + datetime.timedelta(days=32)
        last_day = last_day.replace(day=1) - datetime.timedelta(days=1)
        last_weekday = last_day.weekday()
        days_to_last_thursday = (last_weekday - 3 + 7) % 7
        return last_day - datetime.timedelta(days=days_to_last_thursday)

    @staticmethod
    def get_next_thursday():
        today = datetime.date.today()
        days_until_thursday = (3 - today.weekday() + 7) % 7
        return today + datetime.timedelta(days=days_until_thursday)


    async def expiry_dates(self, sIndex):
        today = datetime.date.today()
        near_expiry = self.get_next_thursday()
        if sIndex == 'bnf' and today != near_expiry:
            near_expiry = self.get_next_thursday() - datetime.timedelta(days=1)
        elif sIndex == 'bnf' and today == near_expiry:
            near_expiry = self.get_next_thursday() + datetime.timedelta(days=6)
        next_expiry = near_expiry + datetime.timedelta(days=7)
        this_month_last_thursday = self.get_last_thursday_of_month(today.year, today.month)
        next_month_last_thursday = self.get_last_thursday_of_month(today.year, (today.month + 1) % 12)

        if this_month_last_thursday in [near_expiry, next_expiry]:
            return [near_expiry.strftime("%d-%b-%Y"), next_expiry.strftime("%d-%b-%Y"), next_month_last_thursday.strftime("%d-%b-%Y")]
        else:
            return [near_expiry.strftime("%d-%b-%Y"), next_expiry.strftime("%d-%b-%Y"), this_month_last_thursday.strftime("%d-%b-%Y")]

    # async def expiry_dates(self):
        

# Usage:
async def main():
    calculator = ExpiryCalculator()
    nf_expiry_dates = await calculator.expiry_dates('nf')
    print("Nifty expiry dates =",nf_expiry_dates)
    bnf_expiry_dates = await calculator.expiry_dates('bnf')
    print("BankNifty expiry dates =",bnf_expiry_dates)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())