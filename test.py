class test:
	def __init__(self):
		self.i = 10

	def testit(self):
		def inner():
			print(self.i)

		inner()

if __name__ == '__main__':
	t = test()
	t.testit()