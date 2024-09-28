import talib
import numpy as np
import time # 需要在策略头部添加time库

differenceC = -30
orderC      =  490

ContractNo0 = "DCE|F|V|2501"  # 交易的品种
ContractNo1 = "DCE|F|V|2502"  # 交易的品种
ContractNo2 = "DCE|S|V|2501|2502"  # 交易的品种


# 创建字典
CodeDict = {'c0': ContractNo0, 'c1': ContractNo1, 'c2': ContractNo2}
retMsg = ''


def initialize(context): 
        
    SetTriggerType(4, ['225950','101450','112950','145950'])  # 定时触发
    SetTriggerType(3, 20000)                   # 每隔固定时间触发：时间间隔为1000毫秒
    SetTriggerType(1)
    SetTriggerType(2)   # 交易数据触发
    SetOrderWay(1)   # 发单方式设置为实时发单
    # 设置基准合约，会覆盖界面设置的合约，建议通过界面设置(屏蔽SetBarInterval后则界面添加合约生效)
    #for key in CodeDict:
    #    SetBarInterval(CodeDict[key], 'M', 1, 5, 1)
        
    SubQuote(ContractNo0,ContractNo1,ContractNo2)
    SetActual()  # 未开启实盘运行！

    
def clear():
    if len(retMsg) > 0 :
        if A_OrderStatus(retMsg) == '4':
            A_DeleteOrder(retMsg)
# 策略退出前执行该函数一次
def exit_callback(context):
    LogInfo("策略退出")
    clear()

def handle_data(context):
    global retMsg

    #StopTrade()
    
    # 即时行情触发时打印信息
    if context.triggerType() == "S" and context.contractNo() == CodeDict['c0']:
        
        difference = round(Q_BidPrice(CodeDict['c0'])-Q_BidPrice(CodeDict['c1']),PriceScale(CodeDict['c0']))
        LogInfo( "------即时行情触发v2-----------------------")
        LogInfo( "差值：",difference )
        LogInfo( "设定差值：",differenceC )
        LogInfo( "订单号：",retMsg )
        LogInfo( "下单量：",len( A_AllOrderNo(CodeDict['c1']) ) )

        distance1 = Q_AskPrice(CodeDict['c1'])-Q_BidPrice(CodeDict['c1'])
        distance0 = Q_AskPrice(CodeDict['c0'])-Q_BidPrice(CodeDict['c0'])
        distance  = distance1-distance0
        #LogInfo( "差值distance1：",distance1 )
        #LogInfo( "差值distance0：",distance0 )
        #LogInfo( "PriceTick(CodeDict['c1'])：",PriceTick(CodeDict['c1']) )

        LogInfo( "差值distance：",distance )
        OrdPrice = Q_BidPrice(CodeDict['c1'])
        if distance > PriceTick(CodeDict['c1'])*5:
            OrdPrice = Q_BidPrice(CodeDict['c1'])+PriceTick(CodeDict['c1'])

        #差值越大，代表买入c1，卖出c0的机会越大
        if difference > differenceC \
        and len(retMsg)<1  \
        and len( A_AllOrderNo(CodeDict['c1']) ) < orderC:

            #LogInfo('差值越大，代表买入c1，卖出c0的机会越大')
            if A_SellPositionCanCover(CodeDict['c1']) > 0:
                
                retCode, retMsg = A_SendOrder( \
                Enum_Buy(), \
                Enum_Exit(), \
                1, \
                OrdPrice,\
                CodeDict['c1'] )

                LogInfo("下单订单号：",retMsg)
                if retCode != 0:
                    LogInfo("下单订失败！！！：",retMsg)
                    retMsg = ''

                

        if len(retMsg) > 0 :
            bidPrice = round(Q_BidPrice(CodeDict['c1']),PriceScale(CodeDict['c1']))
            orderPrice = round( A_OrderPrice(retMsg),PriceScale(CodeDict['c1']))
            if bidPrice > orderPrice or difference < differenceC:
                if  A_OrderStatus(retMsg) == '4':
                    A_DeleteOrder(retMsg)
                    LogInfo("！！！删除订单号：",retMsg)
                    retMsg = ''

    elif context.triggerType() == "O":  # 委托状态变化触发    
        if len(retMsg) > 0 \
         and ( A_OrderStatus(retMsg) == '6' or A_OrderStatus(retMsg) == '5') :
            LogInfo('不活跃订单成交或部分成交')
            if context.triggerData()['Cont'] == CodeDict['c1'] \
            and context.triggerData()['MatchQty'] > 0 \
            and  retMsg == context.triggerData()['StrategyOrderId']:
                LogInfo('发送活跃合约订单')
                A_SendOrder( \
                Enum_Sell(), \
                Enum_Exit(), \
                1, \
                Q_BidPrice(CodeDict['c0'])-PriceTick(CodeDict['c0']), \
                CodeDict['c0'] )
    
    elif context.triggerType() == 'Z':   # 触发类型为交易数据中的市场状态触发
        exhData = context.triggerData()
        if exhData["TradeState"] == '3':  # 连续交易
            if len( A_AllOrderNo(CodeDict['c1']) ) < orderC :
                LogInfo("市场状态为连续交易，所有的订单数量小于orderC")
                LogInfo("重启策略！！！！")
                ReloadStrategy()


        elif exhData["TradeState"] == '4' or exhData["TradeState"] == '5':  # 当前交易所状态为交易暂停或交易闭市
            LogInfo("当前交易所状态为交易暂停或交易闭市,StopTrade")
            StopTrade()

    elif context.triggerType() == "T":  # 定时触发
        LogInfo("定时触发,clear and StopTrade")
        clear()
        StopTrade()

    #elif context.triggerType() == "C":  # delive
        #a = A_AllOrderNo(CodeDict['c1'])
        #LogInfo( '-----重启策略！！！！--------' )
        #clear()
        #StopTrade()
        
 










