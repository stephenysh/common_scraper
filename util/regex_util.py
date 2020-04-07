import re
from collections import namedtuple
from string import punctuation

_reg_dict = {
    'multi_blank': re.compile('\s+'),
    'html_maybe_text': re.compile(r'^p$|^h[1-6]$|^span$'),
    # 'html_maybe_text': re.compile(r'^p$'),
    'arabic_chars_and_space': re.compile('[\u0600-\u06FF ]'),
    'english_chars_and_space': re.compile('[a-zA-Z ]'),
    'arabic_chars': re.compile('[\u0600-\u06FF]'),
    'english_chars': re.compile('[a-zA-Z]'),
    'arabic_words': re.compile('[\u0600-\u06FF]+'),
    'bad_chars': re.compile(
        rf'[^\”\“\«\»\-\–\…\″\’\‘\‑\u202a\u202b\u202c\u202d\u202e\u200b\u200c\u200d\u200e\u200f\u0600-\u06FFa-zA-Z\d ' + ''.join(
            [rf"\\{i}" for i in punctuation]) + ']+')
}
pattern_names = ['multi_blank',
                 'html_maybe_text',
                 'arabic_chars_and_space',
                 'english_chars_and_space',
                 'arabic_chars',
                 'english_chars',
                 'arabic_words',
                 'bad_chars'
                 ]
RegPatterns = namedtuple('RegPatterns', pattern_names)

REGPATTERNS = RegPatterns(multi_blank=re.compile('\s+'),
                          html_maybe_text=re.compile(r'^p$|^h[1-6]$|^span$'),
                          arabic_chars_and_space=re.compile('[\u0600-\u06FF ]'),
                          english_chars_and_space=re.compile('[a-zA-Z ]'),
                          arabic_chars=re.compile('[\u0600-\u06FF]'),
                          english_chars=re.compile('[a-zA-Z]'),
                          arabic_words=re.compile('[\u0600-\u06FF]+'),
                          bad_chars=re.compile(
                              rf'[^\”\“\«\»\-\–\…\″\’\‘\‑\u202a\u202b\u202c\u202d\u202e\u200b\u200c\u200d\u200e\u200f\u0600-\u06FFa-zA-Z\d ' + ''.join(
                                  [rf"\\{i}" for i in punctuation]) + ']+'),
                          )
