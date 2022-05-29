from tinkoff.invest import Client, RequestError, PortfolioResponse, PositionsResponse, PortfolioPosition, AccessLevel
from tokens import My_tokens
import pandas as pd
from tinkoff.invest.services import Services


import datetime
from typing import Optional
from pandas import DataFrame

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

'''def run(token):
    try:
        with Client(token) as client:
            print(USER(client).get_accounts())
    except RequestError as e:
        print(str(e))'''
class USER:
    def __init__(self, client: Services):
        self.client = client
        self.__accounts = []
        self.position_wallet = []
        self.operation = []
        self.wallet = []
        self.with_draw_limitsResponse=[]

    def __PrintingAccessLevel(self, name):
        if name == 'ACCOUNT_ACCESS_LEVEL_UNSPECIFIED':
            str = "Уровень доступа не определён"
            return str
        elif name == 'ACCOUNT_ACCESS_LEVEL_FULL_ACCESS':
            str = "Полный доступ к счёту"
            return str
        elif name == 'ACCOUNT_ACCESS_LEVEL_READ_ONLY':
            str = "Доступ с уровнем прав только чтение"
            return str
        elif name == 'ACCOUNT_ACCESS_LEVEL_NO_ACCESS':
            str = "Доступ отсутствует"
            return str

    def __PrintingAccountStatus(self, name):
        if name == 'ACCOUNT_STATUS_UNSPECIFIED':
            str = 'Статус счёта не определён'
            return str
        elif name == 'ACCOUNT_STATUS_NEW':
            str = 'Новый, в процессе открытия'
            return str
        elif name == 'ACCOUNT_STATUS_OPEN':
            str = 'Открытый и активный счёт'
            return str
        elif name == 'ACCOUNT_STATUS_CLOSED':
            str = 'Закрытый счёт'
            return str

    def get_accounts(self):
        '''возвращает dataframe  с инфой о счетах user'a'''
        acc = self.client.users.get_accounts()
        for account in acc.accounts:
            self.__accounts.append([account.id, account.name, self.__PrintingAccountStatus(account.status.name),
                                    account.opened_date,self.__PrintingAccessLevel(account.access_level.name)])
        acc_user = pd.DataFrame(data=self.__accounts,
                                columns=['id счета', 'название счета', 'статус счета',
                                         'Дата открытия счёта в часовом поясе UTC',
                                         'Уровень доступа токена к текущему счёту'],
                                index=range(1,len(self.__accounts)+1))

        return acc_user
with Client(My_tokens.token_to_read_brokerage_account) as client:
    USER(client).get_accounts().to_csv('token.csv')
    print(USER(client).get_accounts())
