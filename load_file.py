import openpyxl
import xlrd


def read_from_xls(file_path):
    '''
    针对97-03以xls结尾的文件
    :param file_path:
    :return:
    '''
    workbook = xlrd.open_workbook(file_path)
    worksheet = workbook.sheet_by_index(0)
    indexs = worksheet.col_values(0)
    return None


def read_from_xlsx(file_path,prefixs):
    workbook = openpyxl.load_workbook(file_path)
    worksheet = workbook.worksheets[0]
    data = []
    # row from 2 start,id 1 is title
    for i in range(2, worksheet.max_row + 1):
        try:
            data.append(
                [worksheet[f'{prefix}{i}'].value for prefix in prefixs]
            )
        except Exception as e:
            print(f'line {i} is error')
            continue
    return data

