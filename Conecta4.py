class Jogador:
    def __init__(self, idnt, tipo="humano", pesos=None):
        self.id = idnt
        self.tipo = tipo
        self.pesos = pesos or [0.0, 0.0, 0.0]

    def escolher_jogada(self, tabuleiro, _):
        if self.tipo == "humano":
            tabuleiro.imprimir()
            while True:
                try:
                    col = int(input(f"Jogador {self.id}, escolha uma coluna (0-{tabuleiro.cols - 1}): "))
                    if tabuleiro.jogada_valida(col):
                        return col
                    print("Jogada inválida.")
                except ValueError:
                    print("Entrada inválida.")
        else:
            raise NotImplementedError("Apenas o jogadores do tipo humano.")

class Jogadores:
    def __init__(self, players: Jogador):
        self.players = players
        self.idx = 0

    def __iter__(self):
        return self

    def __next__ (self) -> Jogador:
        try:
            item = self.players[self.idx]
        except IndexError:
            self.idx = 0
            item = self.players[self.idx]
        self.idx += 1
        return item

    def atual(self):
        return self.players[self.idx]

class Tabuleiro:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.colunas = [[] for _ in range(cols)]

    def __repr__(self):
        return self.imprimir()

    def imprimir(self):
        for linha in reversed(range(self.rows)):
            print(" | ".join(
                str(self.colunas[col][linha]) if linha < len(self.colunas[col]) else "."
                for col in range(self.cols)
            ))
        print("-" * (self.cols * 4 - 1))
        print("   ".join(str(i) for i in range(self.cols)))

    def jogada_valida(self, col):
        return 0 <= col < self.cols and len(self.colunas[col]) < self.rows

    def aplicar_jogada(self, col, jogador):
        if not self.jogada_valida(col):
            return False
        self.colunas[col].append(jogador)
        if self.verificar_vitoria(len(self.colunas[col]) - 1, col, jogador):
            return f"Jogador {jogador} venceu!"
        elif self.verificar_empate():
            return "Jogo empatou!"

    def verificar_empate(self):
        return all(len(coluna) == self.rows for coluna in self.colunas)

    def verificar_vitoria(self, linha, coluna, jogador):
        def contar_em_direcao(_dx, _dy):
            count = 1
            for direcao in [1, -1]:
                x, y = linha, coluna
                while True:
                    x += direcao * _dx
                    y += direcao * _dy
                    if 0 <= x < self.rows and 0 <= y < self.cols:
                        if x < len(self.colunas[y]) and self.colunas[y][x] == jogador:
                            count += 1
                        else:
                            break
                    else:
                        break
            return count

        for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            if contar_em_direcao(dx, dy) >= 4:
                return True
        return False

    def contar_sequencias(self, jogador, tamanho):
        total = 0
        direcoes = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for col in range(self.cols):
            for lin in range(len(self.colunas[col])):
                for dx, dy in direcoes:
                    count = 0
                    vazio = 0
                    for i in range(4):
                        x = lin + i * dx
                        y = col + i * dy
                        if 0 <= y < self.cols and 0 <= x < self.rows:
                            if x < len(self.colunas[y]):
                                peca = self.colunas[y][x]
                                if peca == jogador:
                                    count += 1
                                elif peca == 0:
                                    vazio += 1
                                else:
                                    break
                            else:
                                vazio += 1
                        else:
                            break
                    if count == tamanho and count + vazio == 4:
                        total += 1
        return total

    def contar_linhas_abertas(self, jogador):
        total = 0
        direcoes = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for col in range(self.cols):
            for lin in range(len(self.colunas[col])):
                for dx, dy in direcoes:
                    bloqueado = False
                    for i in range(4):
                        x = lin + i * dx
                        y = col + i * dy
                        if 0 <= y < self.cols and 0 <= x < self.rows:
                            if x < len(self.colunas[y]):
                                peca = self.colunas[y][x]
                                if peca == 3 - jogador:
                                    bloqueado = True
                                    break
                        else:
                            bloqueado = True
                            break
                    if not bloqueado:
                        total += 1
        return total

    def contar_centro(self, jogador):
        centro = self.cols // 2
        score = 0
        for peca in self.colunas[centro]:
            if peca == jogador:
                score += 1
        return score

    def avaliar_estado(self, jogador):
        w1, w2, w3 = jogador.pesos  # linhas abertas, trincas, centro
        linhas_abertas = self.contar_linhas_abertas(jogador.id)
        trincas = self.contar_sequencias(jogador.id, 3)
        centro = self.contar_centro(jogador.id)
        return w1 * linhas_abertas + w2 * trincas + w3 * centro


def jogo(players):
    tabuleiro = Tabuleiro()
    _jogadores = Jogadores(players)

    for each in _jogadores:
        col = each.escolher_jogada(tabuleiro, 0)

        jogada = tabuleiro.aplicar_jogada(col, each.id)

        if jogada:
            if each.tipo == 'humano':
                tabuleiro.imprimir()
                print(jogada)
            break


if __name__ == '__main__':
    jogadores = [Jogador(1), Jogador(2)]
    jogo(jogadores)
