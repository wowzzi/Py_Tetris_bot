def tri_recursion(k):
	if(k>0):
		print(f"value of k {k}")
		result = k+tri_recursion(k-1)
		print(f"result from each iteration {result}")
	else:
		result = 0
	return result

print("\n\nRecursion Example Results")
result = tri_recursion(6)
print("overall result:")
print(result)