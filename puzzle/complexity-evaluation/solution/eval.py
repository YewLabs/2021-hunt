import itertools

G1 = [[1,0,1,1,1],[0,1,1,0,0],[0,0,1,0,0],[0,0,1,1,1],[0,1,0,0,0],[1,0,0,0,1],[0,1,1,0,0]]
G2 = [[0,1,0,0,0],[0,0,0,1,1],[0,1,0,1,1],[0,1,0,0,0],[0,0,1,0,1],[0,1,0,0,0],[0,0,0,1,1]]
G3 = [[0,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,1,0],[0,0,1,1,0],[1,0,0,0,0]]




def problem1(G):
	ret = [1,1,1,1,1]
	for a in range(5):
		for b in range(5):
			count = 0
			for c in range(7):
				if G[c][a] == 0 and G[c][b] == 0:
					count += 1
			if count == 2:
				ret[a] = 0
				ret[b] = 0
	ans = 0
	for a in range(5):
		ans += ret[a] * (1<<(4-a))
	return ans
	

def problem2(G):
	ret = 0
	for r in [0,1,2,3,4,5]:
		for s in [0,1,2,3,4,5,6,7]:
			for S in itertools.combinations([0,1,2,3,4],r):
				for T in itertools.combinations([0,1,2,3,4,5,6],s):
					works = r*s
					for a in S:
						for b in T:
							works -= G[b][a]
					if works == 0 and r*s > ret:
						ret = r*s
	return 20-ret

def isprime(n):
	for i in range(2,n):
		if n % i == 0:
			return False
	return True

def problem3(G):
	n = 0
	for a in range(5):
		for b in range(7):
			n += G[b][a] * (6**(b))
	count = 0
	for i in range(2,n+1):
		if n%i == 0 and isprime(i):
			count += 1
			if count == 2:
				return (n,(12*i+5)%23)

def problem4(G):
	n = 0
	for a in range(5):
		for b in range(7):
			n += G[b][a]
	return (110*n*n+102*n)%341
	
	
def problem5(G):
	s = ""
	for a in range(5):
		for b in range(7):
			s = s + str(G[b][a])
	return s
	
def problem6(G):
	s = ""
	for b in range(7):
		for a in range(5):
			s = s + str(G[b][a])
	return s

def problem7(G):
	matchings = 0
	size = 0
	for p in itertools.permutations(range(7),5):
		c = 0
		for a in range(5):
			c = c + G[p[a]][a]
		if c == size:
			matchings = matchings + 1
		if c > size:
			matchings = 1
			size = c
	if size == 4:
		matchings = matchings / 3
	if size == 3:
		matchings = matchings / (4*3)
	return matchings + 8*size*size - 78*size + 178


print("See the comment below the code for problems 5 and 6.")
print(" ")
for G in [G1,G2,G3]:
	print(problem1(G))
	print(problem2(G))
	print(problem3(G))
	print(problem4(G))
	print(problem5(G))
	print(problem6(G))
	print(problem7(G))
	print(" ")

"""
For problems 5 and 6, one can use the Turing Machine simulator at http://morphett.info/turing/turing.html
with the following code for their Turing Machines:

0 0 0 r 1
0 1 0 r 3
1 0 0 r 2
1 1 0 r 3
2 0 0 r halt
2 1 0 r 3
3 0 0 r 4
3 1 0 r 3
4 0 0 r 1
4 1 0 r 1


0 0 0 r 0
0 1 0 r 1
1 0 0 r 2
1 1 0 r 1
2 0 0 r 3
2 1 0 r 4
3 0 0 r halt
3 1 0 r halt
4 0 0 r 5
4 1 0 r 4
5 0 0 r 5
5 1 0 r 3

"""