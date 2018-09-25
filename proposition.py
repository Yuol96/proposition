class Node:
	"""
	Basic data structure for the construction of the computing graph of propositional logic expressions.
	"""
	def __init__(self, opr, *parents):
		self.parents = parents
		self.opr = opr

	def __call__(self):
		values = [parent() for parent in self.parents]
		return self.opr(*values)

	def negation(self):
		return Node(lambda p: not p, self)

	def conjunction(self, node):
		return Node(lambda p,q: p and q, self, node)

	def disjunction(self, node):
		return Node(lambda p,q: p or q, self, node)

	def implication(self, node):
		return Node(lambda p,q: False if p and not q else True, self, node)

	def twoWayImplication(self, node):
		return Node(lambda p,q: p == q, self, node)

class Proposition(Node):
	"""
	This is a 'DataProvider', i.e. the placeholder of a logical variable in a propositional logic expression.
	"""
	def __init__(self, name,val=None):
		assert val in [True, False, None]
		self._val = val
		self._name = name
		self.parents = []

	def __call__(self):
		if self._val is None:
			raise ValueError("You haven't input the value of {}".format(self.name))
		return self._val

	@property
	def val(self):
		return self._val

	@val.setter
	def val(self, v):
		assert v in [True, False, None]
		self._val = v

	@property
	def name(self):
		return self._name
	

class PropositionLogic:
	"""
	responsible for parsing input formula and converting it into a computing graph.
	"""
	def __init__(self, formulaStr):
		self.formulaStr = formulaStr.replace(" ",'')
		self.outputNode, self.name2proposition = self.parseFormula(self.formulaStr)

	def __call__(self, **kwargs):
		for varName, value in kwargs.items():
			self.name2proposition[varName].val = value
		output = self.outputNode()
		self.clearAllProposition()
		return output

	def getTruethFunction(self, pandas=True):
		"""
		The trueth function is stored in a pandas DataFrame and returned.
		"""
		dct = {}
		allTokens = sorted(self.name2proposition.keys())
		def DFS(dct, tokenList, currList):
			if len(tokenList) == 0:
				for k,v in zip(allTokens, currList):
					dct[k] = dct.get(k, []) + [v]
				return
			DFS(dct, tokenList[1:], currList+[True])
			DFS(dct, tokenList[1:], currList+[False])
		DFS(dct, allTokens, [])

		if pandas:
			import pandas as pd
			df = pd.DataFrame(dct)
			def compute(row):
				kwargs = row.to_dict()
				if self.formulaStr in row:
					row["output"] = self(**kwargs)
				row[self.formulaStr] = self(**kwargs)
				return row
			df = df.apply(compute, axis=1)
			return df
		else:
			lst = []
			for idx in range(2**len(allTokens)):
				kwargs = {token:dct[token][idx] for token in allTokens}
				lst.append(self(**kwargs))
			if self.formulaStr in dct:
				dct["output"] = lst
			# dct[self.formulaStr] = lst
			dct["output"] = lst
			return dct

	def clearAllProposition(self):
		def DFS(node):
			if len(node.parents) == 0:
				node.val = None
				return
			for parent in node.parents:
				DFS(parent)
		DFS(self.outputNode)

	@classmethod
	def getNextToken(self, s):
		if not s:
			return None
		idx = 0
		if s[idx] in ['(',')','!','&','|']:
			return s[idx]
		if s[idx] == '-':
			if s[idx+1] != '>':
				raise SyntaxError("Do you mean '->'?")
			return '->'
		if s[idx] == '<':
			if s[idx+1:idx+3] != '->':
				raise SyntaxError("Do you mean '<->'?")
			return '<->'
		st = set(list('_abcdefghijklmnopqrstuvwxyz'))
		if s[idx] not in st:
			raise SyntaxError("invalid character '{}'".format(s[idx]))
		while idx<len(s) and s[idx] in st:
			idx += 1
		return s[:idx]

	@classmethod
	def getAllToken(self, s):
		lst = []
		idx = 0
		while idx<len(s):
			token = self.getNextToken(s[idx:])
			idx += len(token)
			lst.append(token)
		return lst

	@classmethod
	def rankChar(self, s):
		if s in ['(',')']:
			return 5
		if s == '!':
			return 4
		if s in ['&','|']:
			return 3
		if s == '->':
			return 2
		if s == '<->':
			return 1
		return 0

	@classmethod
	def transformFormula(self, formulaStr):
		import re
		outputFormula = []
		stack = []
		self.varNames = set(re.findall("([a-z_]+)", formulaStr))
		allTokens = self.getAllToken(formulaStr)
		for token in allTokens:
			rank = self.rankChar(token)
			if rank == 0:
				outputFormula.append(token)
			else:
				if token == '(':
					stack.append((token, rank))
				elif token == ')':
					while len(stack)>0 and stack[-1][0]!='(':
						outputFormula.append(stack.pop()[0])
					if len(stack) == 0:
						raise SyntaxError("Check parenthesis")
					stack.pop()
				else:
					while len(stack)>0 and stack[-1][0]!='(' and stack[-1][1] >= rank:
						outputFormula.append(stack.pop()[0])
					stack.append((token, rank))
		while len(stack)>0:
			outputFormula.append(stack.pop()[0])
		return outputFormula

	@classmethod
	def parseFormula(self, formulaStr):
		postExprList = self.transformFormula(formulaStr)
		stack = []
		name2proposition = {}
		for token in postExprList:
			rank = self.rankChar(token)
			if rank == 0:
				if token not in name2proposition:
					name2proposition[token] = Proposition(token)
				stack.append(name2proposition[token])
			else :
				if token == '!':
					stack[-1] = stack[-1].negation()
				else:
					b = stack.pop()
					a = stack.pop()
					if token == '&':
						stack.append(a.conjunction(b))
					elif token == '|':
						stack.append(a.disjunction(b))
					elif token == '->':
						stack.append(a.implication(b))
					elif token == '<->':
						stack.append(a.twoWayImplication(b))
		return stack[0], name2proposition
	
def test_node():
	lst = [False, True]
	for i in range(2):
		for j in range(2):
			a = Proposition('a',lst[i])
			b = Proposition('b',lst[j])
			assert a()==lst[i]
			assert b()==lst[j]
			assert a.negation()() == (not lst[i])
			assert b.negation()() == (not lst[j])
			assert a.conjunction(b)() == (lst[i] and lst[j])
			assert a.disjunction(b)() == (lst[i] or lst[j])
			assert a.implication(b)() == (not (lst[i] and not lst[j]))
			assert a.twoWayImplication(b)() == (lst[i] == lst[j])

def test_getAllToken():
	s = 'lks<->jd((f))l->ksjdf&lskjdf|b'
	lst = PropositionLogic.getAllToken(s)
	assert tuple(lst) == tuple(['lks','<->','jd','(','(','f',')',')','l','->','ksjdf','&','lskjdf','|','b'])

def test_transformFormula():
	s = '(a<->b->c&d&e|f)->(b<->!c)'
	lst = PropositionLogic.transformFormula(s)
	assert tuple(lst) == tuple(['a', 'b', 'c', 'd', '&', 'e', '&', 'f', '|', '->', '<->', 'b', 'c', '!', '<->', '->'])

if __name__ == '__main__':
	import argparse
	from pprint import pprint
	from IPython import embed
	from http.server import BaseHTTPRequestHandler, HTTPServer
	import os
	import urllib
	import json
	import ssl

	parser = argparse.ArgumentParser()
	parser.add_argument('-f','--formula',type=str,default='(p->q)&(!p->q)')
	parser.add_argument('--pandas',default=False, action="store_true")
	parser.add_argument('-s','--server',default=False, action="store_true")
	parser.add_argument('--addr',default="0.0.0.0")
	parser.add_argument('-p','--port',default=8085,type=int)
	args = parser.parse_args()

	if args.server:
		class myHandler(BaseHTTPRequestHandler):
			def do_GET(self):
				print(self.path)
				if self.path.startswith('/?formula='):
					# idx = self.path.index('=') + 1
					# formulaStr = self.path[idx+1:]
					# print(urllib.parse.parse_qs(self.path.encode()))
					formulaStr = urllib.parse.parse_qs(self.path.encode())[b'/?formula'][0].decode()
					print(formulaStr)
					try:
						dct = os.popen("python3 proposition.py -f='{}'".format(formulaStr)).read()
						dct = eval(dct)
						self.send_response(200)
						self.send_header('Content-type','text/html')
						self.send_header("Access-Control-Allow-Origin", "*")
						self.end_headers()
						self.wfile.write(json.dumps(dct).encode())
					except Exception as e:
						self.send_error(500, str(e))
				else:
					self.send_error(404, 'Invalid URL')

		server = HTTPServer((args.addr,args.port), myHandler)
		server.socket = ssl.wrap_socket (server.socket, certfile='./server.pem', server_side=True)
		print("Started HTTP server on port {}".format(args.port))

		server.serve_forever()

	elif args.formula:

		p = PropositionLogic(args.formula)

		print(p.getTruethFunction(pandas=args.pandas))
