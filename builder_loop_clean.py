import cirq
import numpy as np
from cirq import Simulator
from collections import Counter

#x -> y = ~x | y
#aplicar um fredkin gate com o Aux setado em 1 é um OR, com resultado em B
#aplicar um fredkin gate com o Aux setado em 0 é um AND, com resultado em Aux

#input: formula a ser verificada se é TAUT

#Para cada símbolo atômico, será criado 1 qubit. Caso um símbolo atômico seja repetido, é feito o entrelaçamento
#entre um numero de qubits igual ao numero de repetições

#Para cada conector lógico é criado um Qubit auxiliar

#Os simbolos lógicos usados são: |, &, > e ~. Na falta de parenteses, associação feita sempre a esquerda.

#O iff ainda não é suportado. 

#O algoritmo mostra a distribuição da tabela verdade de uma expressão lógica

#Complexidade O(n^2) - parte clássica
#Parte quântica?

#ARGS:
#formula_original: A formula a ser verificada
#truth_table: a distribuição de 0s e 1s da tabela verdade da formula (OPCIONAL)

def run(formula_original, truth_table = ""):


	# Troca simbolos logicos comuns pelos equivalentes esperados
	formula_original = formula_original.replace(' ', '')
	formula_original = formula_original.replace('∨', '|')
	formula_original = formula_original.replace('→', '>')
	formula_original = formula_original.replace('∧', '&')
	formula_original = formula_original.replace('¬', '~')
	formula = list(formula_original)
	table = list(truth_table)

	parenteses = 0
	atomics = 0
	operations = 0
	negations = 0

	# lê a formula, contando cada elemento
	# O(n)
	for element in formula:
		if element == '~':
			negations = negations + 1
		elif element == '|' or element == '&' or element == '>': #aqui deve entrar qualquer uma das operações
   			operations = operations + 1
		elif element == '(' or element == ')':
			parenteses = parenteses + 1
		else:
   			atomics = atomics + 1
	
   	
	full_size = negations + operations + atomics + parenteses
	size = operations + atomics + parenteses

	# cria o numero de qubits adequado e o circuito
	qubits = cirq.LineQubit.range(size)
	circuit = cirq.Circuit()

	size2 = len(formula)

	# checa se há alguma inconsistência na contagem
	if full_size != size2:
		print("Erro nos tamanhos")
		exit()


	# entrelaça os qubits necessários
	# ignora as negações, que serão lidadas com mais para frente
	formula_use = remove_values(formula, '~')
	#O(n), maximo de ligações é n
	for i in range(size):
		if not str(formula_use[i]).isalnum(): # se não for alfanumérico, ignora
			continue
		circuit.append(cirq.H(qubits[i])) # aplica o Hadamard no primeiro qubit encontrado para cada clausula atomica 
		for j in range(i + 1, size): # procura no resto da formula outras instâncias da clausula atomica
			if (formula_use[i] == formula_use[j]):
				circuit.append([cirq.CNOT(qubits[i], qubits[j])]) # entrelaça as que encontrar com a primeira
				formula_use[j] = "_"
		formula_use[i] = "_" 

	# verifica as clausulas que estão negadas, e faz o bit flip
	#O(n)
	neg_count = 0
	for i in range(full_size):
		if formula[i] == '~':
			if formula[i + 1] == '(': #negações aparecem antes de ( ou antes de uma clausula atomica
				formula_use[i - neg_count] = '[' #troca a representação do parenteses negado
				neg_count = neg_count + 1 
			else:
				circuit.append(cirq.X(qubits[i - neg_count]))
				neg_count = neg_count + 1


	# cria uma lista de inteiros para servir de referência a quais qubits ainda estão com informação importante
	indexator = list(range(size))

	# procura os parenteses mais internos, e chama a função de criar circuito

	has_parenteses = 1
	i = 0
	print(formula_use)
	#O(n^2)
	while len(indexator) > 1 and has_parenteses == 1: # quando o tamanho de indexador é 1, o algoritmo terminou, e o resultado está no qubit com o indice restante
		has_parenteses = 0
		for i in range(len(indexator)):
			negated = 0
			if formula_use[indexator[i]] == '(' or formula_use[indexator[i]] == '[': #achou o abre parenteses
				if formula_use[indexator[i]] == '[':
					negated = 1
				has_parenteses = 1
				start = i
				while formula_use[indexator[i]]  != ')': #procura o fecha parênteses
					i = i + 1
					if formula_use[indexator[i]] == '(' or formula_use[indexator[i]] == '[':# achou outro abre parênteses, atualiza o start
						start = i
						negated = 0
						if formula_use[indexator[i]] == '[':
							negated = 1	
				#quando saiu do while, está no primeiro ')' - assumindo que a afirmação está bem formada (numero equilibrado de parenteses)
				internal_count = i - start - 1
				#remove os parenteses
				del indexator[start]
				del indexator[i - 1]
				create_circuit(formula_use, circuit, qubits, indexator, start, start + internal_count, negated)
				break

	#chama a funçao uma ultima vez, quando nao houver mais nenhum parenteses
	create_circuit(formula_use, circuit, qubits, indexator, 0, len(indexator) - 1, 0)

	# a resposta esta no qubit[indexador[0]]
	print(indexator)
	print(circuit)

	simulator = Simulator()	
	result = simulator.simulate(circuit, initial_state=000000000000000)
	print(result.dirac_notation())
	string_result = str(result.dirac_notation())

	# conta os 0s e 1s do resultado da simulação e compara com os da truth table
	original_ones = 0
	original_zeros = 0
	for i in range(len(table)):
		if int(table[i]) == 0:
			original_zeros = original_zeros + 1
		elif int(table[i]) == 1:
			original_ones = original_ones + 1
	ones = 0
	zeros = 0
	temp_parenteses = 0
	for i in range(indexator[0]):
		if formula_use[i] == ')' or formula_use[i] == '(' or formula_use[i] == '[':
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
	
def create_circuit(formula, circuit, qubits, indexator, start, end, negated):
		size = end - start #calcula o tamanho do que está entre parênteses
		i = start
		current_result = -1
		while i < end and len(indexator) > 1 and size > 1:
			#print(i)
			#print(indexator)	
			if formula[indexator[i]] == '(' or formula[indexator[i]] == ')' or formula[indexator[i]] == '[':
				print("Erro: parentese encontrado fora do lugar")
				exit()
			if formula[indexator[i]] == '|':
				circuit.append(cirq.X(qubits[indexator[i]])) #flipa o bit auxiliar, setado em 0
				circuit.append(cirq.FREDKIN(qubits[indexator[i - 1]], qubits[indexator[i + 1]], qubits[indexator[i]])) #faz o gate de Fredkin em OR
				#resultado está em qubits[i + 1]
				current_result = indexator[i + 1]
				del indexator[i - 1]
				del indexator[i - 1]
				size = size - 2
			elif formula[indexator[i]] == '&':
				formula[indexator[i]] = '_'
				circuit.append(cirq.FREDKIN(qubits[indexator[i - 1]], qubits[indexator[i + 1]], qubits[indexator[i]])) #faz o gate de Fredkin em AND
				#resultado está em qubits[i]
				current_result = indexator[i]
				del indexator[i - 1]
				del indexator[i]
				size = size - 2
			elif formula[indexator[i]] == '>': #flipa o resultado atual a faz o OR
				circuit.append(cirq.X(qubits[indexator[i - 1]]))
				circuit.append(cirq.X(qubits[indexator[i]]))
				circuit.append(cirq.FREDKIN(qubits[indexator[i - 1]], qubits[indexator[i + 1]], qubits[indexator[i]])) #faz o gate de Fredkin em OR
				current_result = indexator[i + 1]
				del indexator[i - 1]
				del indexator[i - 1]
				size = size - 2
			else:
				i = i + 1
		if negated == 1:
			circuit.append(cirq.X(qubits[current_result]))


def remove_values(the_list, val):
   return [value for value in the_list if value != val]


#run("(A | B) > (C & A)")
#run("((A | B) > (~B | C | A)) > C")
#run("(P → (Q → R)) → ((P → Q) → (P → R))")
#run("(A ∧ B) → (P ∧ ((R ∨ ¬A) ∨ (¬P ∧ Q)) → A)", "")
#run("(A ∧ B) → (P ∧ ((R ∨ ¬A) ∨ (¬P ∧ Q)) → A ∨ (H ∧ A))", "")
#run("A → (¬(P ∨ U) ∨ ¬(A ∧ P))","00111111")
#run("¬((A → (¬(P ∨ U) ∨ ¬(A ∧ P))) → ¬(¬(P ∨ ¬U) → P))")
#run("¬((A → (¬(P ∨ U) ∨ ¬(A ∧ P))) → ¬(E → P))")
#run("¬((A → (¬(B ∨ C) ∨ ¬(D ∧ E))) → ¬(G → H))")
#run("¬(A→¬(B ∨ C) ∨ ¬(D∧E) → ¬(G → H)) ∨ (P > S)", "10111011101110111111101111111111111110111111111111111011111111111011101110111011111110111111111111111011111111111111101111111111101110111011101111111011111111111111101111111111111110111111111111111011111111111111101111111111111110111111111111111011111111111111101111111111111110111111111111111011111111111111101111111111111110111111111111111011111111111111101111111111111110111111111111111011111111111111101111111111111110111111111111111011111111111111101111111111111110111111111111111011111111111111101111111111")
run("A&B&C&~A")