import os
import subprocess
import math
from collections import deque


# ============================================================
# CONFIGURAÇÃO
# ============================================================

TAMANHO_MAXIMO = 320

GESTO_FIST = "FIST"
GESTO_OPEN_PALM = "OPEN_PALM"
GESTO_UNKNOWN = "UNKNOWN"

ARQUIVO_DEBUG = "gesto_detectado.png"
ARQUIVO_MASCARA = "gesto_mascara.png"


# ============================================================
# IMAGEM
# ============================================================

def obter_tamanho_imagem(arquivo):

    resultado = subprocess.run(
        [
            "magick",
            arquivo,
            "-resize",
            f"{TAMANHO_MAXIMO}x{TAMANHO_MAXIMO}",
            "-format",
            "%w %h",
            "info:"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if resultado.returncode != 0:

        print(
            "❌ ERRO AO OBTER TAMANHO DA IMAGEM"
        )

        print(
            resultado.stderr
        )

        return None

    try:

        largura, altura = map(
            int,
            resultado.stdout.strip().split()
        )

        return largura, altura

    except Exception:

        return None


# ============================================================
# CARREGAR RGB
# ============================================================

def carregar_rgb(arquivo, largura, altura):

    resultado = subprocess.run(
        [
            "magick",
            arquivo,
            "-resize",
            f"{TAMANHO_MAXIMO}x{TAMANHO_MAXIMO}",
            "-depth",
            "8",
            "rgb:-"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if resultado.returncode != 0:

        print(
            "❌ ERRO AO LER RGB"
        )

        try:

            print(
                resultado.stderr.decode(
                    errors="ignore"
                )
            )

        except Exception:

            pass

        return None

    dados = resultado.stdout

    esperado = largura * altura * 3

    if len(dados) < esperado:

        print()
        print(
            "❌ DADOS RGB INCOMPLETOS"
        )

        print(
            "ESPERADO:",
            esperado
        )

        print(
            "RECEBIDO:",
            len(dados)
        )

        return None

    return dados


# ============================================================
# PIXEL
# ============================================================

def pixel_rgb(dados, largura, x, y):

    indice = (
        (y * largura + x)
        * 3
    )

    return (
        dados[indice],
        dados[indice + 1],
        dados[indice + 2]
    )


# ============================================================
# DETECÇÃO DE PELE
# ============================================================

def pixel_eh_pele(r, g, b):

    maior = max(
        r,
        g,
        b
    )

    menor = min(
        r,
        g,
        b
    )

    saturacao = maior - menor

    # --------------------------------------------------------
    # Regras simples.
    #
    # Não dependemos de uma cor específica.
    # A ideia é encontrar regiões com:
    #
    # R >= G >= B
    #
    # e alguma diferença entre as cores.
    # --------------------------------------------------------

    if r < 25:
        return False

    if g < 12:
        return False

    if b < 5:
        return False

    if r < g:
        return False

    if g < b:
        return False

    if saturacao < 8:
        return False

    if (r - b) < 10:
        return False

    return True


# ============================================================
# CRIAR MÁSCARA
# ============================================================

def criar_mascara(dados, largura, altura):

    mascara = bytearray(
        largura * altura
    )

    # --------------------------------------------------------
    # Evitamos a parte superior da foto.
    #
    # Isso ajuda a não confundir rosto/cabelo com a mão.
    # --------------------------------------------------------

    inicio_y = int(
        altura * 0.42
    )

    inicio_x = int(
        largura * 0.08
    )

    fim_x = int(
        largura * 0.92
    )

    quantidade = 0

    for y in range(
        inicio_y,
        altura
    ):

        for x in range(
            inicio_x,
            fim_x
        ):

            r, g, b = pixel_rgb(
                dados,
                largura,
                x,
                y
            )

            if pixel_eh_pele(
                r,
                g,
                b
            ):

                mascara[
                    y * largura + x
                ] = 1

                quantidade += 1

    print(
        "PIXELS DE PELE:",
        quantidade
    )

    return mascara


# ============================================================
# COMPONENTES CONECTADOS
# ============================================================

def encontrar_componentes(
    mascara,
    largura,
    altura
):

    visitado = bytearray(
        largura * altura
    )

    componentes = []

    for y in range(
        altura
    ):

        for x in range(
            largura
        ):

            indice = (
                y * largura + x
            )

            if not mascara[indice]:
                continue

            if visitado[indice]:
                continue

            fila = deque()

            fila.append(
                (x, y)
            )

            visitado[indice] = 1

            pontos = []

            min_x = x
            max_x = x
            min_y = y
            max_y = y

            while fila:

                px, py = fila.popleft()

                pontos.append(
                    (px, py)
                )

                if px < min_x:
                    min_x = px

                if px > max_x:
                    max_x = px

                if py < min_y:
                    min_y = py

                if py > max_y:
                    max_y = py

                vizinhos = (
                    (px - 1, py),
                    (px + 1, py),
                    (px, py - 1),
                    (px, py + 1),
                    (px - 1, py - 1),
                    (px + 1, py - 1),
                    (px - 1, py + 1),
                    (px + 1, py + 1),
                )

                for nx, ny in vizinhos:

                    if nx < 0:
                        continue

                    if ny < 0:
                        continue

                    if nx >= largura:
                        continue

                    if ny >= altura:
                        continue

                    ni = (
                        ny * largura + nx
                    )

                    if not mascara[ni]:
                        continue

                    if visitado[ni]:
                        continue

                    visitado[ni] = 1

                    fila.append(
                        (nx, ny)
                    )

            area = len(
                pontos
            )

            if area < 80:
                continue

            largura_componente = (
                max_x - min_x + 1
            )

            altura_componente = (
                max_y - min_y + 1
            )

            centro_x = (
                min_x + max_x
            ) / 2

            centro_y = (
                min_y + max_y
            ) / 2

            componentes.append(
                {
                    "pontos": pontos,
                    "area": area,
                    "x": min_x,
                    "y": min_y,
                    "w": largura_componente,
                    "h": altura_componente,
                    "cx": centro_x,
                    "cy": centro_y
                }
            )

    return componentes


# ============================================================
# ESCOLHER CANDIDATO
# ============================================================

def escolher_componente(
    componentes,
    largura,
    altura
):

    if not componentes:

        return None

    melhor = None
    melhor_score = -1

    centro_imagem_x = (
        largura / 2
    )

    for componente in componentes:

        area = componente["area"]

        cx = componente["cx"]
        cy = componente["cy"]

        # ----------------------------------------------------
        # Quanto mais próximo do centro horizontal,
        # melhor.
        # ----------------------------------------------------

        distancia_x = abs(
            cx - centro_imagem_x
        )

        score_centro = max(
            0,
            1 - (
                distancia_x
                /
                (largura / 2)
            )
        )

        # ----------------------------------------------------
        # Preferir região inferior.
        # ----------------------------------------------------

        score_inferior = max(
            0,
            min(
                1,
                (
                    cy
                    -
                    altura * 0.42
                )
                /
                (
                    altura * 0.58
                )
            )
        )

        # ----------------------------------------------------
        # Componentes maiores têm mais peso.
        # ----------------------------------------------------

        score_area = math.sqrt(
            area
        )

        # ----------------------------------------------------
        # Evitar componentes encostados
        # nas bordas.
        # ----------------------------------------------------

        penalidade = 0

        if componente["x"] <= 2:
            penalidade += 50

        if (
            componente["x"]
            +
            componente["w"]
            >= largura - 2
        ):
            penalidade += 50

        score = (
            score_area
            +
            score_centro * 70
            +
            score_inferior * 50
            -
            penalidade
        )

        if score > melhor_score:

            melhor_score = score
            melhor = componente

    print()
    print(
        "COMPONENTE ESCOLHIDO:"
    )

    print(
        "AREA:",
        melhor["area"]
    )

    print(
        "X:",
        melhor["x"]
    )

    print(
        "Y:",
        melhor["y"]
    )

    print(
        "W:",
        melhor["w"]
    )

    print(
        "H:",
        melhor["h"]
    )

    return melhor


# ============================================================
# DISTÂNCIA ENTRE RETÂNGULOS
# ============================================================

def distancia_caixas(a, b):

    ax1 = a["x"]
    ay1 = a["y"]

    ax2 = (
        a["x"]
        +
        a["w"]
    )

    ay2 = (
        a["y"]
        +
        a["h"]
    )

    bx1 = b["x"]
    by1 = b["y"]

    bx2 = (
        b["x"]
        +
        b["w"]
    )

    by2 = (
        b["y"]
        +
        b["h"]
    )

    dx = max(
        ax1 - bx2,
        bx1 - ax2,
        0
    )

    dy = max(
        ay1 - by2,
        by1 - ay2,
        0
    )

    return math.sqrt(
        dx * dx
        +
        dy * dy
    )


# ============================================================
# JUNTAR COMPONENTES PRÓXIMOS
# ============================================================

def juntar_componentes(
    componentes,
    principal
):

    selecionados = [
        principal
    ]

    limite = 55

    mudou = True

    while mudou:

        mudou = False

        for componente in componentes:

            if componente in selecionados:
                continue

            distancia = min(
                distancia_caixas(
                    componente,
                    outro
                )
                for outro in selecionados
            )

            # ------------------------------------------------
            # Não pegar coisas muito nas bordas.
            # ------------------------------------------------

            if componente["x"] <= 5:
                continue

            if (
                componente["x"]
                +
                componente["w"]
                >= 315
            ):
                continue

            if distancia <= limite:

                selecionados.append(
                    componente
                )

                mudou = True

    pontos = []

    for componente in selecionados:

        pontos.extend(
            componente["pontos"]
        )

    print()
    print(
        "COMPONENTES JUNTOS:",
        len(selecionados)
    )

    print(
        "PIXELS TOTAIS:",
        len(pontos)
    )

    return pontos


# ============================================================
# CONVEX HULL
# ============================================================

def cross(o, a, b):

    return (
        (a[0] - o[0])
        *
        (b[1] - o[1])
        -
        (a[1] - o[1])
        *
        (b[0] - o[0])
    )


def convex_hull(pontos):

    pontos = sorted(
        set(pontos)
    )

    if len(pontos) <= 2:

        return pontos

    inferior = []

    for ponto in pontos:

        while (
            len(inferior) >= 2
            and
            cross(
                inferior[-2],
                inferior[-1],
                ponto
            ) <= 0
        ):

            inferior.pop()

        inferior.append(
            ponto
        )

    superior = []

    for ponto in reversed(pontos):

        while (
            len(superior) >= 2
            and
            cross(
                superior[-2],
                superior[-1],
                ponto
            ) <= 0
        ):

            superior.pop()

        superior.append(
            ponto
        )

    return (
        inferior[:-1]
        +
        superior[:-1]
    )


# ============================================================
# DISTÂNCIA PONTO / LINHA
# ============================================================

def distancia_ponto_linha(
    ponto,
    inicio,
    fim
):

    x, y = ponto

    x1, y1 = inicio
    x2, y2 = fim

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:

        return math.sqrt(
            (x - x1) ** 2
            +
            (y - y1) ** 2
        )

    t = (
        (
            (x - x1) * dx
            +
            (y - y1) * dy
        )
        /
        (
            dx * dx
            +
            dy * dy
        )
    )

    t = max(
        0,
        min(
            1,
            t
        )
    )

    px = x1 + t * dx
    py = y1 + t * dy

    return math.sqrt(
        (x - px) ** 2
        +
        (y - py) ** 2
    )


# ============================================================
# SIMPLIFICAR POLIGONO
# ============================================================

def simplificar_poligono(
    pontos,
    epsilon
):

    if len(pontos) <= 3:

        return pontos

    maior_distancia = 0
    indice = 0

    inicio = pontos[0]
    fim = pontos[-1]

    for i in range(
        1,
        len(pontos) - 1
    ):

        distancia = distancia_ponto_linha(
            pontos[i],
            inicio,
            fim
        )

        if distancia > maior_distancia:

            maior_distancia = distancia
            indice = i

    if maior_distancia > epsilon:

        esquerda = simplificar_poligono(
            pontos[:indice + 1],
            epsilon
        )

        direita = simplificar_poligono(
            pontos[indice:],
            epsilon
        )

        return (
            esquerda[:-1]
            +
            direita
        )

    return [
        inicio,
        fim
    ]


def simplificar_hull(hull):

    if len(hull) < 3:
        return hull

    pontos = (
        hull
        +
        [hull[0]]
    )

    perimetro = 0

    for i in range(
        len(pontos) - 1
    ):

        x1, y1 = pontos[i]
        x2, y2 = pontos[i + 1]

        perimetro += math.sqrt(
            (x2 - x1) ** 2
            +
            (y2 - y1) ** 2
        )

    epsilon = max(
        3,
        perimetro * 0.03
    )

    simplificado = simplificar_poligono(
        pontos,
        epsilon
    )

    if (
        simplificado
        and
        simplificado[-1]
        ==
        simplificado[0]
    ):

        simplificado.pop()

    return simplificado


# ============================================================
# AREA DO POLIGONO
# ============================================================

def area_poligono(pontos):

    if len(pontos) < 3:
        return 0

    area = 0

    for i in range(
        len(pontos)
    ):

        x1, y1 = pontos[i]

        x2, y2 = pontos[
            (i + 1)
            %
            len(pontos)
        ]

        area += (
            x1 * y2
            -
            x2 * y1
        )

    return abs(
        area
    ) / 2


# ============================================================
# PERFIL RADIAL
# ============================================================

def contar_picos(
    pontos,
    centro_x,
    centro_y
):

    quantidade_bins = 72

    perfil = [
        0
        for _ in range(
            quantidade_bins
        )
    ]

    for x, y in pontos:

        dx = x - centro_x
        dy = y - centro_y

        raio = math.sqrt(
            dx * dx
            +
            dy * dy
        )

        angulo = math.atan2(
            dy,
            dx
        )

        indice = int(
            (
                (
                    angulo
                    +
                    math.pi
                )
                /
                (
                    2 * math.pi
                )
            )
            *
            quantidade_bins
        )

        indice %= quantidade_bins

        if raio > perfil[indice]:

            perfil[indice] = raio

    # --------------------------------------------------------
    # Suavização circular
    # --------------------------------------------------------

    for _ in range(2):

        novo = []

        for i in range(
            quantidade_bins
        ):

            valor = (
                perfil[
                    (i - 2)
                    %
                    quantidade_bins
                ]
                +
                perfil[
                    (i - 1)
                    %
                    quantidade_bins
                ]
                +
                perfil[i]
                +
                perfil[
                    (i + 1)
                    %
                    quantidade_bins
                ]
                +
                perfil[
                    (i + 2)
                    %
                    quantidade_bins
                ]
            ) / 5

            novo.append(
                valor
            )

        perfil = novo

    minimo = min(
        perfil
    )

    maximo = max(
        perfil
    )

    if maximo <= minimo:

        return 0

    media = sum(
        perfil
    ) / len(
        perfil
    )

    limite = (
        media
        +
        (
            maximo - media
        )
        *
        0.20
    )

    picos = []

    for i in range(
        quantidade_bins
    ):

        anterior = perfil[
            (i - 1)
            %
            quantidade_bins
        ]

        atual = perfil[i]

        proximo = perfil[
            (i + 1)
            %
            quantidade_bins
        ]

        if (
            atual > anterior
            and
            atual >= proximo
            and
            atual > limite
        ):

            picos.append(
                i
            )

    # --------------------------------------------------------
    # Agrupar picos próximos
    # --------------------------------------------------------

    grupos = []

    for pico in picos:

        if not grupos:

            grupos.append(
                [pico]
            )

            continue

        ultimo = grupos[-1][-1]

        if (
            pico - ultimo
            <= 6
        ):

            grupos[-1].append(
                pico
            )

        else:

            grupos.append(
                [pico]
            )

    # --------------------------------------------------------
    # Corrigir fechamento circular
    # --------------------------------------------------------

    if len(grupos) > 1:

        primeiro = grupos[0][0]
        ultimo = grupos[-1][-1]

        if (
            primeiro
            +
            quantidade_bins
            -
            ultimo
            <= 6
        ):

            grupos[0] = (
                grupos[-1]
                +
                grupos[0]
            )

            grupos.pop()

    return len(
        grupos
    )


# ============================================================
# CLASSIFICAR
# ============================================================

def classificar_gesto(
    pontos,
    poligono,
    componente
):

    if not pontos:
        return GESTO_UNKNOWN, {}

    centro_x = sum(
        x
        for x, y in pontos
    ) / len(pontos)

    centro_y = sum(
        y
        for x, y in pontos
    ) / len(pontos)

    area_pixels = len(
        pontos
    )

    area_hull = area_poligono(
        poligono
    )

    if area_hull <= 0:

        return GESTO_UNKNOWN, {}

    vertices = len(
        poligono
    )

    proporcao = (
        area_pixels
        /
        area_hull
    )

    largura = componente["w"]
    altura = componente["h"]

    proporcao_caixa = (
        largura
        /
        max(
            1,
            altura
        )
    )

    picos = contar_picos(
        pontos,
        centro_x,
        centro_y
    )

    print()
    print(
        "========================================"
    )

    print(
        "📐 ANÁLISE DO POLÍGONO"
    )

    print(
        "========================================"
    )

    print(
        "VERTICES:",
        vertices
    )

    print(
        "AREA PIXELS:",
        area_pixels
    )

    print(
        "AREA POLIGONO:",
        round(
            area_hull,
            2
        )
    )

    print(
        "SOLIDEZ:",
        round(
            proporcao,
            3
        )
    )

    print(
        "PROPORÇÃO CAIXA:",
        round(
            proporcao_caixa,
            3
        )
    )

    print(
        "PICOS RADIAIS:",
        picos
    )

    # --------------------------------------------------------
    # CLASSIFICAÇÃO
    #
    # Para um punho:
    #
    # - poucos picos
    # - formato compacto
    #
    # Para mão aberta:
    #
    # - mais picos
    # - formato menos compacto
    # --------------------------------------------------------

    if picos <= 3:

        gesto = GESTO_FIST

    elif picos >= 4:

        gesto = GESTO_OPEN_PALM

    else:

        gesto = GESTO_UNKNOWN

    return gesto, {
        "vertices": vertices,
        "area_pixels": area_pixels,
        "area_poligono": area_hull,
        "solidez": proporcao,
        "proporcao_caixa": proporcao_caixa,
        "picos": picos
    }


# ============================================================
# CRIAR MÁSCARA PNG
# ============================================================

def salvar_mascara(
    mascara,
    largura,
    altura
):

    dados = bytes(
        255 if valor else 0
        for valor in mascara
    )

    resultado = subprocess.run(
        [
            "magick",
            "-size",
            f"{largura}x{altura}",
            "-depth",
            "8",
            "gray:-",
            ARQUIVO_MASCARA
        ],
        input=dados,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if resultado.returncode != 0:

        print(
            "❌ ERRO AO SALVAR MÁSCARA"
        )

        try:

            print(
                resultado.stderr.decode(
                    errors="ignore"
                )
            )

        except Exception:
            pass

        return False

    return True


# ============================================================
# DESENHAR POLÍGONO
# ============================================================

def pintar_poligono(
    arquivo_original,
    largura,
    altura,
    poligono,
    gesto,
    metricas
):

    if len(poligono) < 3:

        print(
            "❌ POLÍGONO INVÁLIDO"
        )

        return False

    pontos_texto = " ".join(
        f"{x},{y}"
        for x, y in poligono
    )

    comando_polygon = (
        "polygon "
        +
        pontos_texto
    )

    texto = (
        f"GESTO: {gesto}"
        f" | vertices={metricas.get('vertices', 0)}"
        f" | picos={metricas.get('picos', 0)}"
    )

    resultado = subprocess.run(
        [
            "magick",

            arquivo_original,

            "-resize",
            f"{TAMANHO_MAXIMO}x{TAMANHO_MAXIMO}",

            # ----------------------------------------------
            # PREENCHIMENTO
            # ----------------------------------------------

            "-fill",
            "rgba(255,0,0,0.25)",

            # ----------------------------------------------
            # CONTORNO
            # ----------------------------------------------

            "-stroke",
            "#00ff00",

            "-strokewidth",
            "3",

            "-draw",
            comando_polygon,

            # ----------------------------------------------
            # TEXTO
            # ----------------------------------------------

            "-fill",
            "white",

            "-stroke",
            "black",

            "-strokewidth",
            "2",

            "-pointsize",
            "16",

            "-gravity",
            "northwest",

            "-annotate",
            "+8+8",
            texto,

            ARQUIVO_DEBUG
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if resultado.returncode != 0:

        print()
        print(
            "❌ ERRO AO PINTAR POLÍGONO"
        )

        print(
            resultado.stderr
        )

        return False

    return True


# ============================================================
# RECONHECER GESTO
# ============================================================

def reconhecer_gesto(arquivo):

    print()
    print(
        "========================================"
    )

    print(
        "🖐️ DETECTOR DE GESTO"
    )

    print(
        "========================================"
    )

    print(
        "ARQUIVO:",
        arquivo
    )

    # --------------------------------------------------------
    # FOTO EXISTE?
    # --------------------------------------------------------

    if not os.path.exists(
        arquivo
    ):

        print(
            "❌ FOTO NÃO EXISTE"
        )

        return GESTO_UNKNOWN

    # --------------------------------------------------------
    # TAMANHO
    # --------------------------------------------------------

    tamanho = obter_tamanho_imagem(
        arquivo
    )

    if tamanho is None:

        return GESTO_UNKNOWN

    largura, altura = tamanho

    print(
        "TAMANHO:",
        largura,
        "x",
        altura
    )

    # --------------------------------------------------------
    # RGB
    # --------------------------------------------------------

    dados = carregar_rgb(
        arquivo,
        largura,
        altura
    )

    if dados is None:

        return GESTO_UNKNOWN

    # --------------------------------------------------------
    # MÁSCARA
    # --------------------------------------------------------

    mascara = criar_mascara(
        dados,
        largura,
        altura
    )

    # --------------------------------------------------------
    # SALVAR MÁSCARA
    # --------------------------------------------------------

    salvar_mascara(
        mascara,
        largura,
        altura
    )

    print()
    print(
        "MÁSCARA:",
        ARQUIVO_MASCARA
    )

    # --------------------------------------------------------
    # COMPONENTES
    # --------------------------------------------------------

    componentes = encontrar_componentes(
        mascara,
        largura,
        altura
    )

    print()
    print(
        "COMPONENTES ENCONTRADOS:",
        len(componentes)
    )

    if not componentes:

        print(
            "❌ NENHUM COMPONENTE ENCONTRADO"
        )

        return GESTO_UNKNOWN

    # --------------------------------------------------------
    # MOSTRAR COMPONENTES
    # --------------------------------------------------------

    for indice, componente in enumerate(
        componentes,
        start=1
    ):

        print(
            "COMPONENTE",
            indice,
            "|",
            "AREA:",
            componente["area"],
            "|",
            "BOX:",
            (
                componente["x"],
                componente["y"],
                componente["w"],
                componente["h"]
            )
        )

    # --------------------------------------------------------
    # PRINCIPAL
    # --------------------------------------------------------

    principal = escolher_componente(
        componentes,
        largura,
        altura
    )

    if principal is None:

        return GESTO_UNKNOWN

    # --------------------------------------------------------
    # JUNTAR PARTES DA MÃO
    # --------------------------------------------------------

    pontos = juntar_componentes(
        componentes,
        principal
    )

    if len(pontos) < 30:

        print(
            "❌ POUCOS PIXELS PARA ANALISAR"
        )

        return GESTO_UNKNOWN

    # --------------------------------------------------------
    # POLÍGONO
    # --------------------------------------------------------

    hull = convex_hull(
        pontos
    )

    if len(hull) < 3:

        print(
            "❌ NÃO FOI POSSÍVEL CRIAR POLÍGONO"
        )

        return GESTO_UNKNOWN

    print()
    print(
        "POLÍGONO BRUTO:",
        len(hull),
        "vértices"
    )

    # --------------------------------------------------------
    # SIMPLIFICAR
    # --------------------------------------------------------

    poligono = simplificar_hull(
        hull
    )

    print(
        "POLÍGONO SIMPLIFICADO:",
        len(poligono),
        "vértices"
    )

    # --------------------------------------------------------
    # CLASSIFICAR
    # --------------------------------------------------------

    gesto, metricas = classificar_gesto(
        pontos,
        poligono,
        principal
    )

    # --------------------------------------------------------
    # PINTAR
    # --------------------------------------------------------

    pintado = pintar_poligono(
        arquivo,
        largura,
        altura,
        poligono,
        gesto,
        metricas
    )

    if pintado:

        print()
        print(
            "🎨 POLÍGONO PINTADO!"
        )

        print(
            "ARQUIVO:",
            ARQUIVO_DEBUG
        )

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    print()
    print(
        "========================================"
    )

    print(
        "🤖 RESULTADO"
    )

    print(
        "========================================"
    )

    print(
        "GESTO:",
        gesto
    )

    print(
        "========================================"
    )

    return gesto


# ============================================================
# TESTE DIRETO
# ============================================================

if __name__ == "__main__":

    foto = "robot_foto.jpg"

    gesto = reconhecer_gesto(
        foto
    )

    print()
    print(
        "RESULTADO FINAL:",
        gesto
    )