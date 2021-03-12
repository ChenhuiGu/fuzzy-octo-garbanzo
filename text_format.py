import json
import os

from config import itsm_data_dir
from load_file import read_from_xlsx
import re

def extract_chinese(content):
    '''
    提取文本内的中文字符
    :param content:
    :return:
    '''
    if len(content) > 1000:
        return None
    # 中文字符
    content = re.findall(u"[\u4e00-\u9fa5]+", content)
    string = ''.join(content)
    if len(string) < 4:
        return None
    return string



def itsm_tbl_clean():
    '''
    工单分类文本清洗
    :return:
    '''
    cache_path = f'{itsm_data_dir}/clean_tmp.json'
    sentences = []
    # 类别对应的编号
    labels = []
    if not os.path.exists(cache_path):
        for item in read_from_xlsx(f'{itsm_data_dir}/tbl_itsm_incident_info.xlsx', ['E', 'I', 'J']):
            label = str(item[2]).strip()
            if not label:
                continue
            # 清洗数据
            sentence = item[0]
            if sentence:
                if len(sentence) > 400:
                    continue
                res = re.sub(r'<[^>]+>', "", sentence, flags=re.S).replace('&nbsp','').replace('"','')
                res = res.replace('\n','').replace('\t','').replace(' ','')
                if res.startswith('?') or res.startswith('[') or len(res) < 4 or res.startswith('%3'):
                    continue
                sentences.append(res.strip())
                labels.append(label)
        with open(cache_path, 'w') as fIn:
            json.dump({'sentences': sentences, 'label': labels}, fIn, ensure_ascii=False)
    else:
        with open(cache_path, 'r') as fOut:
            data = json.load(fOut)
            sentences = data['sentences']
            labels = data['label']
    return sentences, labels


if __name__ == '__main__':
    s,l = itsm_tbl_clean()
    print(s[:-10])
