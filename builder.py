import cirq
import numpy as np
from cirq import Simulator
from collections import Counter

#((C ∨ D) ∧ (C → E)) ∨ ¬(C ∨ D) ∨ ¬(C → E)
#x -> y = ~x | y
#aplicar um fredkin gate com o Aux setado em 1, ou seja, um OR, com resultado em B
#aplicar um fredkin gate com o Aux setado em 0, ou seja, um AND, com resultado em Aux

#input: formula a ser verificada se é TAUT

#Para cada símbolo atômico, será criado 1 qubit. Caso um símbolo atômico seja repetido, é feito o entrelaçamento
#entre um numero de qubits igual ao numero de repetições

#Para cada conector lógico é criado um Qubit auxiliar

#Os simbolos lógicos usados são: |, &, > e ~. Por enquanto, não suporta o uso de parenteses, associação feita sempre a esquerda.

#Tirando a negação, nunca haverá duas letras ou simbolos logicos adjacentes

#O algoritmo mostra a distribuição da tabela verdade de uma expressão lógica

#Complexidade O(n)?! P = NP? kkkkkk

def run(formula_original):
	atomics = 0
	operations = 0
	negations = 0
	repetitions = []
	formula_original = formula_original.replace(' ', '')
	formula = list(formula_original)
	print(formula)

	#tranforma x > y em ~x | y #ERRO ESTÁ AQUI. A associação é a esquerda, mas o caso (x | y) -> z está vendo traduzido
	#como x | ~y | z, quando na verdade deve ser ~(x | y) | z
	# O(n)

	"""
	for i in range(len(formula)):
		if formula[i] == '>':
			formula[i] = '|'
			formula.insert(i - 1, '~')
	"""
	print(formula)

	# lê a formula, contando cada coisa
	# O(n)
	for element in formula:
		if element == '~':
			#lidando apenas com a negação de clausulas atomicas. Qualquer negação maior devem ser aplicadas as De Morgan Laws
			negations = negations + 1
		elif element == '|' or element == '&' or element == '>': #aqui deve entrar qualquer uma das operações
   			operations = operations + 1
		else:
   			atomics = atomics + 1
   			repetitions.append(element)

	print("Atomicos: ", end = '')
	print(atomics)
	print("operations: ", end = '')
	print(operations)
	
	#print(repetitions)
   	
	full_size = negations + operations + atomics
	size = operations + atomics
	# cria o numero de qubits adequado
	qubits = cirq.LineQubit.range(operations + atomics)
	circuit = cirq.Circuit()
	size2 = len(formula)
	#print(len(formula))
	#print(full_size)
	if full_size != size2:
		print("Erro nos tamanhos!")
		exit()

	


	# entrelaça os qubits necessários
	# ignora as negations, que serão lidadas com mais para frente
	uniques = 0
	formula_use = remove_values(formula, '~')
	#O(n), maximo de ligações é N
	for i in range(size):
		if not str(formula_use[i]).isalnum():
			#print(formula_use[i])
			continue
		uniques = uniques + 1
		circuit.append(cirq.H(qubits[i]))
		for j in range(i + 1, size):
			if (formula_use[i] == formula_use[j]):
				circuit.append([cirq.CNOT(qubits[i], qubits[j])])
				formula_use[j] = "_"
		formula_use[i] = "_" 

	#Cuida das negations
	#O(n)
	neg_count = 0
	for i in range(full_size):
		if formula[i] == '~':
			circuit.append(cirq.X(qubits[i - neg_count]))
			neg_count = neg_count + 1
	indexator = list(range(0, size))

	#faz as operações lógicas
	#associação a esquerda, não aceita parênteses por enquanto
	i = 0 
	print(formula_use)
	#O(n)
	while len(indexator) > 1:
		#print(i)
		#print(indexator)
		if formula_use[indexator[i]] == '|':
			#print(i)
			#print(indexator[i])			
			circuit.append(cirq.X(qubits[indexator[i]])) #flipa o bit auxiliar, setado em 0
			circuit.append(cirq.FREDKIN(qubits[indexator[i - 1]], qubits[indexator[i + 1]], qubits[indexator[i]])) #faz o gate de Fredkin em OR
			#resultado está em qubits[i + 1]
			del indexator[i - 1]
			del indexator[i - 1]
			#print(indexator)
		elif formula_use[indexator[i]] == '&':
			#print(i)
			#print(indexator[i])	
			circuit.append(cirq.FREDKIN(qubits[indexator[i - 1]], qubits[indexator[i + 1]], qubits[indexator[i]])) #faz o gate de Fredkin em AND
			#resultado está em qubits[i]
			del indexator[i - 1]
			del indexator[i]
		elif formula_use[indexator[i]] == '>': #flipa o resultado atual a faz o OR 
			circuit.append(cirq.X(qubits[indexator[i - 1]]))
			circuit.append(cirq.X(qubits[indexator[i]]))
			circuit.append(cirq.FREDKIN(qubits[indexator[i - 1]], qubits[indexator[i + 1]], qubits[indexator[i]])) #faz o gate de Fredkin em OR
			del indexator[i - 1]
			del indexator[i - 1]
		else:
			i = i + 1
	print(indexator)

	print(circuit)
	simulator = Simulator()	
	result = simulator.simulate(circuit, initial_state=000000000000000)
	print(result.dirac_notation())
	string_result = str(result.dirac_notation())
	ones = 0
	zeros = 0
	for i in range(len(string_result)):
		if string_result[i] == "|":
			if int(string_result[i+indexator[0]+1]) == 0:
				zeros = zeros + 1
			else:
				ones = ones + 1
	print("Ones:", end = '')
	print(ones)
	print("Zeros:", end='')
	print(zeros)
	



def remove_values(the_list, val):
   return [value for value in the_list if value != val]

#run("C | B & ~C | E | ~C | ~D | C | ~E") #OK 
#run("C | B & C > E | ~C | ~D | ~C > ~E") #OK
#run("A | B > ~B | C | A > ~C")		  	#OK ((((A ∨ B) → ¬B) ∨ C ∨ A) → ¬C) TV: 4/4
#run("A | E > B | C | A > C")		  	#OK (((((A | E) → B) | C) | A) → C) TV: 9/7
#run("A | B > E | C | A") 				#OK (((A ∨ B) → ¬B) ∨ C ∨ A) TV: 15/1
#run("A | B > ~B | C | A > C")			#OK ((((A | B) → ¬B) | C) | A) → C TV: 5/3
#run("A | B > B | C | A > C")			#OK ((((A | B) → B) | C) | A) → C TV: 4/4
#run("A | B & ~E | B | ~C | A & C | D & E")	#OK TV: 11/21
#run("A | B & E | B | C | A & C | D & E") #OK TV: 12/20
#run("A | B > D & E | ~C > D & ~A | G > ~B") #OK ((((((((A v B) -> D) & E) v ~C) -> D) & ~A) v G) -> ~B) TV: 42/22