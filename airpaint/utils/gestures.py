import math

def dist(a, b):
    """
    Calcula a distância euclidiana entre dois landmarks (a e b),
    usando apenas as coordenadas x e y.

    Nota:
    - a.x, a.y e b.x, b.y são coordenadas normalizadas (0..1) típicas do MediaPipe.
    - math.dist recebe duas listas com as coordenadas e devolve a distância.
    """
    return math.dist([a.x, a.y], [b.x, b.y])

def fingers_up(lm):
    """
    Conta quantos dedos (indicador, médio, anelar, mindinho) estão levantados.

    Estratégia:
    - Usa os índices dos 'tips' (pontas dos dedos): 8, 12, 16, 20.
    - Compara a coordenada y da ponta (tip) com a da articulação 2 nós abaixo (tip-2).
      Se tip.y < (tip-2).y, o dedo está "para cima" (mais alto na imagem).

    Retorno:
    - int: número de dedos levantados (0 a 4).
    """
    if lm is None:
        return 0
    tips = [8, 12, 16, 20]
    count = 0
    for tip in tips:
        if lm[tip].y < lm[tip - 2].y:
            count += 1
    return count

def pinch(lm):
    """
    Deteta o gesto de 'pinça' (polegar + indicador próximos).

    Estratégia:
    - Calcula a distância entre:
      - landmark 4 (ponta do polegar)
      - landmark 8 (ponta do indicador)
    - Se a distância for menor que um limiar (0.045), considera pinça.

    Retorno:
    - bool: True se estiver em pinça, False caso contrário.
    """
    if lm is None:
        return False
    return dist(lm[4], lm[8]) < 0.045

def one_finger(lm):
    """
    Verifica se há exatamente 1 dedo levantado.
    """
    return lm is not None and fingers_up(lm) == 1

def two_fingers(lm):
    """
    Verifica se há exatamente 2 dedos levantados.
    """
    return lm is not None and fingers_up(lm) == 2

def three_fingers(lm):
    """
    Verifica se há exatamente 3 dedos levantados.
    """
    return lm is not None and fingers_up(lm) == 3

def four_fingers(lm):
    """
    Verifica se há exatamente 4 dedos levantados.
    """
    return lm is not None and fingers_up(lm) == 4

def is_fist(lm):
    """
    Deteta se a mão está em punho (fist).

    Estratégia:
    - Usa os mesmos 'tips' dos dedos (8, 12, 16, 20).
    - Considera um dedo "fechado" se a ponta estiver abaixo (y maior) do nó 2 abaixo (tip-2):
      lm[tip].y > lm[tip-2].y
    - Se pelo menos 3 dedos estiverem fechados, assume punho.

    Retorno:
    - bool: True se for punho, False caso contrário.
    """
    if lm is None:
        return False
    tips = [8, 12, 16, 20]
    closed = 0
    for tip in tips:
        if lm[tip].y > lm[tip - 2].y:
            closed += 1
    return closed >= 3