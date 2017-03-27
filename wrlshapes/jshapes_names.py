ans = []

liste = ["j01",
"j08",
"j10",
"j12",
"j13",
"j14",
"j15",
"j16",
"j17",
"j49",
"j50",
"j51",
"j84",
"j86",
"j87",
"j88",
"j89",
"j90"]

for name in liste:
	file = open(name+".wrl")
	data = file.read()
	file.close()
	ans.append(data[data.index('"')+1:data.index(")")+1].capitalize())
for a in ans:
	b=a.split()
	print(" ".join(b[:-1]),b[-1])

