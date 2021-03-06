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


def run(formula_original, truth_table):
	atomics = 0
	operations = 0
	negations = 0
	repetitions = []
	formula_original = formula_original.replace(' ', '')
	formula_original = formula_original.replace('∨', '|')
	formula_original = formula_original.replace('→', '>')
	formula_original = formula_original.replace('∧', '&')
	formula_original = formula_original.replace('¬', '~')
	formula = list(formula_original)
	table = list(truth_table)
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
	parenteses = 0

	# lê a formula, contando cada coisa
	# O(n)
	for element in formula:
		if element == '~':
			#lidando apenas com a negação de clausulas atomicas. Qualquer negação maior devem ser aplicadas as De Morgan Laws
			negations = negations + 1
		elif element == '|' or element == '&' or element == '>': #aqui deve entrar qualquer uma das operações
   			operations = operations + 1
		elif element == '(' or element == ')':
			parenteses = parenteses + 1
		else:
   			atomics = atomics + 1
   			repetitions.append(element)

	print("Atomicos: ", end = '')
	print(atomics)
	print("operations: ", end = '')
	print(operations)
	
	#print(repetitions)
   	
	full_size = negations + operations + atomics + parenteses
	size = operations + atomics + parenteses
	# cria o numero de qubits adequado
	qubits = cirq.LineQubit.range(size)
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
	indexator = list(range(size))

	#faz as operações lógicas
	#associação a esquerda, não aceita parênteses por enquanto
	print(formula_use)
	print(formula)

	#passada inicial, lidando com os parenteses:
	print(indexator)
	print("ENTRANDO -------------")

	has_parenteses = 1
	i = 0
	while len(indexator) > 1 and has_parenteses == 1:
		has_parenteses = 0
		for i in range(len(indexator)):
			if formula_use[indexator[i]] == '(': #achou o abre parenteses
				print(" ABRIU -------------")
				has_parenteses = 1
				start = i
				while formula_use[indexator[i]]  != ')': #procura o fecha parênteses
					i = i + 1
					if formula_use[indexator[i]] == '(':# achou outro abre parênteses, atualiza o start
						start = i	
				print("FECHOU ---------")			
				#quando saiu do while, está no primeiro ')' - assumindo que a afirmação está bem formada (numero equilibrado de parenteses)
				#destruir os parenteses antes
				internal_count = i - start - 1
				print(indexator)
				del indexator[start]
				del indexator[i - 1]
				print(indexator)
				create_circuit(formula_use, circuit, qubits, indexator, start, start + internal_count)
				print("CHECK----------")
				print(i)
				print(indexator)
				break
		#if i >= len(indexator):
		#	i = 0
	print("SAINDO ------------------------")
	print(formula_use)
	print(indexator)
	create_circuit(formula_use, circuit, qubits, indexator, 0, len(indexator) - 1)

	print(indexator)

	print(circuit)
	simulator = Simulator()	
	result = simulator.simulate(circuit, initial_state=000000000000000)
	print(result.dirac_notation())
	string_result = str(result.dirac_notation())
	original_ones = 0
	original_zeros = 0
	for i in range(len(table)):
		if table[i] == 0:
			original_zeros = original_zeros + 1
		else:
			original_ones = original_ones + 1
	ones = 0
	zeros = 0
	temp_parenteses = 0
	for i in range(indexator[0]):
		if formula_use[i] == ')' or formula_use[i] == '(':
			temp_parenteses = temp_parenteses + 1
	for i in range(len(string_result)):
		if string_result[i] == "|":
			if int(string_result[i + indexator[0] + 1 - temp_parenteses]) == 0:
				zeros = zeros + 1
			else:
				ones = ones + 1

	print("Truth Table Ones/Zeros:", end = ' ')
	print(original_ones, end = '/')
	print(original_zeros)
	print("Circuit Result:")
	print("Ones:", end = '')
	print(ones)
	print("Zeros:", end='')
	print(zeros)
	
def create_circuit(formula, circuit, qubits, indexator, start, end):
		size = end - start #calcula o tamanho do que está entre parênteses

		print("CREATE CIRCUIT CALLED ---------------------")
		#print(formula)
		print(start)
		print(end)
		i = start
		while i < end and len(indexator) > 1 and size > 1:
			print(i)
			print(indexator)
			print(formula)
			if formula[indexator[i]] == '(' or formula[indexator[i]] == ')':
				print("ERRO")
				exit()
			if formula[indexator[i]] == '|':
				circuit.append(cirq.X(qubits[indexator[i]])) #flipa o bit auxiliar, setado em 0
				circuit.append(cirq.FREDKIN(qubits[indexator[i - 1]], qubits[indexator[i + 1]], qubits[indexator[i]])) #faz o gate de Fredkin em OR
				#resultado está em qubits[i + 1]
				del indexator[i - 1]
				del indexator[i - 1]
				size = size - 2
			elif formula[indexator[i]] == '&':
				formula[indexator[i]] = '_'
				circuit.append(cirq.FREDKIN(qubits[indexator[i - 1]], qubits[indexator[i + 1]], qubits[indexator[i]])) #faz o gate de Fredkin em AND
				#resultado está em qubits[i]
				del indexator[i - 1]
				del indexator[i]
				size = size - 2
			elif formula[indexator[i]] == '>': #flipa o resultado atual a faz o OR
				print("IMPLICATION")
				circuit.append(cirq.X(qubits[indexator[i - 1]]))
				circuit.append(cirq.X(qubits[indexator[i]]))
				circuit.append(cirq.FREDKIN(qubits[indexator[i - 1]], qubits[indexator[i + 1]], qubits[indexator[i]])) #faz o gate de Fredkin em OR
				del indexator[i - 1]
				del indexator[i - 1]
				size = size - 2
			else:
				i = i + 1
		print("CREATE CIRCUIT FINISHED ---------------------")



def remove_values(the_list, val):
   return [value for value in the_list if value != val]


#run("(A | B) > (C & A)")
#run("((A | B) > (~B | C | A)) > C")
#run("(P → (Q → R)) → ((P → Q) → (P → R))")
#run("(A ∧ B) → (P ∧ ((R ∨ ¬A) ∨ (¬P ∧ Q)) → A)")
#run("(A ∧ B) → (P ∧ ((R ∨ ¬A) ∨ (¬P ∧ Q)) → A ∨ (H ∧ A))", "")
