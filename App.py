import streamlit as st
import pandas as pd
import main
import plotly.graph_objects as go
import os

start_menu = ['7', '8', '9', '10', '11', '12']
fuel_menu = ['下降傾向','変化なし','上昇傾向']
class_menu = ['一般用','業務用']
page = st.sidebar.selectbox('Menu select', ['九州電力_従量電灯B', '九州電力_従量電灯C', '九州電力_スマートファミリープランB', '九州電力_スマートビジネスプランC'])
if page == '九州電力_従量電灯B':
    st.title('料金シミュレーション')
    st.write('九州電力 従量電灯Bとの比較')
    col1, col2 = st.columns(2)
    with col1:
        base_amp = st.number_input('アンペア数(A)', min_value=30, max_value=60, step=10, key='A1')
        one_kWh = st.number_input('供給開始月の電気使用量(kWh)', min_value=100, max_value=2000, step=50, key='B1')
        fuel_chenge = st.selectbox('燃料調整費の傾向', fuel_menu, key='C3')
    with col2:
        month = st.selectbox('供給開始月', start_menu, key='A2')
        one_gas = st.number_input('供給開始月のガス使用量(㎥)', min_value=10, max_value=200, step=5, key='B2')
        gas_class = st.selectbox('ガス用途', class_menu, key='C3')

    submit_button = st.button('実行')

    if submit_button:
        kWh, display_month = main.kWh_calc(int(one_kWh), int(month))
        base_bill = main.NG_amp_price_calc(int(base_amp),int(month))
        kWh_bill, set_kWh_bill = main.NG_kWh_set_calc(kWh, int(base_amp))
        re_energy_bill = main.re_energy_calc(kWh, int(month))
        fuel_bill_NG, fuel_bills_NG = main.fuel_calc(kWh, int(month), fuel_chenge)
        kanwa_bill = main.kanwa_calc(kWh, int(month))
        
        data_kWh_NG = {
            '電気使用量[kWh]': kWh,
            '基本料金': base_bill,
            '従量料金': kWh_bill,
            '特別割': set_kWh_bill,
            '再エネ賦課金': re_energy_bill,
            '燃調費': fuel_bill_NG,
            '激変緩和': kanwa_bill
        }
        index = display_month
        df_kWh_NG = pd.DataFrame(data_kWh_NG, index=index)
        total_sum = df_kWh_NG.drop('電気使用量[kWh]', axis=1).sum(axis=1)#電気使用量を除く料金関連の足し算
        df_kWh_NG['合計'] = total_sum
        df_kWh_NG = df_kWh_NG.astype(int)
        df_kWh_NG_T = df_kWh_NG.T

        base_bill = main.Q_amp_price_calc(int(base_amp),int(month))
        kWh_bill, set_kWh_bill = main.Q_kWh_set_calc(kWh, int(month))
        re_energy_bill = main.re_energy_calc(kWh, int(month))
        fuel_bill_Q, fuel_bills_Q = main.reg_fuel_calc(kWh, int(month), fuel_chenge)
        kanwa_bill = main.kanwa_calc(kWh, int(month))
        
        data_kWh_Q = {
            '電気使用量[kWh]': kWh,
            '基本料金': base_bill,
            '従量料金': kWh_bill,
            '特別割': set_kWh_bill,
            '再エネ賦課金': re_energy_bill,
            '燃調費': fuel_bill_Q,
            '激変緩和': kanwa_bill
        }
        index = display_month
        df_kWh_Q = pd.DataFrame(data_kWh_Q, index=index)
        total_sum = df_kWh_Q.drop('電気使用量[kWh]', axis=1).sum(axis=1)
        df_kWh_Q['合計'] = total_sum
        df_kWh_Q = df_kWh_Q.astype(int)
        df_kWh_Q_T = df_kWh_Q.T

        gas = main.gas_calc(int(one_gas), int(month))
        gas_bill, set_gas_bill = main.NG_gas_set_calc(gas, gas_class)
        gas_kanwa_bill = main.gas_kanwa_calc(gas, int(month))
        data_gas_NG = {
            'ガス使用量[㎥]': gas,
            'ガス料金': gas_bill,
            '特別割': set_gas_bill,
            '激変緩和': gas_kanwa_bill
        }
        index = display_month
        df_gas_NG = pd.DataFrame(data_gas_NG, index=index)
        total_sum = df_gas_NG.drop('ガス使用量[㎥]', axis=1).sum(axis=1)
        df_gas_NG['合計'] = total_sum
        df_gas_NG = df_gas_NG.astype(int)
        df_gas_NG_T = df_gas_NG.T
        
        kWh_NG_sum = df_kWh_NG_T.loc['合計', '合計']
        kWh_Q_sum = df_kWh_Q_T.loc['合計', '合計']
        kWh_comp = kWh_Q_sum - kWh_NG_sum

        kWh_set = df_kWh_NG_T.loc['特別割', '合計']
        
        gas_NG_sum_before = df_gas_NG_T.loc['合計', '合計'] - df_gas_NG_T.loc['特別割', '合計']
        gas_NG_sum_after = df_gas_NG_T.loc['合計', '合計']
        gas_comp = gas_NG_sum_before - gas_NG_sum_after
        sum_comp = kWh_comp + gas_comp

        st.markdown("---")
        st.write(
            f'2023年{month}月から日本ガスでんきに切り替わると、'
            f'<div style="background-color: #cce5ff; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 20px;">'
            #f'<span style="font-size: 32px; color: blue;">{"{:,.0f}".format(sum_comp)}</span> 円オトクになります!<span style="font-size: 14px; color: black;">  ( 試算期間は2023年{month}月から2024年3月 )</span></div>',
            f'<span style="font-size: 32px; color: blue;">{"{:,.0f}".format(sum_comp)}</span> 円オトクになります!</div>',
            unsafe_allow_html=True
        )
        st.write(f'( 試算期間は2023年{month}月から2024年3月 )')
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("■特別割", "ガスセット割適用", f'{"{:,.0f}".format(gas_comp)}円オトク')
            st.metric("■基本料金無料CP",
                        "適用なし" if month == "9"  else "３ヵ月適用",
                        0 if month == "9"  else f'{"{:,.0f}".format(int(base_bill[-2]*3))}円オトク')
        with col2:
            st.metric("■特別割", "電気セット割適用", f'{"{:,.0f}".format(-kWh_set)}円オトク')
            st.metric("■基本料金半額還元",
                        "１ヵ月適用" if month == "7"  else "適用なし",
                        f'{"{:,.0f}".format(int(base_bill[-2]*0.5))}円オトク' if month == "7"  else 0)

        image_path = main.plot_comparison_kWh_graph(df_kWh_NG, df_kWh_Q)
        # 画像をStreamlitに表示
        st.image(image_path)
        # 一時的なファイルなので削除
        os.remove(image_path)

        st.write("■日本ガス_ファミリープランB_試算結果")
        st.table(df_kWh_NG_T)
        st.write("■九州電力_従量電灯B_試算結果")
        st.table(df_kWh_Q_T)

        image_path = main.plot_comparison_gas_graph(df_gas_NG)
        # 画像をStreamlitに表示
        st.image(image_path)
        # 一時的なファイルなので削除
        os.remove(image_path)

        st.write("■日本ガス_ガスセット割_試算結果")
        st.table(df_gas_NG_T)

        x_1,x_2, fuel_bills_Q_1, fuel_bills_Q_2, fuel_bills_NG_1, fuel_bills_NG_2 = main.fuel_vision(fuel_chenge)
        # グラフの設定
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_1, y=fuel_bills_NG_1, mode='lines', line=dict(color='blue'), name='日本ガス_過去実績'))
        fig.add_trace(go.Scatter(x=x_2, y=fuel_bills_NG_2, mode='lines', line=dict(color='blue',dash='dot'), name='日本ガス_今後の推移予測'))
        fig.add_trace(go.Scatter(x=x_1, y=fuel_bills_Q_1, mode='lines', line=dict(color='red'), name='九州電力_過去実績'))
        fig.add_trace(go.Scatter(x=x_2, y=fuel_bills_Q_2, mode='lines', line=dict(color='red',dash='dot'), name='九州電力_今後の推移予測'))
        fig.update_layout(xaxis_title='月', yaxis_title='燃調費[円/kWh]')
        # グラフを表示
        st.write('■燃調費の推移')
        st.plotly_chart(fig)
        



