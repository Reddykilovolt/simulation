import streamlit as st
import pandas as pd
import main
import os
import time

plan_menu =['九州電力_従量電灯B','九州電力_スマートファミリープラン','九州電力_従量電灯C','九州電力_スマートビジネスプラン','九州電力_低圧動力']
start_menu = ['7', '8', '9', '10', '11', '12']
fuel_menu = ['下降傾向','変化なし','上昇傾向']
class_menu = ['一般用','業務用']

page = st.sidebar.selectbox('Menu select', plan_menu)
time.sleep(0.5)
if page == '九州電力_従量電灯B':
    st.title('料金シミュレーション')
    st.write('九州電力 従量電灯Bとの比較')
    col1, col2 = st.columns(2)
    with col1:
        base_amp = st.number_input('アンペア数(A)', min_value=30, max_value=60, step=10, key='A1')
        one_kWh = st.number_input('供給開始月の電気使用量(kWh)', min_value=100, max_value=2000, value = 300, step=50, key='B1')
        fuel_chenge = st.selectbox('燃料調整費の傾向', fuel_menu, key='C3')
    with col2:
        month = st.selectbox('供給開始月', start_menu, key='A2')
        one_gas = st.number_input('供給開始月のガス使用量(㎥)', min_value=5, max_value=200, value = 20, step=5, key='B2')
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
            '電力量料金': kWh_bill,
            '特別割': set_kWh_bill,
            '再エネ賦課金': re_energy_bill,
            '燃調費': fuel_bill_NG,
            '政府激変緩和': kanwa_bill
        }
        index = display_month
        df_kWh_NG = pd.DataFrame(data_kWh_NG, index=index)
        total_sum_NG = df_kWh_NG.drop('電気使用量[kWh]', axis=1).sum(axis=1)#電気使用量を除く料金関連の足し算
        df_kWh_NG['合計'] = total_sum_NG
        df_kWh_NG = df_kWh_NG.astype(int)
        df_kWh_NG_T = df_kWh_NG.T

        base_bill_Q = main.Q_amp_price_calc(int(base_amp),int(month))
        kWh_bill_Q, set_bill_Q = main.Q_kWh_set_calc(kWh, int(month), page)
        re_energy_bill = main.re_energy_calc(kWh, int(month))
        fuel_bill_Q, fuel_bills_Q = main.reg_fuel_calc(kWh, int(month), fuel_chenge)
        kanwa_bill_Q = main.kanwa_calc(kWh, int(month))
        
        data_kWh_Q = {
            '電気使用量[kWh]': kWh,
            '基本料金': base_bill_Q,
            '電力量料金': kWh_bill_Q,
            '特別割': set_bill_Q,
            '再エネ賦課金': re_energy_bill,
            '燃調費': fuel_bill_Q,
            '政府激変緩和': kanwa_bill_Q
        }
        index = display_month
        df_kWh_Q = pd.DataFrame(data_kWh_Q, index=index)
        total_sum_Q = df_kWh_Q.drop('電気使用量[kWh]', axis=1).sum(axis=1)
        df_kWh_Q['合計'] = total_sum_Q
        df_kWh_Q = df_kWh_Q.astype(int)
        df_kWh_Q_T = df_kWh_Q.T

        gas = main.gas_calc(int(one_gas), int(month))
        gas_bill, set_gas_bill = main.NG_gas_set_calc(gas, gas_class)
        gas_kanwa_bill = main.gas_kanwa_calc(gas, int(month))
        data_gas_NG = {
            'ガス使用量[㎥]': gas,
            'ガス料金': gas_bill,
            '特別割': set_gas_bill,
            '政府激変緩和': gas_kanwa_bill
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

        if sum_comp > 0:            
            st.markdown("---")
            st.write(
                f'2023年{month}月から日本ガスでんきに切り替わると、'
                f'<div style="background-color: #cce5ff; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 20px;">'
                f'<span style="font-size: 32px; color: blue;">{"{:,.0f}".format(sum_comp)}</span> 円オトクになります!</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown("---")
            st.write(
                f'2023年{month}月から日本ガスでんきに切り替わると、'
                f'<div style="background-color: #cce5ff; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 20px;">'
                f'<span style="font-size: 32px; color: red;">{"{:,.0f}".format(-sum_comp)}</span> 円デメリットになります、、</div>',
                unsafe_allow_html=True
            )
        st.write(f'( 試算期間は2023年{month}月から2024年3月 )')
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("■特別割",
                        "ガスセット割適用" if gas_class == "一般用" else "ガスｾｯﾄ割適用なし",
                        f'{"{:,.0f}".format(gas_comp)}円オトク')
            st.metric("■基本料金無料CP",
                        "適用なし" if month == "9"  else "３ヵ月適用",
                        0 if month == "9"  else f'{"{:,.0f}".format(int(base_bill[-2]*3))}円オトク')
        with col2:
            st.metric("■特別割", "電気セット割適用", f'{"{:,.0f}".format(-kWh_set)}円オトク')
            st.metric("■基本料金半額還元",
                        "１ヵ月適用" if month == "7"  else "適用なし",
                        f'{"{:,.0f}".format(int(base_bill[-2]*0.5))}円オトク' if month == "7"  else 0)

        image_path = main.plot_comparison_kWh_graph(df_kWh_NG, df_kWh_Q, page)
        st.image(image_path)# 画像をStreamlitに表示
        os.remove(image_path)# 一時的なファイルなので削除

        st.write("■日本ガス_ファミリープランB_試算結果")
        st.write(df_kWh_NG_T)
        st.write('<p style="font-size: 12px; margin-top: -20px;">※特別割 = 日本ガスセット割(電気)</p>', unsafe_allow_html=True)
        st.write("■九州電力_従量電灯B_試算結果")
        st.write(df_kWh_Q_T)
        st.write('<p style="font-size: 12px; margin-top: -20px;">※特別割 = 九州電力口座振替割引</p>', unsafe_allow_html=True)

        image_path = main.plot_comparison_gas_graph(df_gas_NG)
        st.image(image_path)# 画像をStreamlitに表示
        os.remove(image_path)# 一時的なファイルなので削除

        st.write("■日本ガス_ガス料金(セット割適用)_試算結果" if gas_class == "一般用" else "■日本ガス_ガス料金(セット割適用なし)_試算結果")
        df_gas_NG_T = df_gas_NG_T.applymap(lambda x: "{:,}".format(int(x)) if isinstance(x, str) else x)
        st.write(df_gas_NG_T)
        st.write('<p style="font-size: 12px; margin-top: -20px;">※特別割 = 日本ガスセット割(ガス)</p>', unsafe_allow_html=True)
        
        st.write("■ガスでんき料金合算_試算結果")
        image_path, df_total = main.plot_comparison_total_graph(df_kWh_NG_T, df_kWh_Q_T, df_gas_NG_T, display_month)
        st.image(image_path)# 画像をStreamlitに表示
        os.remove(image_path)# 一時的なファイルなので削除
        df_total_T = df_total.T
        st.write(df_total_T)

        st.write(f'■燃調費の推移({fuel_chenge}想定)')
        main.fuel_vision(fuel_chenge, page)#燃調費グラフ表示

        # Excelファイル名
        output_file = 'output_A_Q.xlsx'

        # Excel Writerオブジェクトを作成
        writer = pd.ExcelWriter(output_file)

        # DataFrameをExcelファイルに書き込む
        df_kWh_NG_T.to_excel(writer, sheet_name='Sheet1', index=False)
        df_kWh_Q_T.to_excel(writer, sheet_name='Sheet2', index=False)
        df_gas_NG_T.to_excel(writer, sheet_name='Sheet3', index=False)
        df_total_T.to_excel(writer, sheet_name='Sheet4', index=False)

        # Excelファイルを保存
        writer.save()

if page == '九州電力_スマートファミリープラン':
    st.title('料金シミュレーション')
    st.write('九州電力 スマートファミリープランとの比較')
    col1, col2 = st.columns(2)
    with col1:
        base_amp = st.number_input('アンペア数(A)', min_value=30, max_value=60, step=10, key='A1')
        one_kWh = st.number_input('供給開始月の電気使用量(kWh)', min_value=100, max_value=2000, value = 300, step=50, key='B1')
        fuel_chenge = st.selectbox('燃料調整費の傾向', fuel_menu, key='C3')
    with col2:
        month = st.selectbox('供給開始月', start_menu, key='A2')
        one_gas = st.number_input('供給開始月のガス使用量(㎥)', min_value=5, max_value=200, value = 20, step=5, key='B2')
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
            '電力量料金': kWh_bill,
            '特別割': set_kWh_bill,
            '再エネ賦課金': re_energy_bill,
            '燃調費': fuel_bill_NG,
            '政府激変緩和': kanwa_bill
        }
        index = display_month
        df_kWh_NG = pd.DataFrame(data_kWh_NG, index=index)
        total_sum = df_kWh_NG.drop('電気使用量[kWh]', axis=1).sum(axis=1)#電気使用量を除く料金関連の足し算
        df_kWh_NG['合計'] = total_sum
        df_kWh_NG = df_kWh_NG.astype(int)
        df_kWh_NG_T = df_kWh_NG.T

        base_bill_Q = main.Q_amp_price_calc(int(base_amp),int(month))
        kWh_bill_Q, set_bill_Q = main.Q_kWh_set_calc(kWh, int(month), page)
        re_energy_bill = main.re_energy_calc(kWh, int(month))
        fuel_bill_Q, fuel_bills_Q = main.fuel_calc(kWh, int(month), fuel_chenge)
        kanwa_bill_Q = main.kanwa_calc(kWh, int(month))
        
        data_kWh_Q = {
            '電気使用量[kWh]': kWh,
            '基本料金': base_bill_Q,
            '電力量料金': kWh_bill_Q,
            '特別割': set_bill_Q,
            '再エネ賦課金': re_energy_bill,
            '燃調費': fuel_bill_Q,
            '政府激変緩和': kanwa_bill_Q
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
            '政府激変緩和': gas_kanwa_bill
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

        if sum_comp > 0:            
            st.markdown("---")
            st.write(
                f'2023年{month}月から日本ガスでんきに切り替わると、'
                f'<div style="background-color: #cce5ff; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 20px;">'
                f'<span style="font-size: 32px; color: blue;">{"{:,.0f}".format(sum_comp)}</span> 円オトクになります!</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown("---")
            st.write(
                f'2023年{month}月から日本ガスでんきに切り替わると、'
                f'<div style="background-color: #cce5ff; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 20px;">'
                f'<span style="font-size: 32px; color: red;">{"{:,.0f}".format(-sum_comp)}</span> 円デメリットになります、、</div>',
                unsafe_allow_html=True
            )

        st.write(f'( 試算期間は2023年{month}月から2024年3月 )')
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("■特別割",
                        "ガスセット割適用" if gas_class == "一般用" else "ガスｾｯﾄ割適用なし",
                        f'{"{:,.0f}".format(gas_comp)}円オトク')
            st.metric("■基本料金無料CP",
                        "適用なし" if month == "9"  else "３ヵ月適用",
                        0 if month == "9"  else f'{"{:,.0f}".format(int(base_bill[-2]*3))}円オトク')
        with col2:
            st.metric("■特別割", "電気セット割適用", f'{"{:,.0f}".format(-kWh_set)}円オトク')
            st.metric("■基本料金半額還元",
                        "１ヵ月適用" if month == "7"  else "適用なし",
                        f'{"{:,.0f}".format(int(base_bill[-2]*0.5))}円オトク' if month == "7"  else 0)

        image_path = main.plot_comparison_kWh_graph(df_kWh_NG, df_kWh_Q, page)
        st.image(image_path)# 画像をStreamlitに表示
        os.remove(image_path)# 一時的なファイルなので削除

        st.write("■日本ガス_ファミリープラン_試算結果")
        st.write(df_kWh_NG_T)
        st.write('<p style="font-size: 12px; margin-top: -20px;">※特別割 = 日本ガスセット割(電気)</p>', unsafe_allow_html=True)
        st.write("■九州電力_スマートファミリープラン_試算結果")
        st.write(df_kWh_Q_T)
        st.write('<p style="font-size: 12px; margin-top: -20px;">※特別割 = 九州電力２年割契約割</p>', unsafe_allow_html=True)

        image_path = main.plot_comparison_gas_graph(df_gas_NG)
        st.image(image_path)# 画像をStreamlitに表示
        os.remove(image_path)# 一時的なファイルなので削除

        st.write("■日本ガス_ガス料金(セット割適用)_試算結果" if gas_class == "一般用" else "■日本ガス_ガス料金(セット割適用なし)_試算結果")
        st.write(df_gas_NG_T)
        st.write('<p style="font-size: 12px; margin-top: -20px;">※特別割 = 日本ガスセット割(ガス)</p>', unsafe_allow_html=True)
        
        st.write("■ガスでんき料金合算_試算結果")
        image_path, df_total = main.plot_comparison_total_graph(df_kWh_NG_T, df_kWh_Q_T, df_gas_NG_T, display_month)
        st.image(image_path)# 画像をStreamlitに表示
        os.remove(image_path)# 一時的なファイルなので削除
        df_total_T = df_total.T
        st.write(df_total_T)

        st.write(f'■燃調費の推移({fuel_chenge}想定)')
        main.fuel_vision(fuel_chenge, page)#燃調費グラフ表示

        # Excelファイル名
        output_file = 'output_A_Q.xlsx'

        # Excel Writerオブジェクトを作成
        writer = pd.ExcelWriter(output_file)

        # DataFrameをExcelファイルに書き込む
        df_kWh_NG_T.to_excel(writer, sheet_name='Sheet1', index=False)
        df_kWh_Q_T.to_excel(writer, sheet_name='Sheet2', index=False)
        df_gas_NG_T.to_excel(writer, sheet_name='Sheet3', index=False)
        df_total_T.to_excel(writer, sheet_name='Sheet4', index=False)

        # Excelファイルを保存
        writer.save()

if page == '九州電力_従量電灯C':
    st.title('料金シミュレーション')
    st.write('九州電力 従量電灯Cとの比較')
    col1, col2 = st.columns(2)
    with col1:
        base_amp = st.number_input('契約容量(kVA)', min_value=6, max_value=50, value = 12, step=1, key='A1')
        one_kWh = st.number_input('供給開始月の電気使用量(kWh)', min_value=50, max_value=2000, value = 300, step=50, key='B1')
        fuel_chenge = st.selectbox('燃料調整費の傾向', fuel_menu, key='C3')
    with col2:
        month = st.selectbox('供給開始月', start_menu, key='A2')
        one_gas = st.number_input('供給開始月のガス使用量(㎥)', min_value=5, max_value=200, value = 20, step=5, key='B2')
        gas_class = st.selectbox('ガス用途', class_menu, key='C3')

    submit_button = st.button('実行')

    if submit_button:
        kWh, display_month = main.kWh_calc(int(one_kWh), int(month))
        base_bill = main.NG_kVA_price_calc(int(base_amp),int(month))
        kWh_bill, set_kWh_bill = main.NG_kVA_set_calc(kWh)
        re_energy_bill = main.re_energy_calc(kWh, int(month))
        fuel_bill_NG, fuel_bills_NG = main.fuel_calc(kWh, int(month), fuel_chenge)
        kanwa_bill = main.kanwa_calc(kWh, int(month))
        
        data_kWh_NG = {
            '電気使用量[kWh]': kWh,
            '基本料金': base_bill,
            '電力量料金': kWh_bill,
            '特別割': set_kWh_bill,
            '再エネ賦課金': re_energy_bill,
            '燃調費': fuel_bill_NG,
            '政府激変緩和': kanwa_bill
        }
        index = display_month

        df_kWh_NG = pd.DataFrame(data_kWh_NG, index=index)
        total_sum = df_kWh_NG.drop('電気使用量[kWh]', axis=1).sum(axis=1)#電気使用量を除く料金関連の足し算
        df_kWh_NG['合計'] = total_sum
        df_kWh_NG = df_kWh_NG.astype(int)
        df_kWh_NG_T = df_kWh_NG.T

        base_bill_Q = main.Q_kVA_price_calc(int(base_amp),int(month))
        kWh_bill_Q, set_bill_Q = main.Q_kVA_set_calc(kWh, int(month), page)
        re_energy_bill = main.re_energy_calc(kWh, int(month))
        fuel_bill_Q, fuel_bills_Q = main.reg_fuel_calc(kWh, int(month), fuel_chenge)
        kanwa_bill_Q = main.kanwa_calc(kWh, int(month))
        
        data_kWh_Q = {
            '電気使用量[kWh]': kWh,
            '基本料金': base_bill_Q,
            '電力量料金': kWh_bill_Q,
            '特別割': set_bill_Q,
            '再エネ賦課金': re_energy_bill,
            '燃調費': fuel_bill_Q,
            '政府激変緩和': kanwa_bill_Q
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
            '政府激変緩和': gas_kanwa_bill
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

        if sum_comp > 0:            
            st.markdown("---")
            st.write(
                f'2023年{month}月から日本ガスでんきに切り替わると、'
                f'<div style="background-color: #cce5ff; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 20px;">'
                f'<span style="font-size: 32px; color: blue;">{"{:,.0f}".format(sum_comp)}</span> 円オトクになります!</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown("---")
            st.write(
                f'2023年{month}月から日本ガスでんきに切り替わると、'
                f'<div style="background-color: #cce5ff; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 20px;">'
                f'<span style="font-size: 32px; color: red;">{"{:,.0f}".format(-sum_comp)}</span> 円デメリットになります、、</div>',
                unsafe_allow_html=True
            )

        st.write(f'( 試算期間は2023年{month}月から2024年3月 )')
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("■特別割",
                        "ガスセット割適用" if gas_class == "一般用" else "ガスｾｯﾄ割適用なし",
                        f'{"{:,.0f}".format(gas_comp)}円オトク')
            st.metric("■基本料金無料CP",
                        "適用なし" if month == "9"  else "３ヵ月適用",
                        0 if month == "9"  else f'{"{:,.0f}".format(int(base_bill[-2]*3))}円オトク')
        with col2:
            st.metric("■特別割", "電気セット割適用", f'{"{:,.0f}".format(-kWh_set)}円オトク')
            st.metric("■基本料金半額還元",
                        "１ヵ月適用" if month == "7"  else "適用なし",
                        f'{"{:,.0f}".format(int(base_bill[-2]*0.5))}円オトク' if month == "7"  else 0)

        image_path = main.plot_comparison_kWh_graph(df_kWh_NG, df_kWh_Q, page)
        st.image(image_path)# 画像をStreamlitに表示
        os.remove(image_path)# 一時的なファイルなので削除

        st.write("■日本ガス_ビジネスプランC_試算結果")
        st.write(df_kWh_NG_T)
        st.write('<p style="font-size: 12px; margin-top: -20px;">※特別割 = 日本ガスセット割(電気)</p>', unsafe_allow_html=True)
        st.write("■九州電力_従量電灯C_試算結果")
        st.write(df_kWh_Q_T)
        st.write('<p style="font-size: 12px; margin-top: -20px;">※特別割 = 九州電力口座振替割</p>', unsafe_allow_html=True)

        image_path = main.plot_comparison_gas_graph(df_gas_NG)
        st.image(image_path)# 画像をStreamlitに表示
        os.remove(image_path)# 一時的なファイルなので削除

        st.write("■日本ガス_ガス料金(セット割適用)_試算結果" if gas_class == "一般用" else "■日本ガス_ガス料金(セット割適用なし)_試算結果")
        st.write(df_gas_NG_T)
        st.write('<p style="font-size: 12px; margin-top: -20px;">※特別割 = 日本ガスセット割(ガス)</p>', unsafe_allow_html=True)
        
        st.write("■ガスでんき料金合算_試算結果")
        image_path, df_total = main.plot_comparison_total_graph(df_kWh_NG_T, df_kWh_Q_T, df_gas_NG_T, display_month)
        st.image(image_path)# 画像をStreamlitに表示
        os.remove(image_path)# 一時的なファイルなので削除
        df_total_T = df_total.T
        st.write(df_total_T)

        st.write(f'■燃調費の推移({fuel_chenge}想定)')
        main.fuel_vision(fuel_chenge, page)#燃調費グラフ表示

        # # Excelファイル名
        # output_file = 'output_kVA_NG.xlsx'

        # # Excel Writerオブジェクトを作成
        # writer = pd.ExcelWriter(output_file)

        # # DataFrameをExcelファイルに書き込む
        # df_kWh_NG_T.to_excel(writer, sheet_name='Sheet1', index=False)
        # df_kWh_Q_T.to_excel(writer, sheet_name='Sheet2', index=False)
        # df_gas_NG_T.to_excel(writer, sheet_name='Sheet3', index=False)
        # df_total_T.to_excel(writer, sheet_name='Sheet4', index=False)

        # # Excelファイルを保存
        # writer.save()

if page == '九州電力_スマートビジネスプラン':
    st.title('料金シミュレーション')
    st.write('九州電力 スマートビジネスプランとの比較')
    col1, col2 = st.columns(2)
    with col1:
        base_amp = st.number_input('契約容量(kVA)', min_value=6, max_value=50, value = 12, step=1, key='A1')
        one_kWh = st.number_input('供給開始月の電気使用量(kWh)', min_value=50, max_value=2000, value = 300, step=50, key='B1')
        fuel_chenge = st.selectbox('燃料調整費の傾向', fuel_menu, key='C3')
    with col2:
        month = st.selectbox('供給開始月', start_menu, key='A2')
        one_gas = st.number_input('供給開始月のガス使用量(㎥)', min_value=5, max_value=200, value = 20, step=5, key='B2')
        gas_class = st.selectbox('ガス用途', class_menu, key='C3')

    submit_button = st.button('実行')

    if submit_button:
        kWh, display_month = main.kWh_calc(int(one_kWh), int(month))
        base_bill = main.NG_kVA_price_calc(int(base_amp),int(month))
        kWh_bill, set_kWh_bill = main.NG_kVA_set_calc(kWh)
        re_energy_bill = main.re_energy_calc(kWh, int(month))
        fuel_bill_NG, fuel_bills_NG = main.fuel_calc(kWh, int(month), fuel_chenge)
        kanwa_bill = main.kanwa_calc(kWh, int(month))
        
        data_kWh_NG = {
            '電気使用量[kWh]': kWh,
            '基本料金': base_bill,
            '電力量料金': kWh_bill,
            '特別割': set_kWh_bill,
            '再エネ賦課金': re_energy_bill,
            '燃調費': fuel_bill_NG,
            '政府激変緩和': kanwa_bill
        }
        index = display_month

        df_kWh_NG = pd.DataFrame(data_kWh_NG, index=index)
        total_sum = df_kWh_NG.drop('電気使用量[kWh]', axis=1).sum(axis=1)#電気使用量を除く料金関連の足し算
        df_kWh_NG['合計'] = total_sum
        df_kWh_NG = df_kWh_NG.astype(int)
        df_kWh_NG_T = df_kWh_NG.T

        base_bill_Q = main.Q_kVA_price_calc(int(base_amp),int(month))
        kWh_bill_Q, set_bill_Q = main.Q_kVA_set_calc(kWh, int(month), page)
        re_energy_bill = main.re_energy_calc(kWh, int(month))
        fuel_bill_Q, fuel_bills_Q = main.fuel_calc(kWh, int(month), fuel_chenge)
        kanwa_bill_Q = main.kanwa_calc(kWh, int(month))
        
        data_kWh_Q = {
            '電気使用量[kWh]': kWh,
            '基本料金': base_bill_Q,
            '電力量料金': kWh_bill_Q,
            '特別割': set_bill_Q,
            '再エネ賦課金': re_energy_bill,
            '燃調費': fuel_bill_Q,
            '政府激変緩和': kanwa_bill_Q
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
            '政府激変緩和': gas_kanwa_bill
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

        if sum_comp > 0:            
            st.markdown("---")
            st.write(
                f'2023年{month}月から日本ガスでんきに切り替わると、'
                f'<div style="background-color: #cce5ff; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 20px;">'
                f'<span style="font-size: 32px; color: blue;">{"{:,.0f}".format(sum_comp)}</span> 円オトクになります!</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown("---")
            st.write(
                f'2023年{month}月から日本ガスでんきに切り替わると、'
                f'<div style="background-color: #cce5ff; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 20px;">'
                f'<span style="font-size: 32px; color: red;">{"{:,.0f}".format(-sum_comp)}</span> 円デメリットになります、、</div>',
                unsafe_allow_html=True
            )

        st.write(f'( 試算期間は2023年{month}月から2024年3月 )')
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("■特別割",
                        "ガスセット割適用" if gas_class == "一般用" else "ガスｾｯﾄ割適用なし",
                        f'{"{:,.0f}".format(gas_comp)}円オトク')
            st.metric("■基本料金無料CP",
                        "適用なし" if month == "9"  else "３ヵ月適用",
                        0 if month == "9"  else f'{"{:,.0f}".format(int(base_bill[-2]*3))}円オトク')
        with col2:
            st.metric("■特別割", "電気セット割適用", f'{"{:,.0f}".format(-kWh_set)}円オトク')
            st.metric("■基本料金半額還元",
                        "１ヵ月適用" if month == "7"  else "適用なし",
                        f'{"{:,.0f}".format(int(base_bill[-2]*0.5))}円オトク' if month == "7"  else 0)

        image_path = main.plot_comparison_kWh_graph(df_kWh_NG, df_kWh_Q, page)
        st.image(image_path)# 画像をStreamlitに表示
        os.remove(image_path)# 一時的なファイルなので削除

        st.write("■日本ガス_ビジネスプランC_試算結果")
        st.write(df_kWh_NG_T)
        st.write('<p style="font-size: 12px; margin-top: -20px;">※特別割 = 日本ガスセット割(電気)</p>', unsafe_allow_html=True)
        st.write("■九州電力_スマートビジネスプラン_試算結果")
        st.write(df_kWh_Q_T)
        st.write('<p style="font-size: 12px; margin-top: -20px;">※特別割なし</p>', unsafe_allow_html=True)

        image_path = main.plot_comparison_gas_graph(df_gas_NG)
        st.image(image_path)# 画像をStreamlitに表示
        os.remove(image_path)# 一時的なファイルなので削除

        st.write("■日本ガス_ガス料金(セット割適用)_試算結果" if gas_class == "一般用" else "■日本ガス_ガス料金(セット割適用なし)_試算結果")
        st.write(df_gas_NG_T)
        st.write('<p style="font-size: 12px; margin-top: -20px;">※特別割 = 日本ガスセット割(ガス)</p>', unsafe_allow_html=True)
        
        st.write("■ガスでんき料金合算_試算結果")
        image_path, df_total = main.plot_comparison_total_graph(df_kWh_NG_T, df_kWh_Q_T, df_gas_NG_T, display_month)
        st.image(image_path)# 画像をStreamlitに表示
        os.remove(image_path)# 一時的なファイルなので削除
        df_total_T = df_total.T
        st.write(df_total_T)

        st.write(f'■燃調費の推移({fuel_chenge}想定)')
        main.fuel_vision(fuel_chenge, page)#燃調費グラフ表示
        
        # # Excelファイル名
        # output_file = 'output_kVA_Q.xlsx'

        # # Excel Writerオブジェクトを作成
        # writer = pd.ExcelWriter(output_file)

        # # DataFrameをExcelファイルに書き込む
        # df_kWh_NG_T.to_excel(writer, sheet_name='Sheet1', index=False)
        # df_kWh_Q_T.to_excel(writer, sheet_name='Sheet2', index=False)
        # df_gas_NG_T.to_excel(writer, sheet_name='Sheet3', index=False)
        # df_total_T.to_excel(writer, sheet_name='Sheet4', index=False)

        # # Excelファイルを保存
        # writer.save()

if page == '九州電力_低圧動力':
    st.title('料金シミュレーション')
    st.write('九州電力 低圧動力との比較')
    col1, col2 = st.columns(2)
    with col1:
        base_amp = st.number_input('契約容量(kW)', min_value=1, max_value=50, value = 5, step=1, key='A1')
        one_kWh = st.number_input('供給開始月の電気使用量(kWh)', min_value=100, max_value=2000, value = 300, step=50, key='B1')

    with col2:
        month = st.selectbox('供給開始月', start_menu, key='A2')
        fuel_chenge = st.selectbox('燃料調整費の傾向', fuel_menu, key='B2')

    submit_button = st.button('実行')

    if submit_button:
        kWh, display_month = main.kWh_calc(int(one_kWh), int(month))
        base_bill = main.NG_kW_price_calc(int(base_amp),int(month))
        kWh_bill = main.NG_kW_set_calc(kWh)
        re_energy_bill = main.re_energy_calc(kWh, int(month))
        fuel_bill_NG, fuel_bills_NG = main.fuel_calc(kWh, int(month), fuel_chenge)
        kanwa_bill = main.kanwa_calc(kWh, int(month))
        
        data_kWh_NG = {
            '電気使用量[kWh]': kWh,
            '基本料金': base_bill,
            '電力量料金': kWh_bill,
            '再エネ賦課金': re_energy_bill,
            '燃調費': fuel_bill_NG,
            '政府激変緩和': kanwa_bill
        }
        index = display_month
        df_kWh_NG = pd.DataFrame(data_kWh_NG, index=index)
        total_sum = df_kWh_NG.drop('電気使用量[kWh]', axis=1).sum(axis=1)#電気使用量を除く料金関連の足し算
        df_kWh_NG['合計'] = total_sum
        df_kWh_NG = df_kWh_NG.astype(int)
        df_kWh_NG_T = df_kWh_NG.T

        base_bill_Q = main.Q_kW_price_calc(int(base_amp),int(month))
        kWh_bill_Q = main.Q_kW_set_calc(kWh)
        re_energy_bill = main.re_energy_calc(kWh, int(month))
        fuel_bill_Q, fuel_bills_Q = main.reg_fuel_calc(kWh, int(month), fuel_chenge)
        kanwa_bill_Q = main.kanwa_calc(kWh, int(month))
        
        data_kWh_Q = {
            '電気使用量[kWh]': kWh,
            '基本料金': base_bill_Q,
            '電力量料金': kWh_bill_Q,
            '再エネ賦課金': re_energy_bill,
            '燃調費': fuel_bill_Q,
            '政府激変緩和': kanwa_bill_Q
        }
        index = display_month
        df_kWh_Q = pd.DataFrame(data_kWh_Q, index=index)
        total_sum = df_kWh_Q.drop('電気使用量[kWh]', axis=1).sum(axis=1)
        df_kWh_Q['合計'] = total_sum
        df_kWh_Q = df_kWh_Q.astype(int)
        df_kWh_Q_T = df_kWh_Q.T

        kWh_NG_sum = df_kWh_NG_T.loc['合計', '合計']
        kWh_Q_sum = df_kWh_Q_T.loc['合計', '合計']
        kWh_comp = kWh_Q_sum - kWh_NG_sum

        sum_comp = kWh_comp

        if sum_comp > 0:            
            st.markdown("---")
            st.write(
                f'2023年{month}月から日本ガスでんきに切り替わると、'
                f'<div style="background-color: #cce5ff; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 20px;">'
                f'<span style="font-size: 32px; color: blue;">{"{:,.0f}".format(sum_comp)}</span> 円オトクになります!</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown("---")
            st.write(
                f'2023年{month}月から日本ガスでんきに切り替わると、'
                f'<div style="background-color: #cce5ff; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 20px;">'
                f'<span style="font-size: 32px; color: red;">{"{:,.0f}".format(-sum_comp)}</span> 円デメリットになります、、</div>',
                unsafe_allow_html=True
            )

        st.write(f'( 試算期間は2023年{month}月から2024年3月 )')
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("■特別割","ガスｾｯﾄ割適用なし", 0)
            st.metric("■基本料金無料CP",
                        "適用なし", 0)
        with col2:
            st.metric("■特別割", "電気ｾｯﾄ割適用なし", 0)
            if month in ["7", "8", "9", "10"]:
                tekiyo_month = 11 - int(month) #基本料金半額CPを何カ月適用か表示
                st.metric("■基本料金半額還元", f"{tekiyo_month}ヵ月適用", f'{"{:,.0f}".format(int(base_bill[0] * tekiyo_month))}円オトク')
            else:
                st.metric("■基本料金半額還元", "適用なし", 0)

        image_path = main.plot_comparison_kWh_graph(df_kWh_NG, df_kWh_Q, page)
        st.image(image_path)# 画像をStreamlitに表示
        os.remove(image_path)# 一時的なファイルなので削除

        st.write("■日本ガス_低圧電力_試算結果")
        st.write(df_kWh_NG_T)
        st.write("■九州電力_低圧電力_試算結果")
        st.write(df_kWh_Q_T)

        st.write(f'■燃調費の推移({fuel_chenge}想定)')
        main.fuel_vision(fuel_chenge, page)#燃調費グラフ表示

        # # Excelファイル名
        # output_file = 'output_kW.xlsx'

        # # Excel Writerオブジェクトを作成
        # writer = pd.ExcelWriter(output_file)

        # # DataFrameをExcelファイルに書き込む
        # df_kWh_NG_T.to_excel(writer, sheet_name='Sheet1', index=False)
        # df_kWh_Q_T.to_excel(writer, sheet_name='Sheet2', index=False)

        # # Excelファイルを保存
        # writer.save()

