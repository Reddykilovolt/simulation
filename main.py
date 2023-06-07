import streamlit as st
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import plotly.graph_objects as go

#日付設定
today = datetime.today()
year = today.strftime('%Y')
month = today.strftime('%m')
day = today.strftime('%d')
non_zero_day = today.strftime('%d').lstrip("0")

font_path = 'TakaoPGothic.ttf'
font_property = FontProperties(fname=font_path)

#kWhを1カ月単位から任意の期間のkWhを算出する
def kWh_calc(one_kWh, month):
    kWh_chenge = [1.00,1.25,1.17,0.91,0.86,0.99,1.43,1.31,1.12]
    start_index = month - 7
    kWh_chenge_select = kWh_chenge[start_index]
    kWh_chenge = [x / kWh_chenge_select for x in kWh_chenge]
    kWh = [one_kWh * x for x in kWh_chenge]
    kWh = kWh[start_index:]
    kWh_sum = int(sum(kWh))
    kWh.append(kWh_sum)
    display_month = ['7月','8月','9月','10月','11月','12月','1月','2月','3月','合計']
    display_month = display_month[start_index:]
    return kWh, display_month

#㎥を1カ月単位から任意の期間の㎥を算出する
def gas_calc(one_gas, month):
    gas_chenge = [1.00,0.89,0.89,1.00,1.22,1.67,2.22,2.00,1.78]
    start_index = month - 7
    gas_chenge_select = gas_chenge[start_index]
    gas_chenge = [x / gas_chenge_select for x in gas_chenge]
    gas = [one_gas * x for x in gas_chenge][start_index:]
    gas_sum = int(sum(gas))
    gas.append(gas_sum)
    return gas

#日本ガスファミリープランの基本料金算出
def NG_amp_price_calc(base_amp,month):
    base_30 = 893.72
    base_40 = 1229.32
    base_50 = 1536.65
    base_60 = 1843.98

    base_price_cp = {
    7:{
        30:[0,0,0,446.86,base_30,base_30,base_30,base_30,base_30],
        40:[0,0,0,614.66,base_40,base_40,base_40,base_40,base_40],
        50:[0,0,0,768.32,base_50,base_50,base_50,base_50,base_50],
        60:[0,0,0,921.99,base_60,base_60,base_60,base_60,base_60]
        },
    8:{
        30:[0,0,0,base_30,base_30,base_30,base_30,base_30],
        40:[0,0,0,base_40,base_40,base_40,base_40,base_40],
        50:[0,0,0,base_50,base_50,base_50,base_50,base_50],
        60:[0,0,0,base_60,base_60,base_60,base_60,base_60]
        },
    9:{
        30:[base_30,base_30,base_30,base_30,base_30,base_30,base_30],
        40:[base_40,base_40,base_40,base_40,base_40,base_40,base_40],
        50:[base_50,base_50,base_50,base_50,base_50,base_50,base_50],
        60:[base_60,base_60,base_60,base_60,base_60,base_60,base_60]
        },
    10:{
        30:[0,0,0,base_30,base_30,base_30],
        40:[0,0,0,base_40,base_40,base_40],
        50:[0,0,0,base_50,base_50,base_50],
        60:[0,0,0,base_60,base_60,base_60]
        },
    11:{
        30:[0,0,0,base_30,base_30],
        40:[0,0,0,base_40,base_40],
        50:[0,0,0,base_50,base_50],
        60:[0,0,0,base_60,base_60]
        },
    12:{
        30:[0,0,0,base_30],
        40:[0,0,0,base_40],
        50:[0,0,0,base_50],
        60:[0,0,0,base_60]
        }
    }
    base_bill = base_price_cp[month][base_amp]
    base_bill_sum = sum(base_bill)
    base_bill.append(base_bill_sum)
    return base_bill

#日本ガスビジネスプランプランの基本料金算出
def NG_kVA_price_calc(kVA, month):
    kVA_list = []
    kVA = 307.33 * kVA
    kVA_2 = kVA / 2

    base_price_cp = {
    7:[0,0,0,kVA_2,kVA,kVA,kVA,kVA,kVA],
    8:[0,0,0,kVA,kVA,kVA,kVA,kVA],
    9:[kVA,kVA,kVA,kVA,kVA,kVA,kVA],
    10:[0,0,0,kVA,kVA,kVA],
    11:[0,0,0,kVA,kVA],
    12:[0,0,0,kVA]
    }
    kVA_list = base_price_cp[month]
    kVA_sum = sum(kVA_list)
    kVA_list.append(kVA_sum)
    return kVA_list

#日本ガス低圧電力の基本料金算出
def NG_kW_price_calc(kW, month):
    kW_list = []
    kW = 922.03 * kW
    kW_2 = kW / 2    
    base_price_cp = {
    7:[kW_2,kW_2,kW_2,kW_2,kW,kW,kW,kW,kW],
    8:[kW_2,kW_2,kW_2,kW,kW,kW,kW,kW],
    9:[kW_2,kW_2,kW,kW,kW,kW,kW],
    10:[kW_2,kW,kW,kW,kW,kW],
    11:[kW,kW,kW,kW,kW],
    12:[kW,kW,kW,kW]
    }
    kW_list = base_price_cp[month]
    kW_sum = sum(kW_list)
    kW_list.append(kW_sum)
    return kW_list

#九電従電B及びSFPの基本料金算出
def Q_amp_price_calc(base_amp,month):
    base_bill =[]
    base_n = 31.624
    base_n = base_n * base_amp
    base_bill = [base_n] * 9
    start_index = month - 7
    base_bill = base_bill[start_index:]
    base_bill_sum = sum(base_bill)
    base_bill.append(base_bill_sum)
    return base_bill

#九電従電C及びSBPの基本料金算出
def Q_kVA_price_calc(kVA, month):
    kVA_list = []
    kVA = 316.24 * kVA
    kVA_list = [kVA] * 9
    start_index = month - 7
    kVA_list = kVA_list[start_index:]
    kVA_sum = sum(kVA_list)
    kVA_list.append(kVA_sum)
    return kVA_list

#九電低圧電力の基本料金算出
def Q_kW_price_calc(kW, month):
    kW_list = []
    kW = 1023.23 * kW
    kW_list = [kW] * 9
    start_index = month - 7
    kW_list = kW_list[start_index:]
    kW_sum = sum(kW_list)
    kW_list.append(kW_sum)
    return kW_list

#日本ガスファミリープランの従量料金、セット割算出
def NG_kWh_set_calc(kWh, base_amp):                                                                              
    unit_price_1 = 18.27
    unit_price_2 = 23.88
    unit_price_3 = 25.83

    kWh_bill = []
    kWh = kWh[:-1]

    for kWh_value in kWh:
        if kWh_value <= 120:
            kWh_bill.append(kWh_value * unit_price_1)

        elif kWh_value <= 300:
            kWh_bill_1 = 120 * unit_price_1
            kWh_bill_2 = (kWh_value - 120) * unit_price_2
            kWh_bill.append(kWh_bill_1 + kWh_bill_2)

        else:
            kWh_bill_1 = 120 * unit_price_1
            kWh_bill_2 = (300 - 120) * unit_price_2
            kWh_bill_3 = (kWh_value - 300) * unit_price_3
            kWh_bill.append(kWh_bill_1 + kWh_bill_2 + kWh_bill_3)
    kWh_bill_sum = int(sum(kWh_bill))
    kWh_bill.append(kWh_bill_sum)
    set_per = {30: -0.005, 40: -0.02, 50: -0.02, 60: -0.03}
    set_per = set_per[base_amp]
    set_kWh_bill = [x * set_per for x in kWh_bill]
    return kWh_bill, set_kWh_bill

#日本ガスビジネスプランの従量料金、セット割算出
def NG_kVA_set_calc(kWh):                                                                              
    unit_price_1 = 18.27
    unit_price_2 = 23.88
    unit_price_3 = 25.02

    kWh_bill = []
    kWh = kWh[:-1]

    for kWh_value in kWh:
        if kWh_value <= 120:
            kWh_bill.append(kWh_value * unit_price_1)

        elif kWh_value <= 300:
            kWh_bill_1 = 120 * unit_price_1
            kWh_bill_2 = (kWh_value - 120) * unit_price_2
            kWh_bill.append(kWh_bill_1 + kWh_bill_2)

        else:
            kWh_bill_1 = 120 * unit_price_1
            kWh_bill_2 = (300 - 120) * unit_price_2
            kWh_bill_3 = (kWh_value - 300) * unit_price_3
            kWh_bill.append(kWh_bill_1 + kWh_bill_2 + kWh_bill_3)
    kWh_bill_sum = int(sum(kWh_bill))
    kWh_bill.append(kWh_bill_sum)
    set_per = -0.03
    set_kWh_bill = [x * set_per for x in kWh_bill]
    return kWh_bill, set_kWh_bill

#日本ガス低圧電力の従量料金算出
def NG_kW_set_calc(kWh):                                                                              
    unit_price_summer = 17.26
    unit_price_other = 15.58

    kWh_bill = []
    kWh = kWh[:-1]

    if month == '7'or'8'or'9':
        for kWh_value in kWh:
                kWh_bill.append(kWh_value * unit_price_summer)
    else:
        kWh_bill = kWh * unit_price_other
        for kWh_value in kWh:
                kWh_bill.append(kWh_value * unit_price_summer)
    
    kWh_bill_sum = int(sum(kWh_bill))
    kWh_bill.append(kWh_bill_sum)
    return kWh_bill

#日本ガスガス料金の算出及びセット割計算
def NG_gas_set_calc(gas, gas_class):
    base_price_1 = 753.50
    base_price_2 = 1386.0
    base_price_3 = 2006.4
    base_price_4 = 6503.2

    unit_price_1 = 260.98
    unit_price_2 = 218.79
    unit_price_3 = 198.11
    unit_price_4 = 168.13

    gas_bill = []
    set_gas_bill = []
    
    gas = gas[:-1]

    for gas_value in gas:
        if gas_value <= 15:
            _gas_bill = base_price_1 + (gas_value * unit_price_1)
            gas_bill.append(_gas_bill)
            set_gas_bill.append(-0.005 * _gas_bill)

        elif gas_value <= 30:
            _gas_bill = base_price_2 + (gas_value * unit_price_2)
            gas_bill.append(_gas_bill)
            set_gas_bill.append(-0.015 * _gas_bill)

        elif gas_value <= 150:
            _gas_bill = base_price_3 + (gas_value * unit_price_3)
            gas_bill.append(_gas_bill)
            set_gas_bill.append(-0.03 * _gas_bill)

        else:
            _gas_bill = base_price_4 + (gas_value * unit_price_4)
            gas_bill.append(_gas_bill)
            set_per = -0.04
            set_gas_bill.append(-0.04 * _gas_bill)
    gas_bill_sum = int(sum(gas_bill))
    gas_bill.append(gas_bill_sum)
    set_gas_bill_sum = int(sum(set_gas_bill))
    set_gas_bill.append(set_gas_bill_sum)

    set_gas_bill = [0 for _ in set_gas_bill] if gas_class == "業務用" else set_gas_bill
    return gas_bill, set_gas_bill

#九電従電B及びSFPの従量料金、特別割割引の算出
def Q_kWh_set_calc(kWh, month, page):
    unit_price_1 = 18.28
    unit_price_2 = 23.88
    unit_price_3 = 26.88 if page == '九州電力_従量電灯B' else 25.78

    kWh_bill = []
    kWh = kWh[:-1]

    for kWh_value in kWh:
        if kWh_value <= 120:
            kWh_bill.append(kWh_value * unit_price_1)

        elif kWh_value <= 300:
            kWh_bill_1 = 120 * unit_price_1
            kWh_bill_2 = (kWh_value - 120) * unit_price_2
            kWh_bill.append(kWh_bill_1 + kWh_bill_2)

        else:
            kWh_bill_1 = 120 * unit_price_1
            kWh_bill_2 = (300 - 120) * unit_price_2
            kWh_bill_3 = (kWh_value - 300) * unit_price_3
            kWh_bill.append(kWh_bill_1 + kWh_bill_2 + kWh_bill_3)
    
    kWh_bill_sum = int(sum(kWh_bill))
    kWh_bill.append(kWh_bill_sum)

    set_bill = [-55] * 9 if page == '九州電力_従量電灯B' else [0] * 8 + [-777]
    set_bill_sum = sum(set_bill)
    set_bill.append(set_bill_sum)
    start_index = month - 7
    set_bill = set_bill[start_index:]
    return kWh_bill, set_bill

#九電従電C及びSBPの従量料金の算出
def Q_kVA_set_calc(kWh, month, page):
    if page == '九州電力_従量電灯C':
        unit_price_1 = 18.28
        unit_price_2 = 23.88
        unit_price_3 = 26.88

        kWh_bill = []
        kWh = kWh[:-1]
        
        for kWh_value in kWh:
            if kWh_value <= 120:
                kWh_bill.append(kWh_value * unit_price_1)

            elif kWh_value <= 300:
                kWh_bill_1 = 120 * unit_price_1
                kWh_bill_2 = (kWh_value - 120) * unit_price_2
                kWh_bill.append(kWh_bill_1 + kWh_bill_2)

            else:
                kWh_bill_1 = 120 * unit_price_1
                kWh_bill_2 = (300 - 120) * unit_price_2
                kWh_bill_3 = (kWh_value - 300) * unit_price_3
                kWh_bill.append(kWh_bill_1 + kWh_bill_2 + kWh_bill_3)
    else:
        unit_price = 23.88

        kWh_bill = []

        for kWh_value in kWh:
            kWh_bill.append(kWh_value * unit_price)

    kWh_bill_sum = int(sum(kWh_bill))
    kWh_bill.append(kWh_bill_sum)

    set_bill = [-55] * 9 if page == '九州電力_従量電灯C' else [0] * 9
    start_index = month - 7
    set_bill = set_bill[start_index:]
    set_bill_sum = sum(set_bill)
    set_bill.append(set_bill_sum)    
    return kWh_bill, set_bill

#九州電力低圧電力の従量料金算出
def Q_kW_set_calc(kWh):                                                                              
    unit_price_summer = 17.27
    unit_price_other = 15.58

    kWh_bill = []
    kWh = kWh[:-1]

    if month == '7'or'8'or'9':
        for kWh_value in kWh:
                kWh_bill.append(kWh_value * unit_price_summer)
    else:
        kWh_bill = kWh * unit_price_other
        for kWh_value in kWh:
                kWh_bill.append(kWh_value * unit_price_summer)

    kWh_bill_sum = int(sum(kWh_bill))
    kWh_bill.append(kWh_bill_sum)    

    return kWh_bill

#再エネ賦課金の算出
def re_energy_calc(kWh, month):
    re_energy_price = 1.40
    re_energy_bill = [x * re_energy_price for x in kWh]
    #start_index = month - 7
    #re_energy_bill = re_energy_bill[start_index:]
    return re_energy_bill

#燃調費の算出(自由料金)
def fuel_calc(kWh, month, fuel_chenge):
    if fuel_chenge == "上昇傾向":
        fuel_bills = [6.17, 5.49, 6.0, 6.3, 6.6, 7.0, 7.3, 7.5, 8.0]
    if fuel_chenge == "変化なし":
        fuel_bills = [6.17, 5.49, 5.49, 5.49, 5.49, 5.49, 5.49, 5.49, 5.49]
    if fuel_chenge == "下降傾向":
        fuel_bills = [6.17, 5.49, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0]
    start_index = month - 7
    fuel_bill = fuel_bills[start_index:]
    fuel_bill = [x * y for x, y in zip(fuel_bill, kWh)]
    fuel_bill_sum = sum(fuel_bill)
    fuel_bill.append(fuel_bill_sum)
    return fuel_bill, fuel_bills

#燃調費の算出(規制料金)
def reg_fuel_calc(kWh, month, fuel_chenge):
    if fuel_chenge == "上昇傾向":
        fuel_bills = [1.84] * 9
    if fuel_chenge == "変化なし":
        fuel_bills = [1.84] * 9
    if fuel_chenge == "下降傾向":
        fuel_bills = [1.84] * 9
    start_index = month - 7
    fuel_bill = fuel_bills[start_index:]
    fuel_bill = [x * y for x, y in zip(fuel_bill, kWh)]
    fuel_bill_sum = sum(fuel_bill)
    fuel_bill.append(fuel_bill_sum)
    return fuel_bill, fuel_bills

#激変緩和(電気)の算出
def kanwa_calc(kWh, month):
    kanwa_bill = [-7, -7, -7, -3.5, 0, 0, 0, 0, 0]
    start_index = month - 7
    kanwa_bill = kanwa_bill[start_index:]
    kanwa_bill = [x * y for x, y in zip(kanwa_bill, kWh)]
    kanwa_bill_sum = sum(kanwa_bill)
    kanwa_bill.append(kanwa_bill_sum)
    return kanwa_bill

#激変緩和(ガス)の算出
def gas_kanwa_calc(gas, month):
    gas_kanwa_bill = [-30, -30, -30, -15, 0, 0, 0, 0, 0]
    start_index = month - 7
    gas_kanwa_bill = gas_kanwa_bill[start_index:]
    gas_kanwa_bill = [x * y for x, y in zip(gas_kanwa_bill, gas)]
    gas_kanwa_bill_sum = sum(gas_kanwa_bill)
    gas_kanwa_bill.append(gas_kanwa_bill_sum)
    return gas_kanwa_bill

#燃調費の傾向
def fuel_vision(fuel_chenge, page):
    x_1 = ['2022/4','2022/5','2022/6','2022/7','2022/8','2022/9','2022/10','2022/11','2022/12',
        '2023/1','2023/2','2023/3','2023/4','2023/5','2023/6', '2023/7']
    x_2 = ['2023/8','2023/9','2023/10','2023/11','2023/12','2024/1','2024/2','2024/3']

    fuel_bills_Q_1 = [1.57, 1.72, 1.85, 1.92, 1.94, 1.94,
                    1.94, 1.94, 1.94, 1.94, 1.94, 1.94,
                    1.94, 1.94, 1.94, 1.94]
    fuel_bills_Q_2 = [1.94, 1.94, 1.94, 1.94, 1.94, 1.94, 1.94, 1.94]
    
    fuel_bills_NG_1 = [1.57, 1.72, 1.85, 2.48, 3.32, 4.58,
                    5.82, 6.77, 7.63, 8.12, 8.51, 8.19,
                    7.55, 6.80, 6.17, 5.49]
    
    if fuel_chenge == "上昇傾向":
        fuel_bills_NG_2 = [5.49, 6.0, 6.3, 6.6, 7.0, 7.3, 7.5, 8.0]
    if fuel_chenge == "変化なし":
        fuel_bills_NG_2 = [5.49, 5.49, 5.49, 5.49, 5.49, 5.49, 5.49, 5.49]
    if fuel_chenge == "下降傾向":
        fuel_bills_NG_2 = [5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 2.0]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_1, y=fuel_bills_NG_1, mode='lines', line=dict(color='blue'), name='日本ガス_過去実績'))
    fig.add_trace(go.Scatter(x=x_2, y=fuel_bills_NG_2, mode='lines', line=dict(color='blue',dash='dot'), name='日本ガス_今後の推移予測'))
    fig.add_trace(go.Scatter(x=x_1,
                            y=fuel_bills_Q_1 if page == '九州電力_従量電灯B' else fuel_bills_NG_1,
                            mode='lines', line=dict(color='red'), name='九州電力_過去実績'))
    fig.add_trace(go.Scatter(x=x_2,
                            y=fuel_bills_Q_2 if page == '九州電力_従量電灯B' else fuel_bills_NG_2,
                            mode='lines', line=dict(color='red',dash='dot'), name='九州電力_今後の推移予測'))
    fig.update_layout(xaxis_title='月', yaxis_title='燃調費[円/kWh]',
                    font=dict(family='TakaoPGothic', size=12, color='black')
                    )
    # グラフを表示
    st.plotly_chart(fig, static_fonts=True)    

#電気料金比較のグラフ
def plot_comparison_kWh_graph(df_kWh_NG, df_kWh_Q, page):
    df_kWh_NG = df_kWh_NG.drop(['合計'], axis=1)
    df_kWh_NG = df_kWh_NG.drop(['合計'], axis=0)
    df_kWh_Q = df_kWh_Q.drop(['合計'], axis=1)
    df_kWh_Q = df_kWh_Q.drop(['合計'], axis=0)

    months = df_kWh_Q.index.tolist()
    data1 = df_kWh_NG['基本料金']
    data2 = df_kWh_NG['従量料金']
    data3 = df_kWh_NG['燃調費']
    data4 = df_kWh_NG['再エネ賦課金']
    data5 = df_kWh_NG['激変緩和']
    if page == '九州電力_低圧動力':
        data6 = 0 
    else:
        data6 = df_kWh_NG['特別割'] 

    data7 = df_kWh_Q['基本料金']
    data8 = df_kWh_Q['従量料金']
    data9 = df_kWh_Q['燃調費']
    data10 = df_kWh_Q['再エネ賦課金']
    data11 = df_kWh_Q['激変緩和']
    if page == '九州電力_低圧動力':
        data12 = 0 
    else:
        data12 = df_kWh_Q['特別割']

    #plt.rcParams['font.family'] = 'MS Gothic'#文字化け防止
    bar_width = 0.35 #バーの幅
    bar_pos1 = np.arange(len(months)) #グループ1のバーの位置
    bar_pos2 = bar_pos1 + bar_width + 0.05 #グループ2のバーの位置

    # グラフの描画
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.bar(bar_pos1, data1, width=bar_width, color='forestgreen', label='基本料金')
    ax.bar(bar_pos1, data2, width=bar_width, color='yellowgreen', bottom=data1, label='従量料金')
    ax.bar(bar_pos1, data3, width=bar_width, color='darkorange', bottom=np.add(data1, data2), label='燃調費')
    ax.bar(bar_pos1, data4, width=bar_width, color='palegreen', bottom=np.add(data1, data2, data3), label='再エネ賦課金')
    ax.bar(bar_pos1, data5, width=bar_width, color='plum', label='激変緩和')
    ax.bar(bar_pos1, data6, width=bar_width, color='red', bottom=data5, label='特別割')
    ax.bar(bar_pos2, data7, width=bar_width, color='forestgreen')
    ax.bar(bar_pos2, data8, width=bar_width, color='yellowgreen', bottom=data7)
    ax.bar(bar_pos2, data9, width=bar_width, color='darkorange', bottom=np.add(data7, data8))
    ax.bar(bar_pos2, data10, width=bar_width, color='palegreen', bottom=np.add(data7, data8, data9))
    ax.bar(bar_pos2, data11, width=bar_width, color='plum')
    ax.bar(bar_pos2, data12, width=bar_width, color='red', bottom=data11)

    # x軸の設定
    ax.set_xticks(bar_pos1 + bar_width / 2)
    ax.set_xticklabels(months, fontproperties=font_property, fontsize=15)

    # グラフのタイトルと凡例
    ax.set_title('日本ガスと九州電力の電気料金比較', fontproperties=font_property, fontsize=20)
    ax.legend(bbox_to_anchor=(1, 1), loc='upper left', prop=font_property)

    # グラフの0の位置に線を引く
    ax.axhline(0, color='grey', linestyle='--', linewidth=1)

    # グラフの表示
    image_path = 'graph.png'
    fig.savefig(image_path)

    return image_path

#ガス料金比較のグラフ
def plot_comparison_gas_graph(df_gas_NG):
    df_gas_NG = df_gas_NG.drop(['合計'], axis=1)
    df_gas_NG = df_gas_NG.drop(['合計'], axis=0)

    months = df_gas_NG.index.tolist()
    data1 = df_gas_NG['ガス料金']
    data2 = df_gas_NG['激変緩和']
    data3 = df_gas_NG['特別割']

    #plt.rcParams['font.family'] = 'MS Gothic'#文字化け防止
    bar_width = 0.35
    bar_pos1 = np.arange(len(months)) #グループ1のバーの位置

    # グラフの描画
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(bar_pos1, data1, width=bar_width, color='forestgreen', label='ガス料金')
    ax.bar(bar_pos1, data2, width=bar_width, color='plum', label='激変緩和')
    ax.bar(bar_pos1, data3, width=bar_width, color='red', bottom=data2, label='特別割')

    # x軸の設定
    ax.set_xticks(bar_pos1, fontproperties=font_property)
    ax.set_xticklabels(months, fontproperties=font_property, fontsize=15)

    # グラフのタイトルと凡例
    ax.set_title('特別割(セット割)適用時のガス料金', fontproperties=font_property, fontsize=20)
    ax.legend(bbox_to_anchor=(1, 1), loc='upper left', prop=font_property)

    # グラフの0の位置に線を引く
    ax.axhline(0, color='grey', linestyle='--', linewidth=1)

    # グラフの表示
    image_path = 'graph.png'
    fig.savefig(image_path)

    return image_path

def plot_comparison_total_graph(df_kWh_NG_T, df_kWh_Q_T, df_gas_NG_T, display_month):
    kWh_NG_sum_display = []
    kWh_Q_sum_display = []
    gas_NG_sum_display = []
    gas_Q_sum_display = []
    for month in display_month:
        kWh_NG_sum_display.append(df_kWh_NG_T.loc['合計', month])
        kWh_Q_sum_display.append(df_kWh_Q_T.loc['合計', month])
        gas_NG_sum_display.append(df_gas_NG_T.loc['合計', month] + df_gas_NG_T.loc['特別割', month])
        gas_Q_sum_display.append(df_gas_NG_T.loc['合計', month])

    kWhgas_NG_sum_display = [x + y for x, y in zip(kWh_NG_sum_display, gas_NG_sum_display)]
    kWhgas_Q_sum_display = [x + y for x, y in zip(kWh_Q_sum_display, gas_Q_sum_display)]

    data_total_NG = {
        'でんき料金(切替前)': kWh_Q_sum_display,
        'でんき料金(切替後)': kWh_NG_sum_display,
        'ガス料金(切替前)': gas_Q_sum_display,
        'ガス料金(切替後)': gas_NG_sum_display,
        'ガスでんき料金(切替前)': kWhgas_Q_sum_display,
        'ガスでんき料金(切替後)': kWhgas_NG_sum_display
    }
    df_total = pd.DataFrame(data_total_NG, index=display_month)

    months = display_month[:-1]  # 最後の要素"合計"を除く
    data1 = kWh_NG_sum_display[:-1]  # 最後の要素"合計"を除く
    data2 = gas_NG_sum_display[:-1]  # 最後の要素"合計"を除く

    data3 = kWh_Q_sum_display[:-1]  # 最後の要素"合計"を除く
    data4 = gas_Q_sum_display[:-1]  # 最後の要素"合計"を除く

    bar_width = 0.35  # バーの幅
    bar_pos1 = np.arange(len(months))  # グループ1のバーの位置
    bar_pos2 = bar_pos1 + bar_width + 0.05  # グループ2のバーの位置

    # グラフの描画
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.bar(bar_pos1, data1, width=bar_width, color='gold', label='電気料金(切替後)')
    ax.bar(bar_pos1, data2, width=bar_width, color='darkcyan', bottom=data1, label='ガス料金(切替後)')
    ax.bar(bar_pos2, data3, width=bar_width, color='gold', label='電気料金(切替前)')
    ax.bar(bar_pos2, data4, width=bar_width, color='darkcyan', bottom=data3, label='ガス料金(切替前)')

    # x軸の設定
    ax.set_xticks(bar_pos1 + bar_width / 2, fontproperties=font_property)
    ax.set_xticklabels(months, fontsize=15, fontproperties=font_property)

    # グラフのタイトルと凡例
    ax.set_title('ガスでんき料金合算比較', fontsize=20, fontproperties=font_property)
    ax.legend(bbox_to_anchor=(1, 1), loc='upper left', prop=font_property)

    # グラフの0の位置に線を引く
    ax.axhline(0, color='grey', linestyle='--', linewidth=1)

    # グラフの表示
    image_path = 'graph.png'
    fig.savefig(image_path)

    return image_path, df_total

