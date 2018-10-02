def txtReader(fname, page):
	# lcd.clear()
	# f = Framework('txtReader')
	# f.drawNaviButton(strC='EXIT')
	with open(fname, 'r') as o:
		o.seek(page * 240 + 1)
		flag_end = False
		for row in range(12):
			if flag_end:
				break
			for col in range(20):
				c = o.read(1)
				if not c:
					print('--- END ---')
					flag_end = True
					break
				if c != '\n':
					print('%s' % c, end='')
				else:
					break
			print('')

	# 	rawText = o.read()
	# raws = rawText.split('\n')
	# text_dis = []
	# for s in raws:
	# 	if len(s) <= 20:
	# 		text_dis.append(s)
	# 	else:
	# 		n_slice = int(len(s) / 20)+1
	# 		for i in range(n_slice):
	# 			if len(s[i*20:]) > 20:
	# 				text_dis.append(s[i*20:(i+1)*20])
	# 			else:
	# 				text_dis.append(s[i*20:])
	# text_dis.remove('')
	# for i in text_dis:
	# 	print(i)
	# # del raws
	# # del rawText
	# # n_page = (len(text_dis) / 12)+1
	# # n_startPage = 0
	# # # while True:
	# # for ii in range(len(text_dis)):
	# # 	# lcd.clear()
	# # 	# lcd.setCursor(0,0)
	# # 	# lcd.font(lcd.FONT_Ubuntu, transparent=False, fixedwidth=True)
	# # 	endIdx = (n_startPage+1)*12
	# # 	if endIdx > len(text_dis):
	# # 		endIdx = len(text_dis)
	# # 	for i in range(n_startPage*12, endIdx):
	# # 		print(text_dis[i])
	# # 	# while True:
	# # 	# 	time.sleep(0.1)
	# # 	# 	if buttonA.isPressed():
	# # 	# 		if n_startPage != 0:
	# # 	# 			n_startPage -= 1
	# # 	# 		break
	# # 	# 	elif buttonB.isPressed():
	# # 	# 		if n_startPage < n_page:
	# # 	# 			n_startPage += 1
	# # 	# 		break
	# # 	# 	elif buttonC.isPressed():
	# # 	# 		return 0

if __name__ == '__main__':
	txtReader('longtxt.txt', 2)