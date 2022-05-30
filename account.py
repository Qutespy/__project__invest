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

class USER:
    def __init__(self, client: Services):
        self.client = client
        self.__accounts = []
        self.__position_wallet = []
        self.operation = []
        self.__wallet = []
        self.with_draw_limitsResponse=[]

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
        acc_user.to_csv('accounts.csv')
        return acc_user

    def return_account_id(self):
        return self.get_accounts()['id счета']

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

    def get_portfolio(self):
        '''возвращает инфу по состоянию кошелька пользователя'''
        for acc_id in self.return_account_id():
            wall = self.client.operations.get_portfolio(account_id=acc_id)
            self.__wallet.append(
                    [acc_id, self.__cast_money(wall.total_amount_shares), self.__cast_money(wall.total_amount_bonds),
                     self.__cast_money(wall.total_amount_etf),self.__cast_money(wall.total_amount_currencies),
                     self.__cast_money(wall.total_amount_futures), self.__cast_money(wall.expected_yield)])
            wallet_user = pd.DataFrame(data=self.__wallet,
                                        columns=['id счета', 'Общая стоимость акций(руб)',
                                        'Общая стоимость облигаций(руб)',
                                        'Общая стоимость фондов(руб)',
                                        'Общая стоимость валют(руб)',
                                        'Общая стоимость фьючерсов(руб)',
                                        'Текущая относительная доходность(%)'],
                                       index=range(1,len(self.__accounts)+1))
        if self.__wallet == []:
            print('Кошелек пользоваетля пуст')
        else:
            wallet_user.to_csv('wallet.csv')
            return wallet_user

    def get_portfolio_position(self):
        '''возвращает позиции в кошельке поьзоваетеля'''
        for acc_id in self.return_account_id():
            wall = self.client.operations.get_portfolio(account_id=acc_id)
            for pos in wall.positions:
                self.__position_wallet.append([pos.figi, pos.instrument_type, self.__cast_money(pos.quantity),
                                             self.__cast_money(pos.average_position_price),
                                             self.__cast_money(pos.expected_yield), self.__cast_money(pos.current_nkd),
                                             self.__cast_money(pos.average_position_price_pt),
                                             self.__cast_money(pos.current_price),
                                             self.__cast_money(pos.average_position_price_fifo),
                                             self.__cast_money(pos.quantity_lots)])
            position_wallet_user = pd.DataFrame(data=self.__position_wallet,
                                                columns=['Figi-идентификатора инструмента', 'Тип инструмента',
                                                         'Количество инструмента в портфеле в штуках',
                                                         'Средневзвешенная цена позиции',
                                                         'Текущая рассчитанная относительная доходность позиции, в %',
                                                         'Текущий НКД', 'Средняя цена лота в позиции в пунктах (для фьючерсов)',
                                                         'Текущая цена за 1 инструмент',
                                                         'Средняя цена лота в позиции по методу FIFO',
                                                         'Количество лотов в портфеле'],
                                                index = range(1, len(self.__position_wallet) + 1))
        if self.__position_wallet == []:
            print('нет позиций в кошельке пользователя')
        position_wallet_user.to_csv('wallet_position.csv')
        return position_wallet_user

#по умолчанию RUB , переделать для других валют!!!!!!!
    def __cast_money(self, val, to_rub=True):
        '''возвращает число во float'''
        return val.units + val.nano / 1e9


with Client(My_tokens.token_main_ro_all_accounts) as client:
    data = USER(client).get_portfolio_position()
    print(data)

