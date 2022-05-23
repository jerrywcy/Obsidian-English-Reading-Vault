import json
import pathlib
import sys
import os

vault_path=pathlib.Path(sys.argv[1])
vocabulary_path=vault_path / "Script" / "vocabulary.json"
vocabulary=0
with open(vocabulary_path,"r",encoding='utf-8') as f:
    vocabulary=json.loads(f.read())

text_path=vault_path / "Script" / "vocabulary.txt"
words=0
with open(text_path,"r",encoding='utf-8') as f:
    words=f.readlines()
n=len(words)
for i in range(0,n):
    words[i]=words[i].strip()
l=0
r=n-1
ans=0
flag=0
while l<=r:
    mid=(l+r)//2
    print("你认识"+words[mid]+"吗？(y/n)"+("请输入y或n" if flag==1 else ""));
    x=input()
    flag=0
    if (x=="y"):
        l=mid+1
        ans=l
    elif (x=="n"):
        r=mid-1
    else:
        flag=1
    os.system("cls")
for i in range(0,ans+1):
    vocabulary[words[i]]=1
with open(vocabulary_path,"w",encoding='utf-8') as f:
    print(json.dumps(vocabulary),file=f)
os.system("pause")