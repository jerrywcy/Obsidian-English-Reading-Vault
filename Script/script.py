"""A Python 3 script written for the Obsidian English Reading Vault
Usage:
- python script.py "{{!vault_path}}" "mark as unknown" "{{!selection}}" "{{!file_path:relative}}" {{!caret_position:line}} {{!caret_position:column}}
    - mark the word at the cursor or in selection as unknown in the given document
    - `{{!vault_path}}`: the path to the Obsidian vault root
    - `{{!selection}}`: the word selected
    - `{{!file_path:relative}}`: the path to the document relative to the vault root
    - `{{!caret_position:line}}`: the line the cursor is at
    - `{{!caret_position:column}}`: the column the cursor is at
    - It's better to provide both selection and cursor position. If one of them is not provided, please leave it "" instead of nothing.

- python script.py "{{!vault_path}}" "mark as known" "{{!selection}}" "{{!file_path:relative}}" {{!caret_position:line}} {{!caret_position:column}}
    - mark the word at the cursor or in selection as known in the given document
    - `{{!vault_path}}`: the path to the Obsidian vault root
    - `{{!selection}}`: the word selected
    - `{{!file_path:relative}}`: the path to the document relative to the vault root
    - `{{!caret_position:line}}`: the line the cursor is at
    - `{{!caret_position:column}}`: the column the cursor is at
    - It's better to provide both selection and cursor position. If one of them is not provided, please leave it "" instead of nothing.

- python script.py "{{!vault_path}}" "mark article" "{{!file_path:relative}}"
    - mark the unknown words in the given document
    - `{{!vault_path}}`: the path to the Obsidian vault root
    - `{{!file_path:relative}}`: the path to the document relative to the vault root

- python script.py "{{!vault_path}}" "learn article" "{{!file_path:relative}}"
    - Learn all unknown words in the given document. Mark the words with a [[]] unknown and mark the rest known.
    - `{{!vault_path}}`: the path to the Obsidian vault root
    - `{{!file_path:relative}}`: the path to the document relative to the vault root
"""

#coding:utf-8
import io
from http.client import NETWORK_AUTHENTICATION_REQUIRED
import json
import os
import sys
import pathlib
import re
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')

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

"""puncts = [',', '.', '"', ':', ')', '(', '!', '?', '|', ';', "'", '$', '&', '/', '>', '%', '=', '#', '*', '+', '\\', '•',  '~', '@', '£', 
    '·', '_', '{', '}', '©', '^', '®', '`',  '<', '→', '°', '€', '™', '›',  '♥', '←', '×', '§', '″', '′', 'Â', '█', '½', 'à', '…', 
    '“', '★', '”', '–', '●', 'â', '►', '−', '¢', '²', '¬', '░', '¶', '↑', '±', '¿', '▾', '═', '¦', '║', '―', '¥', '▓', '—', '‹', '─', 
    '▒', '：', '¼', '⊕', '▼', '▪', '†', '■', '’', '▀', '¨', '▄', '♫', '☆', 'é', '¯', '♦', '¤', '▲', 'è', '¸', '¾', 'Ã', '⋅', '‘', '∞', 
    '∙', '）', '↓', '、', '│', '（', '»', '，', '♪', '╩', '╚', '³', '・', '╦', '╣', '╔', '╗', '▬', '❤', 'ï', 'Ø', '¹', '≤', '‡', '√', '\n','￡',
    '0','1','2','3','4','5','6','7','8','9']
"""

def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None

def link_to_word(link):
    return link[link.find("|")+1:link.find("]]")]

def remove_links(text):
    results=re.findall("\[\[[A-Za-z]*\|[A-Za-z]*\]\]",text)
    for res in results:
        print(res,res[res.find("|")+1:res.find("]]")])
        text=text.replace(res,res[res.find("|")+1:res.find("]]")])
    return text

def remove_punctuation(text):
    """Remove punctuation(everything except letters, commas, dots and spaces) from a piece of text.
    
    :param text: the text to remove punctuation from :class: String
    :return: text after being removed punctuation from :class: String
    """
    text=re.sub("[^A-Za-z\[\]\|\s,.]","",text)
    return text

def get_word(file_path,line,column):
    """Get the word at the cursor from a file
    
    :param file_path: the path to the file
    :param line: the line the cursor is at
    :param column: the column the cursor is at
    :return: the word at the cursor
    """
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
    """Mark a given word as unknown in `vocabulary.json` and create meaning document for it
    
    :param word: the word given (original form!)
    :return: 1 means the word is added correctly, 0 means error(already added, no such a word, etc.)
    """
    file_name=word+".md"
    word_path=vault_path / 'Vocabulary' / file_name
    if os.path.exists(word_path):
        print("The word already exists in /Vocabulary")
        return 0;

    if word not in dictionary.keys():
        print("We do not know "+word+"yet")
        return 0
    dic=dictionary[word]

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
    print("Successfully added word "+word)
    return 1

def mark_as_known(word):
    """Mark a given word as known in `vocabulary.json` and remove the meaning document for it
    
    :param word: the word given (original form!)
    """
    file_name=word+".md"
    word_path=vault_path / 'Vocabulary' / file_name
    if os.path.exists(word_path):
        word_path.unlink()
    vocabulary[word]=1
    
def mark_as_unknown_in_file(word,file_path):
    """Mark a given word as unknown in `vocabulary.json`, add the meaning document for it amd add [[]] for all such words in the given document
    
    :param word: the word given (original form!)
    :param file_path: the path to the given document
    """
    text=""
    with open(file_path,"r",encoding='utf-8') as f:
        text=f.read()
        article=remove_punctuation(text)
        article=sent_tokenize(article)
        for sentence in article:
            sentence=remove_links(sentence)
            if word in sentence:
                tokens=word_tokenize(sentence)
                tagged_sent=pos_tag(tokens,tagset='universal')
                wnl = WordNetLemmatizer()
                for tag in tagged_sent:
                    if word==tag[0]:
                        wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
                        word=wnl.lemmatize(tag[0], pos=wordnet_pos).lower()
                        print(word+" is the word selected")
                        if mark_as_unknown(word)==1:
                            add_bracket(word,file_path)
                        return 

def mark_as_known_in_file(word,file_path):
    """Mark a given word as unknown in `vocabulary.json`, remove the meaning document for it amd remove [[]] for all such words in the given document
    
    :param word: the word given (original form!)
    :param file_path: the path to the given document
    """
    text=""
    with open(file_path,"r",encoding='utf-8') as f:
        text=f.read()
        article=remove_punctuation(text)
        # print(article)
        article=sent_tokenize(article)
        for sentence in article:
            sentence=remove_links(sentence)
            print(sentence)
            if word in sentence:
                tokens=word_tokenize(sentence)
                tagged_sent=pos_tag(tokens,tagset='universal')
                wnl = WordNetLemmatizer()
                for tag in tagged_sent:
                    print(word,tag[0])
                    if word==tag[0]:
                        wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
                        word=wnl.lemmatize(tag[0], pos=wordnet_pos).lower()
                        print("the word selected is "+word)
                        mark_as_known(word)
                        remove_bracket(word,file_path)
                        return 

def add_bracket(word,file_path):
    """Add [[]] for a given word in a given document
    
    :param word: the word given (original form!)
    :param file_path: the path to the given document
    """
    print("Trying to add [[]] for word "+word)
    text=""
    with open(file_path,"r",encoding='utf-8') as f:
        text=" "+f.read()+" "
        article=remove_punctuation(text)
        article=sent_tokenize(article)
        for sentence in article:
            original_sentence=sentence
            sentence=remove_links(sentence)
            tokens=word_tokenize(sentence)
            tagged_sent=pos_tag(tokens,tagset='universal')
            wnl = WordNetLemmatizer()
            new_sentence=original_sentence
            for tag in tagged_sent:
                wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
                # print(wnl.lemmatize(tag[0], pos=wordnet_pos).lower(),tag[0],wnl.lemmatize(tag[0], pos=wordnet_pos).lower()==word)
                if word==wnl.lemmatize(tag[0], pos=wordnet_pos).lower():
                    print(tag[0],word)
                    results=re.findall("[^A-Za-z\[\]\|]"+tag[0]+"[^A-Za-z\[\]\|]",original_sentence)
                    for res in results:
                        new_sentence=new_sentence.replace(res,res[0]+"[["+word+"|"+tag[0]+"]]"+res[-1])
            text=text.replace(original_sentence,new_sentence)
            # print(new_sentence)
    text=text[1:-1]
    with open(file_path,"w",encoding='utf-8') as f:
        print(text,end='',file=f);

def remove_bracket(word,file_path):
    """Remove [[]] for a given word in a given document
    
    :param word: the word given (original form!)
    :param file_path: the path to the given document
    """
    text=""
    with open(file_path,"r",encoding='utf-8') as f:
        text=" "+f.read()+" "
        article=remove_punctuation(text)
        print(article)
        article=sent_tokenize(article)
        for sentence in article:
            original_sentence=sentence
            sentence=remove_links(sentence)
            print(sentence)
            tokens=word_tokenize(sentence)
            tagged_sent=pos_tag(tokens,tagset='universal')
            wnl = WordNetLemmatizer()
            new_sentence=original_sentence
            for tag in tagged_sent:
                wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
                if word==wnl.lemmatize(tag[0], pos=wordnet_pos).lower():
                    new_sentence=new_sentence.replace("[["+word+"|"+tag[0]+"]]",tag[0])
            text=text.replace(original_sentence,new_sentence)
    text=text[1:-1]
    with open(file_path,"w",encoding='utf-8') as f:
        print(text,end='',file=f);

def mark_article(file_path):
    """Mark all unknown words in a given document according to `vocabulary.json`
    
    :param file_path: the path to the given document
    """
    with open(file_path,"r",encoding='utf-8') as f:
        text=f.read()
        article=remove_punctuation(text)
        article=sent_tokenize(article)
        for sentence in article:
            sentence=remove_links(sentence)
            tokens=word_tokenize(sentence)
            tagged_sent=pos_tag(tokens,tagset='universal')
            wnl = WordNetLemmatizer()
            for tag in tagged_sent:
                wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
                word=wnl.lemmatize(tag[0], pos=wordnet_pos).lower()
                if word.isalpha() and word not in vocabulary.keys():
                    print("marked word "+word+' '+tag[1])
                    if mark_as_unknown(word)==1:
                        add_bracket(word,file_path)

def learn_article(file_path):
    """Learn all unknown words in a given document according to `vocabulary.json`. 
    Mark the words with a [[]] unknown and mark the rest known.
    
    :param file_path: the path to the given document
    """
    with open(file_path,"r",encoding='utf-8') as f:
        text=f.read()
        article=remove_punctuation(text)
        article=sent_tokenize(article)
        for sentence in article:
            original_sentence=sentence
            sentence=remove_links(sentence)
            tokens=word_tokenize(sentence)
            tagged_sent=pos_tag(tokens,tagset='universal')
            wnl = WordNetLemmatizer()
            for tag in tagged_sent:
                wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
                word=wnl.lemmatize(tag[0], pos=wordnet_pos).lower()
                if "[["+word+"|"+tag[0]+"]]" not in original_sentence or :
                    mark_as_known(word)
                else:
                    if mark_as_unknown(word)==1:
                        add_bracket(word,file_path)

operation=sys.argv[2]
if operation=="mark as unknown":
    word=remove_punctuation(sys.argv[3].lower())
    file_path=vault_path / sys.argv[4]
    if (word==""):
        word=get_word(file_path,int(sys.argv[5]),int(sys.argv[6]))
    mark_as_unknown_in_file(word,file_path)
elif operation=="mark article":
    file_path=vault_path / sys.argv[3]
    mark_article(file_path)
elif operation=="mark as known":
    word=remove_punctuation(sys.argv[3].lower())
    file_path=vault_path / sys.argv[4]
    if (word==""):
        word=get_word(file_path,int(sys.argv[5]),int(sys.argv[6]))
    print("the word selected is "+word)
    mark_as_known_in_file(word,file_path)
elif operation=="learn article":
    file_path=vault_path / sys.argv[3]
    learn_article(file_path)

with open(vocabulary_path,"w",encoding='utf-8') as f:
    print(json.dumps(vocabulary),file=f)