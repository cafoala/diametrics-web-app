from datetime import datetime
import pandas as pd


def try_parsing_date(text):
    text = str(text)
    formats = ("%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%d/%m/%Y %H:%M",
               "%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S",
               "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M")  # add dot format
    for fmt in formats:
        try:
            datetime.strptime(text, fmt)
            return True
        except ValueError:
            pass
    return False


def test_col(col):
    datetime_bool = col.apply(lambda x: try_parsing_date(x))
    if datetime_bool.all():
        return 'dt'
    try:
        print(col.tail())
        col_num = pd.to_numeric(col).dropna()
        print('NUM')
        if ((col_num < 28) & (col_num > 2)).all():
            print('glc_uk')
            return 'glc_uk'
        elif ((col_num < 505) & (col_num > 36)).all():
            return 'glc_us'
        else:
            return 'unknown'

    except Exception:
        print('not num')
        return 'unknown'


def find_header(df):
    dropped = df.dropna()
    dropped.columns = ['time', 'glc']
    count = 0
    for i, row in dropped.iterrows():
        is_date = try_parsing_date(row['time'])
        if not is_date:
            count += 1
            continue
        try:
            float(row['glc'])
            break
        except Exception:
            count += 1
    if count == dropped.shape[0]:
        raise Exception('Problem with input data')
    return dropped.iloc[count:]


def preprocess_data(df, id_colname=None):
    print(df.head())
    max_rows = df.count().max()
    cols_to_keep = df.count()[df.count() > max_rows * 0.7].index
    footer_rows = df[cols_to_keep].iloc[int(-max_rows * 0.8):]
    print(cols_to_keep)
    col_type_dict = {'dt': [], 'glc_uk': [], 'glc_us': []}
    for i in cols_to_keep:
        print(i)
        col_type = test_col(footer_rows[i])
        if col_type != 'unknown':
            col_type_dict[col_type].append(i)
    print(col_type_dict)
    if (len(col_type_dict['dt']) > 0) & (len(col_type_dict['glc_uk']) > 0):
        sub_frame = df[[col_type_dict['dt'][0], col_type_dict['glc_uk'][0]]]
        df_processed = find_header(sub_frame)
    elif (len(col_type_dict['dt']) > 0) & (len(col_type_dict['glc_us']) > 0):
        sub_frame = df[col_type_dict['dt'][0], col_type_dict['glc_us'][0]]
        df_processed = find_header(sub_frame)
        try:
            df_processed['time'] = df_processed['time'] / 0.0555
        except Exception:
            print('Problem with input data')
    else:
        raise Exception('Can\'t identify datetime and/or glucose columns')
    if id_colname is not None:
        df_processed = df_processed.join(df[id_colname], how='left')
        df_processed.rename({id_colname: 'ID'}, inplace=True)
    df_processed.reset_index(drop=True, inplace=True)
    return df_processed
