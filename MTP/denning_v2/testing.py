b=1                     #low <= b        
a=b			# b <= a
c=d=e=f=g=h=i=j=k=l=9             # implimentation pending ;now its printing low <=c  
x=y=10			# implimentation pending ; low<=x
x+=b			# b ⊕ x <= x

if a<b:
	c=d*2		# a ⊕ b ⊕ d <= c
elif c<d:
	if e<f/2:
		c=d*2   # a ⊕ b ⊕ c ⊕ d ⊕ e ⊕ f ≤ c
		f=g*2   # a ⊕ b ⊕ c ⊕ d ⊕ e ⊕ f ⊕ g ≤ f
		while g<h:
			e=1  # a ⊕ b ⊕ c ⊕ d ⊕ e ⊕ f ⊕ g ⊕ h  ≤ e
			if i<j:
				f=1 # a ⊕ b ⊕ c ⊕ d ⊕ e ⊕ f ⊕ g ⊕ h ⊕ i ⊕ j ≤ f

else:
	if x<y:
		c=a # a ⊕ x ⊕ c ⊕ b ⊕ y ⊕ d ≤ c
	while k==l:
		d=e #a ⊕ c ⊕ b ⊕ k ⊕ l ⊕ d ⊕ e≤ d

