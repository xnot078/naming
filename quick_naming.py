import re
from collections import defaultdict
import pandas as pd
from tqdm import tqdm
from typing import Mapping, List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

class get_score:

    def __init__(self, headless=True):
        self.driver = self.InitDriver(headless)

    @staticmethod
    def InitDriver(headless=True):
        """
        初始化瀏覽器
        """
        chrome_options = Options()
        # chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        chrome_options.add_argument("incognito")
        if headless:
            chrome_options.add_argument("--headless")
        Driver = webdriver.Chrome(r"./chromedriver.exe", chrome_options = chrome_options)
        Driver.implicitly_wait(0.5)
        return Driver

    def scoring(self, lastName:str, firstName:str)->Optional[int]:
        if self.driver.current_url != 'https://www.zhanbuwang.com/xingmingceshi_2.php':
            self.driver.get('https://www.zhanbuwang.com/xingmingceshi_2.php')
        lastName_input = self.driver.find_element_by_css_selector('body > div > div > div:nth-child(2) > div.c_name_from > table > tbody > tr > td:nth-child(2) > input')
        if lastName_input:
            lastName_input.clear()
            lastName_input.send_keys(lastName)
        firstName_input = self.driver.find_element_by_css_selector('body > div > div > div:nth-child(2) > div.c_name_from > table > tbody > tr > td:nth-child(4) > input')
        if firstName_input:
            firstName_input.clear()
            firstName_input.send_keys(firstName)
        submmit_key = self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div[3]/table/tbody/tr/td[5]/input")
        if submmit_key:
            submmit_key.click()
        ele_score = self.driver.find_element_by_css_selector('body > div > div > div:nth-child(3) > div.c_1_text > div > div.pingfen_right > div.pingfen_right_ass > span')
        if ele_score:
            score = int(ele_score.text)
            return score
        return None

class get_word_combinations(get_score):

    def __init__(self, headless=True, dictionary_path='./dict_concised_2014_20220328.xlsx', comStr='16+5+8；16+5+10；16+5+11；16+5+12；16+5+18；16+7+8；16+7+9；16+7+10；16+7+14；16+7+16；16+7+18；16+8+5；16+8+7；16+8+9；16+8+13；16+8+15；16+8+17；16+8+21；16+9+7；16+9+8；16+9+14；16+9+16；16+9+20；16+13+8；16+13+10；16+13+16；16+13+18；16+13+19；16+15+8；16+15+10；16+15+14；16+15+16；16+15+17；16+16+7；16+16+9；16+16+13；16+16+15；16+16+16；16+17+8；16+17+15'):
        super().__init__(headless)
        self.txt_dict = self.read_user_dictionary(dictionary_path)
        self.com_dict = self.properly_strokes(comStr)

    def read_user_dictionary(self, path='./dict_concised_2014_20220328.xlsx'):
        """
        讀取國語辭典
        """
        txt_dict = pd.read_excel('./dict_concised_2014_20220328.xlsx')
        txt_dict = txt_dict[txt_dict['L']==1]
        txt_dict = txt_dict[['字詞名', '總筆畫數', '注音一式', '釋義', '部首字']]
        txt_dict['釋義2'] = txt_dict['釋義'].str.split('\[例\]').apply(lambda x: x[0] if len(x)>1 else x)
        txt_dict['釋義2'] = txt_dict['釋義2'].apply(lambda x: '|'.join(x) if isinstance(x, list) else x)
        txt_dict['部首字'] = txt_dict['部首字'].str.strip()
        return txt_dict

    def properly_strokes(self, comStr='16+5+8；16+5+10；16+5+11；16+5+12；16+5+18；16+7+8；16+7+9；16+7+10；16+7+14；16+7+16；16+7+18；16+8+5；16+8+7；16+8+9；16+8+13；16+8+15；16+8+17；16+8+21；16+9+7；16+9+8；16+9+14；16+9+16；16+9+20；16+13+8；16+13+10；16+13+16；16+13+18；16+13+19；16+15+8；16+15+10；16+15+14；16+15+16；16+15+17；16+16+7；16+16+9；16+16+13；16+16+15；16+16+16；16+17+8；16+17+15'):
        """
        # 適合筆畫組合。預設"陳"姓。
        https://www.yamab2b.com/zhouyi/NDZlYXE=.html
        """
        com_dict = defaultdict(list)
        for i in comStr.split('；'):
            f, s, t = i.split('+')
            com_dict[int(s)].append(int(t))
        return com_dict

    # 字義函式
    def find_word_com(self, m1:str, m2:str, head1='', head2='')->Mapping[int, List[str]]:
        res = defaultdict(list)
        res_meaning = defaultdict(list)
        mask_m1 = self.txt_dict['釋義2'].str.match(rf'.*{m1}.*')
        mask_m2 = self.txt_dict['釋義2'].str.match(rf'.*{m2}.*')

        for l1, l2_list in self.com_dict.items():
            subset_w1 = self.txt_dict[mask_m1]
            subset_w1 = self.find_corrcet_word_num(subset_w1, l1)
            subset_w1 = self.find_corrcet_word_head(subset_w1, head1)
            if subset_w1.empty:
                continue
            for l2 in l2_list:
                subset_w2 = self.txt_dict[mask_m2]
                subset_w2 = self.find_corrcet_word_num(subset_w2, l2)
                subset_w2 = self.find_corrcet_word_head(subset_w2, head2)
                if subset_w2.empty:
                    continue
                for w1, real_m1 in subset_w1[['字詞名', '釋義2']].values:
                    for w2, real_m2 in subset_w2[['字詞名', '釋義2']].values:
                        # score = scoring(driver, '陳', w1+w2)
                        res[f'{l1}+{l2}'].append(w1+w2)
                        res_meaning[w1+w2] = [real_m1, real_m2]
        return res, res_meaning

    def find_corrcet_word_num(self, subset:pd.DataFrame, word_num:int)->pd.DataFrame:
        mask = subset['總筆畫數'] == word_num
        return subset[mask]

    def find_corrcet_word_head(self, subset:pd.DataFrame, head:str)->pd.DataFrame:
        if len(head)==0:
            return subset
        mask = subset['部首字'] == head
        return subset[mask]

    def go(self, m1='實', m2='\w', head1='', head2='竹', do_scoring=True, tops=None)->pd.DataFrame:
        name_com, name_com_meaning = self.find_word_com(m1, m2, head1, head2)

        all_names = [j for i in name_com.values() for j in i]
        all_names = list(set(all_names))
        slice_names = all_names[:tops] if tops else all_names
        if not do_scoring:
            res = pd.DataFrame(
                        [
                            slice_names,
                            [name_com_meaning.get(n, None) for n in slice_names]
                        ], index=['name', 'mean']
                    )
            res = res.T
            return res

        scores = []
        pbar = tqdm(slice_names)
        for i in pbar:
            pbar.set_description(i)
            try:
                s = self.scoring('陳', i)
            except:
                s = None
            scores.append(s)

        res = pd.DataFrame(
            [
                slice_names,
                scores,
                [name_com_meaning.get(n, None) for n in slice_names]
            ], index=['name', 'score', 'mean']
        )
        res = res.T
        return res.sort_values('score', ascending=False,)

    def close_driver(self):
        self.driver.close()


if __name__ == '__main__':
    gwc = get_word_combinations(headless=True)

    m1='' # 名的第一個字須包含的字義, ''表示不限制
    m2='勤' # 名的第二個字須包含的字義, ''表示不限制
    head1='' # 名的第一個字的部首, ''表示不限制
    head2='心' # 名的第二個字的部首
    res = gwc.go(m1, m2, head1, head2, do_scoring=True)

    dst = './res/res_' + m1.replace("\\", '') + "+" + m2.replace("\\", '') + "_" + head1.replace("\\", '') + '+' + head2.replace("\\", '')
    res.to_excel(f'{dst}.xlsx')


"""
洋曦: ['1.較海為大的水域，也可泛指地球表面廣大的海域。', '日光、日色。']
洋昀: ['1.較海為大的水域，也可泛指地球表面廣大的海域。', '日光、日色。']
洋曄: ['1.較海為大的水域，也可泛指地球表面廣大的海域。', '光明、繁盛的樣子。']
洋熹: ['1.較海為大的水域，也可泛指地球表面廣大的海域。', '天剛亮、光明。']
洋耀: ['1.較海為大的水域，也可泛指地球表面廣大的海域。', '1.光線強烈的照射。']
濬輝: ['疏通或挖深水道。', '1.光彩、光芒。']
濬明: ['疏通或挖深水道。', '1.光亮，光線充足的。與「暗」相對。']
澤曄: ['1.水流匯聚的地方。', '光明、繁盛的樣子。']
澤熹: ['1.水流匯聚的地方。', '天剛亮、光明。']
"""
