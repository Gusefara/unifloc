﻿"""
Кобзарь О.С. Хабибуллин Р.А.

Модуль для обработки данных скважин, оснащенных УЭЦН (со СУ и шахматки)
"""
import sys
import os
current_path = os.getcwd()
path_to_vba = current_path.replace(r'unifloc\sandbox\uTools', '')
sys.path.append(path_to_vba)
import pandas as pd

import unifloc_vba.description_generated.python_api as python_api

columns_name_dict = {"Pline_atma": "P лин., атм",
                     "pbuf_atma": "P буф., атм",
                     "Pdis_atma": "P выкид ЭЦН, атм",
                     "Pint_atma": "P прием ЭЦН, атм",
                     "pwf_atma": "P прием ЭЦН, атм (P заб. модели)",
                     "qliq_sm3day": "Q ж, м3/сут",
                     "fw_perc": "Обв, %",
                     "tbh_C": "T прием, С ",
                     "twh_C": "T устья, С",
                     "Tsurf_C": "T поверхности, С",
                     "t_dis_C": "T выкид ЭЦН, С",
                     "Tintake_C": "T прием ЭЦН, C",
                     "choke.c_degrad_fr": "К. деградации для штуцера, ед",
                     "Pcas_atma": "P затрубное, атм",
                     "Hdyn_m": "H дин.ур., м",
                     "ESP.power_CS_calc_W": "Акт. мощность на СУ",
                     "ESP.freq_Hz": "F тока, ГЦ",
                     "ESP.I_A": "I, А",
                     "ESP.U_V": "U, В",
                     "ESP.load_fr": "Загрузка двигателя",
                     "ESP.ESPpump.EffiencyESP_d": "КПД ЭЦН, д.ед.",
                     "ESP.KsepTotal_fr": "К. сеп. общий, д.ед.",
                     "ESP.KsepNat_fr": "К. сеп. естесственной, д.ед.",
                     "ESP.KSepGasSep_fr": "К. сеп. газосепаратора",
                     "ESP.c_calibr_head": "К. калибровки по напору - множитель",
                     "ESP.c_calibr_power": "К. калибровки по мощности - множитель",
                     "ESP.c_calibr_rate": "К. калибровки по дебиту - множитель",
                     "ESP.power_motor_nom_W": "Номинальная мощность ПЭД, Вт",
                     "ESP.cable_dU_V": "dU в кабеле, В",
                     "ESP.dPower_GasSep_W": "Мощность, потребляемая газосепаратором",
                     "ESP.dPower_protector_W": "Мощность, потребляемая протектором",
                     "ESP.cable_dPower_W": "Мощность, потребляемая (рассеиваемая) кабелем",
                     "ESP.dPower_transform_W": "Мощность, потребляемая ТМПН",
                     "ESP.dPower_CS_W": "Мощность, потребляемая СУ",
                     "ESP.ESPpump.Powerfluid_Wt": "Мощность, передаваемая жидкости",
                     "ESP.ESPpump.PowerESP_Wt": "Мощность, передаваемая ЭЦН",
                     "ESP.power_shaft_W": "Мощность, передаваемая валу от ПЭД",
                     "ESP.power_motor_W": "Мощность, передаваемая ПЭД",
                     "ESP.cable_power_W": "Мощность, передаваемая кабелю",
                     "ESP.power_CS_teor_calc_W": "Мощность, передаваемая СУ"}



def mark_df_columns(df, mark):
    for i in df.columns:
        df = df.rename(columns={i: i + ' (' + mark + ')' })
    return df

def initial_editing(df, wellname):
    if len(df.columns)==4:
        del df[0]
    df.columns = [0, 1, 2]
    test_str = df[0][0]
    index = test_str.find(wellname)
    str_to_delete = test_str[:index] + wellname + '. '
    df[0] = df[0].str.replace(str_to_delete, "")
    df = df.rename(columns={1: 'Время'})
    df.index = pd.to_datetime(df['Время'])
    del df['Время']
    return df

def extract_df_one_parametr_and_edit(df, list_of_params, number_of_param_in_list):
    extracted_df_one_param = df[df[0] == list_of_params[number_of_param_in_list]]
    extracted_df_one_param = extracted_df_one_param.rename(columns = {2: extracted_df_one_param[0][0]})
    del extracted_df_one_param[0]
    return extracted_df_one_param

def create_edited_df(df):
    parametrs_list = df[0].unique()
    init_one_parametr_df = extract_df_one_parametr_and_edit(df, parametrs_list, 0)
    result = init_one_parametr_df
    for i in range(1, len(parametrs_list)):
        new_one_parametr_df = extract_df_one_parametr_and_edit(df, parametrs_list, i)
        result = result.join(new_one_parametr_df, how = "outer", sort=True)
    return result

def cut_df(df, left_boundary, right_boundary):
    """
    Вырезка из DataFrame временного интервала
    :param df:
    :param left_boundary:
    :param right_boundary:
    :return:
    """
    for start, end in zip(left_boundary, right_boundary):
        df = df[(df.index >= start) & (df.index <= end)]
    return df

def rename_columns_by_dict(df, dict = columns_name_dict):
    """
    Специальное изменение названий столбцов по словарю
    :param df:
    :param dict:
    :return:
    """
    for i in df.columns:
        if i in dict.keys():
            df = df.rename(columns={i: dict[i] })
    return df

def load_calculated_data_from_csv(full_file_name):
    """
    Загрузка результатов расчета модели (адаптации или восстановления) и первичная обработка
    :param full_file_name:
    :return:
    """
    calculated_data = pd.read_csv(full_file_name)
    del calculated_data['Unnamed: 0']
    del calculated_data['Unnamed: 42']
    try:
        del calculated_data['d']
        calculated_data = calculated_data.iloc[1:]
    except:
        pass
    calculated_data.index = pd.to_datetime(calculated_data['Время'])
    del calculated_data['Время']
    calculated_data = rename_columns_by_dict(calculated_data)
    calculated_data['Произведение калибровок H и N'] = calculated_data['К. калибровки по напору - множитель'] * \
                                                       calculated_data['К. калибровки по мощности - множитель']
    calculated_data['Перепад давления в ЭЦН, атм'] = calculated_data['P выкид ЭЦН, атм'] - \
                                                     calculated_data['P прием ЭЦН, атм']
    calculated_data = mark_df_columns(calculated_data, 'Модель')
    return calculated_data

def make_gaps_and_interpolate(df, reverse = False):
    """
    Выкалывание точек и линейная интерполяция. (Восстановление дебитов путем интерполяции)
    :param df:
    :param reverse:
    :return:
    """
    try_check = df.copy()
    try_check['Время'] = try_check.index
    lenth = len(try_check['Время'])
    try_check.index = range(lenth)
    if reverse == True:
        try_check = try_check[(try_check.index) % 2 != 0]
    else:
        try_check = try_check[(try_check.index) % 2 == 0]
    try_check = try_check.interpolate()
    empty = pd.DataFrame({'empty': list(range(lenth))})
    result = empty.join(try_check, how = 'outer')
    result.index = df.index
    result = result.interpolate()
    result['Время'] = result.index
    result.index = result['Время']
    del result['empty']
    del result['Время']
    return result

def load_and_edit_cs_data(cs_data_filename, time_to_resamle, created_input_data_type):
    """
    Загрузка и обработка данных со СУ (не сырых, предварительно обработанных)
    :param cs_data_filename:
    :param time_to_resamle:
    :param created_input_data_type:
    :return:
    """
    edited_data_cs = pd.read_csv(cs_data_filename, parse_dates = True, index_col = 'Время')
    edited_data_cs = edited_data_cs.resample(time_to_resamle).mean()
    edited_data_cs['Выходная частота ПЧ'] = edited_data_cs['Выходная частота ПЧ'].fillna(method='ffill')
    edited_data_cs['Температура на приеме насоса (пласт. жидкость)']  = \
            edited_data_cs['Температура на приеме насоса (пласт. жидкость)'].fillna(method='ffill')
    if created_input_data_type == 0:
        edited_data_cs = edited_data_cs.dropna(subset =['Объемный дебит жидкости'])
    edited_data_cs = edited_data_cs.fillna(method='ffill')
    edited_data_cs['ГФ'] = edited_data_cs['Объемный дебит газа'] / edited_data_cs['Объемный дебит нефти']
    edited_data_cs = mark_df_columns(edited_data_cs, 'СУ')
    return edited_data_cs

def load_and_edit_chess_data(chess_data_filename, time_to_resamle):
    """
    Загрузка и обработка данных с шахматки
    :param chess_data_filename:
    :param time_to_resamle:
    :return:
    """
    chess_data = pd.read_excel(chess_data_filename)
    chess_data.index = pd.to_datetime(chess_data['Дата'], dayfirst = True, format = "%d.%m.%Y", infer_datetime_format=True)
    del chess_data['Дата']
    chess_data.index.name = 'Время'
    chess_data = chess_data[chess_data.columns[5:]]
    chess_data = chess_data.resample(time_to_resamle).last()
    chess_data = chess_data.fillna(method='ffill')
    chess_data = mark_df_columns(chess_data, 'Ш')
    return chess_data

