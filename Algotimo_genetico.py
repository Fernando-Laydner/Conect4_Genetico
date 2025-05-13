import random
import matplotlib.pyplot as plt
from tqdm import tqdm
from copy import deepcopy

# =======================
# Classe Tabuleiro
# =======================
from Conecta4 import Tabuleiro, Jogador, Jogadores

class Player(Jogador):

    def __init__(self, idx, tipo="minmax", pesos=None):
        super().__init__(idx)
        self.tipo = tipo
        self.pesos = pesos or [0.0, 0.0, 0.0]

    def escolher_jogada(self, tabuleiro, jogadores):
        if self.tipo in ["minmax", "baseline"]:
            _, jogada = minmax_com_poda_alfa_beta(
                tabuleiro,
                profundidade=PROFUNDIDADE_MAXIMA,
                alfa=float('-inf'),
                beta=float('inf'),
                jogadores=jogadores
            )
            return jogada
        else:
            raise ValueError("Tipo de jogador inválido")


# =======================
# Algoritmo Min-Max com Poda Alfa-Beta
# =======================
def minmax_com_poda_alfa_beta(tabuleiro, profundidade, alfa, beta, jogadores):
    jogador_max = jogadores.players[0]
    jogador_min = jogadores.players[1]

    def max_valor(tab, prof, _alfa, _beta):
        if prof == 0 or tab.verificar_empate():
            return tab.avaliar_estado(jogador_max), None

        max_score = float('-inf')
        melhor_mov = None

        for col in range(tab.cols):
            if not tab.jogada_valida(col):
                continue

            copia = deepcopy(tab)
            resultado = copia.aplicar_jogada(col, jogador_max.id)
            if resultado and "venceu" in resultado:
                return float('inf'), col

            score, _ = min_valor(copia, prof - 1, _alfa, _beta)

            if score > max_score:
                max_score = score
                melhor_mov = col

            _alfa = max(_alfa, score)
            if _alfa >= _beta:
                break  # Poda

        return max_score, melhor_mov

    def min_valor(tab, prof, _alfa, _beta):
        if prof == 0 or tab.verificar_empate():
            return tab.avaliar_estado(jogador_min), None

        min_score = float('inf')
        melhor_mov = None

        for col in range(tab.cols):
            if not tab.jogada_valida(col):
                continue

            copia = deepcopy(tab)
            resultado = copia.aplicar_jogada(col, jogador_min.id)
            if resultado and "venceu" in resultado:
                return float('-inf'), col

            score, _ = max_valor(copia, prof - 1, _alfa, _beta)

            if score < min_score:
                min_score = score
                melhor_mov = col

            _beta = min(_beta, score)
            if _alfa >= _beta:
                break  # Poda

        return min_score, melhor_mov

    return max_valor(tabuleiro, profundidade, alfa, beta)


# =======================
# Simulação Realista de Partida
# =======================
def simular_jogadas(tabuleiro, _jogadores, numero_jogadas=3):
    copia = deepcopy(tabuleiro)

    for each in _jogadores:
        if numero_jogadas == 0:
            break

        col = each.escolher_jogada(copia)

        jogada = copia.aplicar_jogada(col, each.id)
        numero_jogadas -= 1



def simular_partida(pesos_agente):
    tabuleiro = Tabuleiro()
    jogador1 = Player(1, tipo="minmax", pesos=pesos_agente)
    jogador2 = Player(2, tipo="baseline")
    _jogadores = Jogadores([jogador1, jogador2])

    for each in _jogadores:
        melhor_jogada = each.escolher_jogada(tabuleiro, _jogadores)

        if melhor_jogada is None:
            return 0.5

        jogada = tabuleiro.aplicar_jogada(melhor_jogada, each.id)

        if jogada:
            if "venceu" in jogada:
                return 1.0 if each.id == jogador1.id else 0.0
            elif "empatou" in jogada:
                return 0.5


# =======================
# Avaliação do Fitness
# =======================
def avaliar_individuo(pesos):
    vitorias = 0
    total_jogos = 20
    for _ in range(total_jogos):
        vitorias += simular_partida(pesos)
    return vitorias / total_jogos


# =======================
# Algoritmo Genético
# =======================
def algoritmo_genetico(populacao_tamanho=4, geracoes=4, taxa_mutacao=0.8, taxa_crossover=0.7):
    historico_fitness = []

    populacao = [
        [random.uniform(-1, 1) for _ in range(3)]
        for _ in range(populacao_tamanho)
    ]

    for geracao in tqdm(range(geracoes), desc="Evoluindo Gerações"):
        fitness = [avaliar_individuo(ind) for ind in populacao]
        historico_fitness.append(max(fitness))

        nova_populacao = []
        elite = populacao[fitness.index(max(fitness))]
        nova_populacao.append(elite[:])

        while len(nova_populacao) < populacao_tamanho:
            def torneio():
                a, b = random.sample(range(populacao_tamanho), 2)
                return populacao[a] if fitness[a] > fitness[b] else populacao[b]

            pai1, pai2 = torneio(), torneio()

            if random.random() < taxa_crossover:
                ponto = random.randint(1, len(pai1) - 1)
                filho = pai1[:ponto] + pai2[ponto:]
            else:
                filho = pai1[:]

            for i in range(len(filho)):
                if random.random() < taxa_mutacao:
                    filho[i] += random.uniform(-0.3, 0.3)

            nova_populacao.append(filho)

        if len(nova_populacao) > 1:
            nova_populacao[-1] = [random.uniform(-1, 1) for _ in range(3)]

        populacao = nova_populacao[:]
        melhor_fitness = max(fitness)
        melhor_indice = fitness.index(melhor_fitness)
        melhor_pesos = populacao[melhor_indice]
        print(f"Geração {geracao}: Melhor fitness = {melhor_fitness:.2f} | Pesos = {melhor_pesos}")

    plt.plot(historico_fitness)
    plt.title("Evolução do Fitness Máximo")
    plt.xlabel("Geração")
    plt.ylabel("Fitness")
    plt.grid()
    plt.show()

    return historico_fitness

PROFUNDIDADE_MAXIMA = 3

algoritmo_genetico()