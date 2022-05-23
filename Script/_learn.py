import os

text = input() # command line use

def learn(text):
    folder_path = "your/foler/path/Vocabulary"
    for word in text:
        if "[[" not in word:
            if os.path.exists(folder_path + "/" + word.lower() + ".md"):
                os.remove(folder_path + "/" + word.lower() + ".md")
                print("delete {}".format(word))
            else:
                pass


puncts = [',', '.', '"', ':', ')', '(', '!', '?', '|', ';', "'", '$', '&', '/', '>', '%', '=', '#', '*', '+', '\\', '•',  '~', '@', '£', 
    '·', '_', '{', '}', '©', '^', '®', '`',  '<', '→', '°', '€', '™', '›',  '♥', '←', '×', '§', '″', '′', 'Â', '█', '½', 'à', '…', 
    '“', '★', '”', '–', '●', 'â', '►', '−', '¢', '²', '¬', '░', '¶', '↑', '±', '¿', '▾', '═', '¦', '║', '―', '¥', '▓', '—', '‹', '─', 
    '▒', '：', '¼', '⊕', '▼', '▪', '†', '■', '’', '▀', '¨', '▄', '♫', '☆', 'é', '¯', '♦', '¤', '▲', 'è', '¸', '¾', 'Ã', '⋅', '‘', '∞', 
    '∙', '）', '↓', '、', '│', '（', '»', '，', '♪', '╩', '╚', '³', '・', '╦', '╣', '╔', '╗', '▬', '❤', 'ï', 'Ø', '¹', '≤', '‡', '√', ]

def remove_punctuation(x):
    x = str(x)
    for punct in puncts:
        if punct in x:
            x = x.replace(punct, '')
    return x

for i in text:
    i = remove_punctuation(i)
    i = i.split()

    learn(i)



