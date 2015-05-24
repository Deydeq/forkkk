# -*- coding: utf-8 -*-

import pandas as pd
import pubtool
import os

'''
mzh
2015-4-26
'''


def get_data():
    """
    返回值：一个dict，对应的value是DataFrame，以及列名
    """
    excel_file = 'c:\\123.xls'
    template_list = pubtool.readXml(os.getcwd()+'\\template.xml')
    coefficient_dict = pubtool.readCoefficientFromXml(os.getcwd()+'\\coefficient.xml')
    all_sheet_name = []
    for sheet_dict in template_list:
        all_sheet_name.append(sheet_dict['sheetname'])
    all_original_df = pd.read_excel(excel_file, all_sheet_name)

    '''将第一列设为营销人员'''
    sales_column = [template_list[0]['groupby'][0]]
    payment_column = [template_list[0]['groupby'][0]]

    sales_df = []
    payment_df = []
    for sheet_dict in template_list:
        select_fields = []
        if sheet_dict['sum'] is not None:
            select_fields.extend(sheet_dict['sum'])
        if sheet_dict['groupby'] is not None:
            select_fields.extend(sheet_dict['groupby'])

        init_df = all_original_df[sheet_dict['sheetname']]

        """根据where条件过滤"""
        if sheet_dict['where'] is not None:
            column_and_value = sheet_dict['where'].split('=')
            where_df = init_df[init_df[column_and_value[0]] == column_and_value[1]]
            # where_df = init_df.where(init_df[3:3] == u'芯片卡')
        else:
            where_df = init_df

        """筛选所需的列"""
        selected_df = where_df.loc[:, select_fields]

        # data_dict = selected_df.to_dict()
        # print data_dict

        """分组合并"""
        grouped_df = selected_df.groupby(sheet_dict['groupby'])
        if sheet_dict['count'] == 0:
            grouped_df = grouped_df.sum().reset_index()
        else:
            grouped_df = grouped_df.count().reset_index()

        """用作合计"""
        grouped_df[sheet_dict['sheetname']] = 0

        temp_sales_df = None
        temp_payment_df = None
        """state为0表示是销售统计的模板，1表示是中收的模板，2表示是公用的模板。"""
        if sheet_dict['state'] == '0':
            temp_sales_df = grouped_df.copy()
            sales_column.append(sheet_dict['sheetname'])
        elif sheet_dict['state'] == '1':
            temp_payment_df = grouped_df.copy()
            payment_column.append(sheet_dict['sheetname'])
        else:
            temp_sales_df = grouped_df.copy()
            temp_payment_df = grouped_df.copy()
            sales_column.append(sheet_dict['sheetname'])
            payment_column.append(sheet_dict['sheetname'])

        """计算值"""
        """中收"""
        if temp_payment_df is not None:
            if len(sheet_dict['groupby']) == 1:
                for row_index, row in temp_payment_df.iterrows():
                    temp_payment_df.loc[row_index, sheet_dict['sheetname']] = row[sheet_dict['sum']][0] * float(coefficient_dict.get(sheet_dict['sheetname'], 1))
                temp_payment_df = temp_payment_df.loc[:, [sheet_dict['groupby'][0], sheet_dict['sheetname']]]
            elif len(sheet_dict['groupby']) == 2:
                for row_index, row in temp_payment_df.iterrows():
                    temp_payment_df.loc[row_index, sheet_dict['sheetname']] = row[sheet_dict['sum']][0] * float(coefficient_dict.get(row[sheet_dict['groupby'][1]], 1))
                temp_payment_df = temp_payment_df.loc[:, [sheet_dict['groupby'][0], sheet_dict['sheetname']]]
                temp_payment_df = temp_payment_df.groupby(sheet_dict['groupby'][0]).sum().reset_index()
            payment_df.append(temp_payment_df)

        """销售统计"""
        if temp_sales_df is not None:
            if len(sheet_dict['groupby']) == 1:
                for row_index, row in temp_sales_df.iterrows():
                    temp_sales_df.loc[row_index, sheet_dict['sheetname']] = row[sheet_dict['sum']][0]
                temp_sales_df = temp_sales_df.loc[:, [sheet_dict['groupby'][0], sheet_dict['sheetname']]]
            elif len(sheet_dict['groupby']) == 2:
                for row_index, row in temp_sales_df.iterrows():
                    # i think it should row[sheet_dict['sum']], but actual is row[sheet_dict['sum']][0]
                    temp_sales_df.loc[row_index, sheet_dict['sheetname']] = row[sheet_dict['sum']][0] * float(coefficient_dict.get(row[sheet_dict['groupby'][1]], 1))
                temp_sales_df = temp_sales_df.loc[:, [sheet_dict['groupby'][0], sheet_dict['sheetname']]]
                temp_sales_df = temp_sales_df.groupby(sheet_dict['groupby'][0]).sum().reset_index()
            sales_df.append(temp_sales_df)

    # use merge.
    sales_results_df = sales_df.pop()
    for single_df in sales_df:
        sales_results_df = pd.merge(sales_results_df, single_df, how='outer', on=template_list[0]['groupby'][0])

    payment_results_df = payment_df.pop()
    for single_df in payment_df:
        payment_results_df = pd.merge(payment_results_df, single_df, how='outer', on=template_list[0]['groupby'][0])

    sales_dict = sales_results_df.T.fillna(0).to_dict()
    payment_dict = payment_results_df.T.fillna(0).to_dict()

    ret_dict = {
        'sales': sales_dict,
        'payment': payment_dict,
        'sales_column': sales_column,
        'payment_column': payment_column
    }

    return ret_dict


get_data()