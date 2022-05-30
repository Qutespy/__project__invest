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
        self.__operation = []
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

    def __PrintingOperationState(self, name):
        if name == 'OPERATION_STATE_UNSPECIFIED':
            str = "Статус операции не определён"
            return str
        elif name == 'OPERATION_STATE_EXECUTED':
            str = "Исполнена"
            return str
        elif name == 'OPERATION_STATE_CANCELED':
            str = "Отменена"
            return str

    def __PrintingOperationType(self, name):
        if name == 'OPERATION_TYPE_UNSPECIFIED':
            str = "Тип операции не определён"
            return str
        elif name == 'OPERATION_TYPE_INPUT':
            str = "Пополнение брокерского счёта"
            return str
        elif name == 'OPERATION_TYPE_BOND_TAX':
            str = "Удержание НДФЛ по купонам"
            return str
        elif name == 'OPERATION_TYPE_OUTPUT_SECURITIES':
            str = "Вывод ЦБ"
            return str
        elif name == 'OPERATION_TYPE_OVERNIGHT':
            str = "Доход по сделке РЕПО овернайт"
            return str
        elif name == 'OPERATION_TYPE_TAX':
            str = "Удержание налога"
            return str
        elif name == 'OPERATION_TYPE_BOND_REPAYMENT_FULL':
            str = "Полное погашение облигаций"
            return str
        elif name == 'OPERATION_TYPE_SELL_CARD':
            str = "Продажа ЦБ с карты"
            return str
        elif name == 'OPERATION_TYPE_DIVIDEND_TAX':
            str = "Удержание налога по дивидендам"
            return str
        elif name == 'OPERATION_TYPE_OUTPUT':
            str = "Вывод денежных средств"
            return str
        elif name == 'OPERATION_TYPE_BOND_REPAYMENT':
            str = "Частичное погашение облигаций"
            return str
        elif name == 'OPERATION_TYPE_TAX_CORRECTION':
            str = "Корректировка налога"
            return str
        elif name == 'OPERATION_TYPE_SERVICE_FEE':
            str = "Удержание комиссии за обслуживание брокерского счёта"
            return str
        elif name == 'OPERATION_TYPE_BENEFIT_TAX':
            str = "Удержание налога за материальную выгоду"
            return str
        elif name == 'OPERATION_TYPE_MARGIN_FEE':
            str = "Удержание комиссии за непокрытую позицию"
            return str
        elif name == 'OPERATION_TYPE_BUY':
            str = "Покупка ЦБ"
            return str
        elif name == 'OPERATION_TYPE_BUY_CARD':
            str = "Покупка ЦБ с карты"
            return str
        elif name == 'OPERATION_TYPE_INPUT_SECURITIES':
            str = "Перевод ценных бумаг из другого депозитария"
            return str
        elif name == 'OPERATION_TYPE_SELL_MARGIN':
            str = "Продажа в результате Margin-call"
            return str
        elif name == 'OPERATION_TYPE_BROKER_FEE':
            str = "Удержание комиссии за операцию"
            return str
        elif name == 'OPERATION_TYPE_BUY_MARGIN':
            str = "Покупка в результате Margin-call"
            return str
        elif name == 'OPERATION_TYPE_DIVIDEND':
            str = "Выплата дивидендов"
            return str
        elif name == 'OPERATION_TYPE_SELL':
            str = "Продажа ЦБ"
            return str
        elif name == 'OPERATION_TYPE_COUPON':
            str = "Выплата купонов"
            return str
        elif name == 'OPERATION_TYPE_SUCCESS_FEE':
            str = "Удержание комиссии SuccessFee"
            return str
        elif name == 'OPERATION_TYPE_DIVIDEND_TRANSFER':
            str = "Передача дивидендного дохода"
            return str
        elif name == 'OPERATION_TYPE_ACCRUING_VARMARGIN':
            str = "Зачисление вариационной маржи"
            return str
        elif name == 'OPERATION_TYPE_WRITING_OFF_VARMARGIN':
            str = "Списание вариационной маржи"
            return str
        elif name == 'OPERATION_TYPE_DELIVERY_BUY':
            str = "Покупка в рамках экспирации фьючерсного контракта"
            return str
        elif name == 'OPERATION_TYPE_DELIVERY_SELL':
            str = "Продажа в рамках экспирации фьючерсного контракта"
            return str
        elif name == 'OPERATION_TYPE_TRACK_MFEE':
            str = "Комиссия за управление по счёту автоследования"
            return str
        elif name == 'OPERATION_TYPE_TRACK_PFEE':
            str = "Комиссия за результат по счёту автоследования"
            return str
        elif name == 'OPERATION_TYPE_TAX_PROGRESSIVE':
            str = "Удержание налога по ставке 15%"
            return str
        elif name == 'OPERATION_TYPE_BOND_TAX_PROGRESSIVE':
            str = 'Удержание налога по купонам по ставке 15%'
            return str
        elif name == 'OOPERATION_TYPE_DIVIDEND_TAX_PROGRESSIVE':
            str = "Удержание налога по дивидендам по ставке 15%"
            return str
        elif name == 'OPERATION_TYPE_BENEFIT_TAX_PROGRESSIVE':
            str = "Удержание налога за материальную выгоду по ставке 15%"
            return str
        elif name == 'OPERATION_TYPE_TAX_CORRECTION_PROGRESSIVE':
            str = "Корректировка налога по ставке 15%"
            return str
        elif name == 'OPERATION_TYPE_TAX_REPO_PROGRESSIVE':
            str = "Удержание налога за возмещение по сделкам РЕПО по ставке 15%"
            return str
        elif name == 'OPERATION_TYPE_TAX_REPO':
            str = "Удержание налога за возмещение по сделкам РЕПО"
            return str
        elif name == 'OPERATION_TYPE_TAX_REPO_HOLD':
            str = "Удержание налога по сделкам РЕПО"
            return str
        elif name == 'OPERATION_TYPE_TAX_REPO_REFUND':
            str = "Возврат налога по сделкам РЕПО"
            return str
        elif name == 'OPERATION_TYPE_TAX_REPO_HOLD_PROGRESSIVE':
            str = "Удержание налога по сделкам РЕПО по ставке 15%"
            return str
        elif name == 'OPERATION_TYPE_TAX_REPO_REFUND_PROGRESSIVE':
            str = "Возврат налога по сделкам РЕПО по ставке 15%"
            return str
        elif name == 'OPERATION_TYPE_DIV_EXT':
            str = "Выплата дивидендов на карту"
            return str
        elif name == 'OPERATION_TYPE_TAX_CORRECTION_COUPON':
            str = "	Корректировка налога по купонам"
            return str

    def get_operations(self, from__, to__):
        '''
             возвращает все транзакции
                                          '''
        for acc_id in self.return_account_id():
            for operation in self.client.operations.get_operations(
                    account_id=acc_id,
                    from_=datetime.datetime(*from__),
                    to=datetime.datetime(*to__)
            ).operations:
                self.__operation.append([operation.id, operation.currency, self.__cast_money(operation.payment),
                                       self.__cast_money(operation.price), self.__PrintingOperationState(operation.state.name),
                                       operation.quantity,operation.quantity_rest, operation.figi,
                                       operation.instrument_type,operation.date,
                                       self.__PrintingOperationType(operation.operation_type.name)])

            all_operation_user = pd.DataFrame(data=self.__operation,
                                            columns=['id', 'Валюта операции', 'Сумма операции',
                                                     'Цена операции за 1 инструмент', 'Статус операции',
                                                     'Количество единиц инструмента', 'Неисполненный остаток по сделке',
                                                     'Figi-идентификатор инструмента', 'Тип инструмента',
                                                     'Дата и время операции в формате часовом поясе UTC',
                                                     'Тип операции'],
                                              index=range(1, len(self.__operation) + 1)
                                              )
        all_operation_user.to_csv('operation.csv')
        return all_operation_user
    
with Client(My_tokens.token_main_ro_all_accounts) as client:
    data = USER(client).get_portfolio_position()
    print(data)

