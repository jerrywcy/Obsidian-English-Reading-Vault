import json

vocabulary=0;
with open("vocabulary.json","r",encoding='utf-8') as f:
    vocabulary=json.loads(f.read())

word=input();
while word!="0":
    vocabulary[word]=1;
    word=input();

with open("vocabulary.json","w",encoding='utf-8') as f:
    print(json.dumps(vocabulary,indent=1),file=f);