from main import query

cnt = 0
with open("term.txt", 'r') as f:
    for i in range(6000):
        f.readline()
    for i in range(1000):
        tmp = f.readline()
        query(tmp)