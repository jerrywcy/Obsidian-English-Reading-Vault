import json
import os
import sys
import pathlib
import re

# vault path
vault_path=pathlib.Path(sys.argv[1])
script_path=vault_path / "Script"

# dictionary
dictionary={}
dictionary_path=vault_path / "Script" 
with open("dictionary.json","r",encoding='utf-8') as f:
    dictionary=json.loads(f.read())

# known vocabulary
vocabulary={}
vocabulary_path=vault_path / "Script" / "vocabulary.json"
with open(vocabulary_path,"r",encoding='utf-8') as f:
    vocabulary=json.loads(f.read());

# puncts = [',', '.', '"', ':', ')', '(', '!', '?', '|', ';', "'", '$', '&', '/', '>', '%', '=', '#', '*', '+', '\\', '•',  '~', '@', '£', 
#     '·', '_', '{', '}', '©', '^', '®', '`',  '<', '→', '°', '€', '™', '›',  '♥', '←', '×', '§', '″', '′', 'Â', '█', '½', 'à', '…', 
#     '“', '★', '”', '–', '●', 'â', '►', '−', '¢', '²', '¬', '░', '¶', '↑', '±', '¿', '▾', '═', '¦', '║', '―', '¥', '▓', '—', '‹', '─', 
#     '▒', '：', '¼', '⊕', '▼', '▪', '†', '■', '’', '▀', '¨', '▄', '♫', '☆', 'é', '¯', '♦', '¤', '▲', 'è', '¸', '¾', 'Ã', '⋅', '‘', '∞', 
#     '∙', '）', '↓', '、', '│', '（', '»', '，', '♪', '╩', '╚', '³', '・', '╦', '╣', '╔', '╗', '▬', '❤', 'ï', 'Ø', '¹', '≤', '‡', '√', '\n','￡',
#     '0','1','2','3','4','5','6','7','8','9']

def remove_punctuation(x):
    # for punct in puncts:
    #     if punct in x:
    #         x = x.replace(punct, '')
    results=re.findall("[^A-Z,a-z,\[,\]\s]",x)
    for res in results:
        x=x.replace(res,'')
    return x

def get_word(file_path,line,column):
    text=""
    with open(file_path,"r",encoding='utf-8') as f:
        text=f.readlines()[line-1]
    l=column-1
    while l>=0 and text[l:l+1].isalpha():
        l=l-1
    l=l+1
    r=column-1
    while r<len(text) and text[r:r+1].isalpha():
        r=r+1
    word=text[l:r]
    print(l,r)
    return word

def mark_as_unknown(word):
    word=remove_punctuation(word.lower())
    file_name=word+".md"
    word_path=vault_path / 'Vocabulary' / file_name
    if os.path.exists(word_path):
        return 0;

    # APIurl='https://api.dictionaryapi.dev/api/v2/entries/en/';
    # dic=requests.get(APIurl+word).json();

    if word not in dictionary.keys():
        return 0
    dic=dictionary[word]
    # print("findword\n"+json.dumps(dic,indent=4))

    if word in vocabulary.keys():
        del vocabulary[word]
    word_path.touch()
    with open(word_path,"w",encoding='utf-8') as f:
        f.write(open("front_template.md","r").read());
        print("# "+word,file=f);
        print(word,end=' ',file=f);
        for x in dic['readings']:
            print("/"+x+"/",end=' ',file=f);
        print("",file=f);
        print("",file=f);
        for definition in dic['defs']:
            print("## "+definition['pos_cn'],file=f);
            print("",file=f);
            print(definition['def_cn'],file=f);
            print("",file=f);
            print(definition['def_en'],file=f);
            print("",file=f);
            for ext in definition['ext']:
                print("> "+ext['ext_en'],file=f);
                print("> "+ext['ext_cn'],file=f);
                print("",file=f);
                print("",file=f);
        f.write(open("back_template.md","r").read());
    return 1

def mark_as_known(word):
    word=remove_punctuation(word.lower())
    file_name=word+".md"
    word_path=vault_path / 'Vocabulary' / file_name
    if os.path.exists(word_path):
        word_path.unlink()
    vocabulary[word]=1

def add_bracket(word,file_path):
    article=""
    with open(file_path,"r",encoding='utf-8') as f:
        article=f.read()
        results=re.findall("[^A-Z,a-z,\[,\]]"+word+"[^A-Z,a-z,\[,\]]",article)
        for res in results:
            article=article.replace(res,res.replace(word,"[["+word+"]]"));
    with open(file_path,"w",encoding='utf-8') as f:
        print(article,end='',file=f);

def remove_bracket(word,file_path):
    article=""
    with open(file_path,"r",encoding='utf-8') as f:
        article=f.read().replace("[["+word+"]]",word);
    with open(file_path,"w",encoding='utf-8') as f:
        print(article,end='',file=f);

def mark_article(file_path):
    article=""
    with open(file_path,"r",encoding='utf-8') as f:
        article=f.read();
        text=remove_punctuation(article).split();
        for word in text:
            if word!="" and word.lower() not in vocabulary.keys():
                if mark_as_unknown(word)==1:
                    add_bracket(word,file_path)

def learn_article(file_path):
    article=""
    with open(file_path,"r",encoding='utf-8') as f:
        article=f.read();
        text=remove_punctuation(article).split();
        for word in text:
            if "[[" not in word:
                vocabulary[word.lower()]=1
            else:
                word=word[2:-2]
                if mark_as_unknown(word)==1:
                    add_bracket(word,file_path)

operation=sys.argv[2]
if operation=="mark as unknown":
    word=remove_punctuation(sys.argv[3].lower())
    file_path=vault_path / sys.argv[4]
    if (word==""):
        word=get_word(file_path,int(sys.argv[5]),int(sys.argv[6]))
    mark_as_unknown(word)
    add_bracket(word,file_path)
elif operation=="mark article":
    file_path=vault_path / sys.argv[3]
    mark_article(file_path)
elif operation=="mark as known":
    word=remove_punctuation(sys.argv[3].lower())
    file_path=vault_path / sys.argv[4]
    if (word==""):
        word=get_word(file_path,int(sys.argv[5]),int(sys.argv[6]))
    mark_as_known(word)
    remove_bracket(word,file_path)
elif operation=="learn article":
    file_path=vault_path / sys.argv[3]
    learn_article(file_path)

with open(vocabulary_path,"w",encoding='utf-8') as f:
    print(json.dumps(vocabulary),file=f)