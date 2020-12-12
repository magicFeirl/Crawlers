"""从文本读取输入，生成图云，并将 jieba 分词的结果输出
请自备字体"""
from wordcloud import WordCloud

import jieba
from bili_dynamic_crawler import fetch_all_dynamic


def generate_from_text_file(dest, **kwargs):
    with open(dest, encoding='utf-8') as f_str:
        text = f_str.read().strip()

    text = ' '.join(jieba.lcut(text))

    save_file = dest[:dest.find('.')] + '_jieba.txt'

    with open(save_file, 'w', encoding='utf-8') as f:
        f.write(text)

    wc = WordCloud(**kwargs).generate(text)
    wc.to_file(dest+'.png')


# fetch_all_dynamic('381678436', dest='yunjie')

generate_from_text_file('yunjie.txt', scale=8, font_path='Deng.ttf', background_color='white')

