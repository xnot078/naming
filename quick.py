import re
from collections import defaultdict
import pandas as pd
from typing import Mapping, List

# 國語辭典
txt_dict = pd.read_excel('dict_concised_2014_20220328.xlsx')
txt_dict = txt_dict[txt_dict['L']==1]
txt_dict = txt_dict[['字詞名', '總筆畫數', '注音一式', '釋義']]
txt_dict['釋義2'] = txt_dict['釋義'].str.split('\[例\]').apply(lambda x: x[0] if len(x)>1 else x)
txt_dict['釋義2'] = txt_dict['釋義2'].apply(lambda x: '|'.join(x) if isinstance(x, list) else x)

# 適合筆畫組合
num_com = '16+5+8；16+5+10；16+5+11；16+5+12；16+5+18；16+7+8；16+7+9；16+7+10；16+7+14；16+7+16；16+7+18；16+8+5；16+8+7；16+8+9；16+8+13；16+8+15；16+8+17；16+8+21；16+9+7；16+9+8；16+9+14；16+9+16；16+9+20；16+13+8；16+13+10；16+13+16；16+13+18；16+13+19；16+15+8；16+15+10；16+15+14；16+15+16；16+15+17；16+16+7；16+16+9；16+16+13；16+16+15；16+16+16；16+17+8；16+17+15'
com_dict = defaultdict(list)
for i in num_com.split('；'):
    f, s, t = i.split('+')
    com_dict[int(s)].append(int(t))

# 字義函式
def find_word_com(m1:str, m2:str)->Mapping[int, List[str]]:
    res = defaultdict(list)
    res_meaning = defaultdict(list)
    mask_m1 = txt_dict['釋義2'].str.match(rf'.*{m1}.*')
    mask_m2 = txt_dict['釋義2'].str.match(rf'.*{m2}.*')

    for l1, l2_list in com_dict.items():
        subset_w1 = txt_dict[mask_m1]
        subset_w1 = find_corrcet_word_num(subset_w1, l1)
        if subset_w1.empty:
            continue
        for l2 in l2_list:
            subset_w2 = txt_dict[mask_m2]
            subset_w2 = find_corrcet_word_num(subset_w2, l2)
            if subset_w2.empty:
                continue
            for w1, real_m1 in subset_w1[['字詞名', '釋義2']].values:
                for w2, real_m2 in subset_w2[['字詞名', '釋義2']].values:
                    res[f'{l1}+{l2}'].append(w1+w2)
                    res_meaning[w1+w2] = [real_m1, real_m2]

    return res, res_meaning

def find_corrcet_word_num(subset:pd.DataFrame, word_num:int)->pd.DataFrame:
    mask = subset['總筆畫數'] == word_num
    return subset[mask]

name_com, name_com_meaning = find_word_com(m1='水', m2='光')
name_com_meaning['澧熹']
"""
洋曦: ['1.較海為大的水域，也可泛指地球表面廣大的海域。', '日光、日色。']
洋昀: ['1.較海為大的水域，也可泛指地球表面廣大的海域。', '日光、日色。']
洋曄: ['1.較海為大的水域，也可泛指地球表面廣大的海域。', '光明、繁盛的樣子。']
洋熹: ['1.較海為大的水域，也可泛指地球表面廣大的海域。', '天剛亮、光明。']
洋耀: ['1.較海為大的水域，也可泛指地球表面廣大的海域。', '1.光線強烈的照射。']
濬明: ['疏通或挖深水道。', '1.光亮，光線充足的。與「暗」相對。']
澤曄: ['1.水流匯聚的地方。', '光明、繁盛的樣子。']
澤熹: ['1.水流匯聚的地方。', '天剛亮、光明。']
"""
