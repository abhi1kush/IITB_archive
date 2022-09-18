# Procedure copy2
z = 1
y = -1
while z == 1:
	y = y + 1
	if y == 0:
		z = x
	else:
		z = 0

Verify '=' : Low <= z
Verify '=' : Low <= y
Verify '=' : y <= y
Verify '=' : x <= z
Verify '=' : Low <= z
Verify if: y <= z
Verify seq 0 : y <= z
Verify while : y + x + z <= y * z
Verify seq 0 : Low <= y * z
Verify seq 1 : Low <= y * z

