import sys
with open(sys.argv[1]) as f:
	content = '\n'.join(f.readlines()).strip()
N = len(content) # total length of ciphertext

# First determine the key length using index of coincidence
for n in range(1,40):
	chars = [ord(content[i]) for i in range(0,N,n)]
	score = sum( (chars.count(c) / (N//n))**2 for c in set(chars) )
	print(n,score)
	if score > 0.05: # arbitrary threshold
		print("Key length", n, "with score", score, "\n")
		break
else:
	sys.exit("Could not determine key length, change threshold manually")

shifts = []
for k in range(n):
	chars = [ord(content[i]) for i in range(k,N,n)]
	# look at the smallest index m
	m = min(chars)
	k = m + ord(' ') - ord('\n') # if m is '\n' this is ' '
	if chars.count(k) > 0:
		shift = m - ord('\n') # guess that m is newline
	else:
		shift = m - ord(' ') # guess that m is space
	shifts.append(shift)

plaintext = ''
for i in range(N):
	plaintext += chr(ord(content[i]) - shifts[i%n])
print('KEY:', ''.join(chr(_) for _ in shifts))
print(plaintext[0:200] + "...")
