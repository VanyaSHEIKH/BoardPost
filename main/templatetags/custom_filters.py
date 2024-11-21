from django import template

register = template.Library()


BAN_WORDS=['редиска', 'кабачок', 'дурак', 'дура', 'блин']


@register.filter(name='censor')
def censor(value):
    for word in BAN_WORDS:
        check = (value.lower()).find(word)
        while check != -1:
            len_ = len(word)
            value = value[:check]+word[0]+'*'*len_ + value[check+len_:]+word[-1]
            check = (value.lower()).find(word)
    return value
