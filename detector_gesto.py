import os
import sys
import subprocess
import math
from collections import deque
import glob
import urllib.request
import numpy as np

try:
    import tflite_runtime.interpreter as tflite
except Exception as e:
    print("❌ tflite_runtime não disponível")
    print(e)
    sys.exit(1)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

TAMANHO_MAXIMO = 320

GESTO_FIST = "FIST"
GESTO_OPEN_PALM = "OPEN_PALM"
GESTO_UNKNOWN = "UNKNOWN"

ARQUIVO_DEBUG = "gesto_detectado.png"
ARQUIVO_MASCARA = "gesto_mascara.png"

AREA_MINIMA = 120

# ------------------------------------------------------------
# MODELOS
# ------------------------------------------------------------

PASTA_PROJETO = os.path.dirname(
    os.path.abspath(__file__)
)

MODELO_PALMA = os.path.join(
    PASTA_PROJETO,
    "palm_detection_full.tflite"
)

MODELO_LANDMARK = os.path.join(
    PASTA_PROJETO,
    "hand_landmark_full.tflite"
)

MODELO_EMBEDDING = os.path.join(
    PASTA_PROJETO,
    "gesture_embedder.tflite"
)

MODELO_GESTO = os.path.join(
    PASTA_PROJETO,
    "canned_gesture_classifier.tflite"
)


URL_MODELOS = {
    MODELO_PALMA:
        "https://storage.googleapis.com/mediapipe-assets/palm_detection_full.tflite",

    MODELO_LANDMARK:
        "https://storage.googleapis.com/mediapipe-assets/hand_landmark_full.tflite",

    MODELO_EMBEDDING:
        "https://storage.googleapis.com/mediapipe-assets/gesture_embedder.tflite",

    MODELO_GESTO:
        "https://storage.googleapis.com/mediapipe-assets/canned_gesture_classifier.tflite",
}


# ============================================================
# DOWNLOAD DOS MODELOS
# ============================================================

def baixar_modelos():

    print()
    print("========================================")
    print("📦 MODELOS TFLITE")
    print("========================================")

    for arquivo, url in URL_MODELOS.items():

        nome = os.path.basename(arquivo)

        if os.path.exists(arquivo):

            tamanho = os.path.getsize(arquivo)

            print(
                f"✅ {nome}: "
                f"{tamanho / 1024:.1f} KB"
            )

            continue

        print()
        print("⬇️ Baixando:", nome)
        print(url)

        try:

            urllib.request.urlretrieve(
                url,
                arquivo
            )

            tamanho = os.path.getsize(
                arquivo
            )

            print(
                f"✅ Baixado: "
                f"{tamanho / 1024:.1f} KB"
            )

        except Exception as e:

            print(
                "❌ ERRO AO BAIXAR:",
                nome
            )

            print(e)

            if os.path.exists(arquivo):

                try:
                    os.remove(arquivo)
                except Exception:
                    pass

    faltando = []

    for arquivo in URL_MODELOS:

        if not os.path.exists(arquivo):
            faltando.append(
                os.path.basename(arquivo)
            )

    if faltando:

        print()
        print(
            "❌ MODELOS FALTANDO:"
        )

        for nome in faltando:
            print(" -", nome)

        return False

    print()
    print("✅ Todos os modelos disponíveis")

    return True


# ============================================================
# UTILITÁRIOS TFLITE
# ============================================================

def criar_interpreter(arquivo):

    print()
    print(
        "CARREGANDO TFLITE:",
        os.path.basename(arquivo)
    )

    interpreter = tflite.Interpreter(
        model_path=arquivo,
        num_threads=2
    )

    interpreter.allocate_tensors()

    entradas = interpreter.get_input_details()
    saidas = interpreter.get_output_details()

    print(
        "ENTRADAS:",
        len(entradas)
    )

    for entrada in entradas:

        print(
            " ",
            entrada["name"],
            entrada["shape"],
            entrada["dtype"]
        )

    print(
        "SAÍDAS:",
        len(saidas)
    )

    for saida in saidas:

        print(
            " ",
            saida["name"],
            saida["shape"],
            saida["dtype"]
        )

    return interpreter


# ============================================================
# LIMPEZA
# ============================================================

def limpar_pngs():

    for arq in glob.glob(
        os.path.join(
            PASTA_PROJETO,
            "*.png"
        )
    ):

        try:
            os.remove(arq)
            print(
                "🗑️ Removido:",
                arq
            )
        except Exception as e:
            print(
                "⚠️ Não foi possível remover:",
                arq,
                e
            )


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
            "❌ ERRO AO OBTER TAMANHO"
        )

        print(
            resultado.stderr
        )

        return None

    try:

        return tuple(
            map(
                int,
                resultado.stdout.strip().split()
            )
        )

    except Exception:

        return None


def carregar_rgb(
    arquivo,
    largura,
    altura
):

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

        return None

    dados = resultado.stdout

    esperado = (
        largura *
        altura *
        3
    )

    if len(dados) < esperado:

        print(
            "❌ RGB INCOMPLETO"
        )

        return None

    return dados


def pixel_rgb(
    dados,
    largura,
    x,
    y
):

    i = (
        y *
        largura +
        x
    ) * 3

    return (
        dados[i],
        dados[i + 1],
        dados[i + 2]
    )


# ============================================================
# IMAGEM NUMPY
# ============================================================

def rgb_para_numpy(
    dados,
    largura,
    altura
):

    arr = np.frombuffer(
        dados,
        dtype=np.uint8
    )

    arr = arr[
        :largura * altura * 3
    ]

    return arr.reshape(
        altura,
        largura,
        3
    )


# ============================================================
# DETECTOR DE PELE
# ============================================================

def distancia_cor(a, b):

    return math.sqrt(
        (a[0] - b[0]) ** 2 +
        (a[1] - b[1]) ** 2 +
        (a[2] - b[2]) ** 2
    )


def amostrar_pele(
    dados,
    largura,
    altura
):

    inicio_y = int(
        altura * 0.35
    )

    fim_y = int(
        altura * 0.92
    )

    inicio_x = int(
        largura * 0.03
    )

    fim_x = int(
        largura * 0.95
    )

    candidatos = []

    passo = 3

    for y in range(
        inicio_y,
        fim_y,
        passo
    ):

        for x in range(
            inicio_x,
            fim_x,
            passo
        ):

            r, g, b = pixel_rgb(
                dados,
                largura,
                x,
                y
            )

            brilho = (
                r + g + b
            ) / 3.0

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

            sat = maior - menor

            if brilho < 35:
                continue

            if brilho > 250:
                continue

            if sat < 8:
                continue

            if r < b * 0.45:
                continue

            if g < b * 0.60:
                continue

            candidatos.append(
                (r, g, b)
            )

    if not candidatos:

        print(
            "⚠️ Nenhuma amostra de pele"
        )

        return (
            150,
            110,
            90
        )

    rs = sorted(
        x[0]
        for x in candidatos
    )

    gs = sorted(
        x[1]
        for x in candidatos
    )

    bs = sorted(
        x[2]
        for x in candidatos
    )

    meio = len(
        candidatos
    ) // 2

    referencia = (
        rs[meio],
        gs[meio],
        bs[meio]
    )

    print(
        "AMOSTRA PELE:",
        referencia
    )

    print(
        "AMOSTRAS:",
        len(candidatos)
    )

    return referencia


def pixel_eh_pele(
    r,
    g,
    b,
    referencia
):

    rr, rg, rb = referencia

    brilho = (
        r + g + b
    ) / 3.0

    if brilho < 30:
        return False

    if brilho > 252:
        return False

    distancia = distancia_cor(
        (r, g, b),
        referencia
    )

    if distancia > 115:
        return False

    if abs(r - rr) > 95:
        return False

    if abs(g - rg) > 95:
        return False

    if abs(b - rb) > 95:
        return False

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

    if maior - menor < 6:
        return False

    if r < b * 0.45:
        return False

    if g < b * 0.58:
        return False

    return True


# ============================================================
# MÁSCARA
# ============================================================

def criar_mascara(
    dados,
    largura,
    altura
):

    mascara = bytearray(
        largura * altura
    )

    referencia = amostrar_pele(
        dados,
        largura,
        altura
    )

    quantidade = 0

    for y in range(
        int(altura * 0.20),
        int(altura * 0.98)
    ):

        for x in range(
            int(largura * 0.02),
            int(largura * 0.98)
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
                b,
                referencia
            ):

                mascara[
                    y * largura + x
                ] = 1

                quantidade += 1

    print(
        "PIXELS DE PELE:",
        quantidade
    )

    mascara = dilatar_mascara(
        mascara,
        largura,
        altura,
        1
    )

    mascara = erodir_mascara(
        mascara,
        largura,
        altura,
        1
    )

    return mascara


def dilatar_mascara(
    mascara,
    largura,
    altura,
    iteracoes=1
):

    atual = mascara

    for _ in range(
        iteracoes
    ):

        nova = bytearray(
            len(atual)
        )

        for y in range(
            1,
            altura - 1
        ):

            for x in range(
                1,
                largura - 1
            ):

                idx = (
                    y *
                    largura +
                    x
                )

                if atual[idx]:

                    nova[idx] = 1

                    nova[idx - 1] = 1
                    nova[idx + 1] = 1

                    nova[
                        idx - largura
                    ] = 1

                    nova[
                        idx + largura
                    ] = 1

                    nova[
                        idx - largura - 1
                    ] = 1

                    nova[
                        idx - largura + 1
                    ] = 1

                    nova[
                        idx + largura - 1
                    ] = 1

                    nova[
                        idx + largura + 1
                    ] = 1

        atual = nova

    return atual


def erodir_mascara(
    mascara,
    largura,
    altura,
    iteracoes=1
):

    atual = mascara

    for _ in range(
        iteracoes
    ):

        nova = bytearray(
            len(atual)
        )

        for y in range(
            1,
            altura - 1
        ):

            for x in range(
                1,
                largura - 1
            ):

                idx = (
                    y *
                    largura +
                    x
                )

                if (
                    atual[idx]
                    and atual[idx - 1]
                    and atual[idx + 1]
                    and atual[idx - largura]
                    and atual[idx + largura]
                ):

                    nova[idx] = 1

        atual = nova

    return atual


# ============================================================
# COMPONENTES
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

            idx = (
                y *
                largura +
                x
            )

            if not mascara[idx]:
                continue

            if visitado[idx]:
                continue

            fila = deque([
                (x, y)
            ])

            visitado[idx] = 1

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

                min_x = min(
                    min_x,
                    px
                )

                max_x = max(
                    max_x,
                    px
                )

                min_y = min(
                    min_y,
                    py
                )

                max_y = max(
                    max_y,
                    py
                )

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
                        ny *
                        largura +
                        nx
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

            if area < AREA_MINIMA:
                continue

            componentes.append({
                "pontos": pontos,
                "area": area,
                "x": min_x,
                "y": min_y,
                "w": max_x - min_x + 1,
                "h": max_y - min_y + 1,
                "cx": (
                    min_x + max_x
                ) / 2,
                "cy": (
                    min_y + max_y
                ) / 2
            })

    componentes.sort(
        key=lambda c: c["area"],
        reverse=True
    )

    return componentes


def escolher_componente(
    componentes,
    largura,
    altura
):

    if not componentes:
        return None

    alvo_x = largura * 0.50
    alvo_y = altura * 0.60

    melhor = None
    melhor_score = -999999

    for comp in componentes:

        cx = comp["cx"]
        cy = comp["cy"]
        area = comp["area"]

        distancia = math.sqrt(
            (
                (cx - alvo_x)
                / largura
            ) ** 2
            +
            (
                (cy - alvo_y)
                / altura
            ) ** 2
        )

        proximidade = max(
            0,
            1 - distancia * 2.5
        )

        score = (
            math.sqrt(area) * 2
            +
            proximidade * 220
        )

        if cy < altura * 0.30:
            score -= 200

        if score > melhor_score:

            melhor_score = score
            melhor = comp

    print()
    print(
        "COMPONENTE ESCOLHIDO"
    )

    print(
        "AREA:",
        melhor["area"]
    )

    print(
        "BOX:",
        (
            melhor["x"],
            melhor["y"],
            melhor["w"],
            melhor["h"]
        )
    )

    return melhor


# ============================================================
# CONTORNO
# ============================================================

def extrair_contorno(
    pontos,
    largura,
    altura
):

    conjunto = set(
        pontos
    )

    contorno = []

    for x, y in pontos:

        borda = False

        for nx, ny in (
            (x - 1, y),
            (x + 1, y),
            (x, y - 1),
            (x, y + 1),
        ):

            if (
                nx < 0
                or ny < 0
                or nx >= largura
                or ny >= altura
                or (nx, ny) not in conjunto
            ):

                borda = True
                break

        if borda:
            contorno.append(
                (x, y)
            )

    return contorno


def calcular_centro(
    pontos
):

    if not pontos:
        return 0, 0

    sx = 0
    sy = 0

    for x, y in pontos:

        sx += x
        sy += y

    return (
        sx / len(pontos),
        sy / len(pontos)
    )


# ============================================================
# POLÍGONO
# ============================================================

def ordenar_contorno(
    contorno,
    cx,
    cy
):

    return sorted(
        contorno,
        key=lambda p: math.atan2(
            p[1] - cy,
            p[0] - cx
        )
    )


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
            (x - x1) ** 2 +
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
            dx * dx +
            dy * dy
        )
    )

    t = max(
        0,
        min(1, t)
    )

    px = x1 + t * dx
    py = y1 + t * dy

    return math.sqrt(
        (x - px) ** 2 +
        (y - py) ** 2
    )


def simplificar_poligono(
    pontos,
    epsilon
):

    if len(pontos) <= 3:
        return pontos

    maior = 0
    indice = 0

    inicio = pontos[0]
    fim = pontos[-1]

    for i in range(
        1,
        len(pontos) - 1
    ):

        d = distancia_ponto_linha(
            pontos[i],
            inicio,
            fim
        )

        if d > maior:

            maior = d
            indice = i

    if maior > epsilon:

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


def criar_poligono_contorno(
    contorno
):

    if len(contorno) < 3:
        return contorno

    cx, cy = calcular_centro(
        contorno
    )

    ordenado = ordenar_contorno(
        contorno,
        cx,
        cy
    )

    perimetro = 0

    for i in range(
        len(ordenado)
    ):

        x1, y1 = ordenado[i]

        x2, y2 = ordenado[
            (i + 1)
            % len(ordenado)
        ]

        perimetro += math.sqrt(
            (x2 - x1) ** 2 +
            (y2 - y1) ** 2
        )

    epsilon = max(
        1.5,
        min(
            5.0,
            perimetro * 0.008
        )
    )

    fechado = (
        ordenado
        +
        [ordenado[0]]
    )

    simplificado = (
        simplificar_poligono(
            fechado,
            epsilon
        )
    )

    if (
        len(simplificado) > 1
        and
        simplificado[-1]
        ==
        simplificado[0]
    ):

        simplificado.pop()

    return simplificado


# ============================================================
# TFLITE — LANDMARK
# ============================================================

def recortar_mao(
    imagem,
    componente
):

    h, w, _ = imagem.shape

    x = componente["x"]
    y = componente["y"]
    cw = componente["w"]
    ch = componente["h"]

    margem_x = max(
        10,
        int(cw * 0.25)
    )

    margem_y = max(
        10,
        int(ch * 0.25)
    )

    x1 = max(
        0,
        x - margem_x
    )

    y1 = max(
        0,
        y - margem_y
    )

    x2 = min(
        w,
        x + cw + margem_x
    )

    y2 = min(
        h,
        y + ch + margem_y
    )

    crop = imagem[
        y1:y2,
        x1:x2
    ]

    return crop, (
        x1,
        y1,
        x2,
        y2
    )


def preparar_entrada_landmark(
    crop
):

    imagem = ImageResize(
        crop,
        224,
        224
    )

    entrada = imagem.astype(
        np.float32
    )

    # O modelo full trabalha com RGB normalizado.
    entrada = (
        entrada - 127.5
    ) / 127.5

    entrada = entrada[
        np.newaxis,
        ...
    ]

    return entrada


def ImageResize(
    imagem,
    largura,
    altura
):

    # Usa ImageMagick para evitar Pillow.
    #
    # O crop é convertido para bytes RGB
    # e redimensionado através de magick.

    h, w, _ = imagem.shape

    dados = imagem.astype(
        np.uint8
    ).tobytes()

    processo = subprocess.run(
        [
            "magick",
            "-size",
            f"{w}x{h}",
            "-depth",
            "8",
            "rgb:-",
            "-resize",
            f"{largura}x{altura}!",
            "-depth",
            "8",
            "rgb:-"
        ],
        input=dados,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    esperado = (
        largura *
        altura *
        3
    )

    if (
        processo.returncode != 0
        or
        len(processo.stdout) < esperado
    ):

        print(
            "❌ Falha resize TFLite"
        )

        return np.zeros(
            (
                altura,
                largura,
                3
            ),
            dtype=np.uint8
        )

    return np.frombuffer(
        processo.stdout[:esperado],
        dtype=np.uint8
    ).reshape(
        altura,
        largura,
        3
    )


def detectar_landmarks(
    interpreter,
    crop
):

    entradas = (
        interpreter
        .get_input_details()
    )

    entrada = entradas[0]

    shape = entrada["shape"]

    altura = int(
        shape[1]
    )

    largura = int(
        shape[2]
    )

    imagem = ImageResize(
        crop,
        largura,
        altura
    )

    dtype = entrada[
        "dtype"
    ]

    if dtype == np.float32:

        tensor = (
            imagem.astype(
                np.float32
            )
            -
            127.5
        ) / 127.5

    elif dtype == np.uint8:

        tensor = imagem.astype(
            np.uint8
        )

    else:

        tensor = imagem.astype(
            dtype
        )

    tensor = tensor[
        np.newaxis,
        ...
    ]

    interpreter.set_tensor(
        entrada["index"],
        tensor
    )

    interpreter.invoke()

    saidas = (
        interpreter
        .get_output_details()
    )

    resultados = []

    for saida in saidas:

        arr = interpreter.get_tensor(
            saida["index"]
        )

        resultados.append(
            (
                saida,
                arr
            )
        )

    # --------------------------------------------------------
    # Procuramos uma saída contendo 63 valores.
    # 21 landmarks x 3 coordenadas.
    # --------------------------------------------------------

    landmarks = None

    for detalhe, arr in resultados:

        flat = arr.reshape(-1)

        if len(flat) >= 63:

            # Muitas versões do modelo possuem
            # Identity = 63 coordenadas.
            landmarks = flat[:63]

            print(
                "LANDMARK OUTPUT:",
                detalhe["name"],
                arr.shape
            )

            break

    if landmarks is None:

        print(
            "❌ Não encontramos saída 63"
        )

        return None

    landmarks = landmarks.reshape(
        21,
        3
    )

    # --------------------------------------------------------
    # O modelo retorna coordenadas no espaço do crop.
    #
    # Nas versões atuais do modelo full,
    # a coordenada XY é referente ao espaço 224x224.
    # --------------------------------------------------------

    pontos = []

    for lm in landmarks:

        lx = float(
            lm[0]
        )

        ly = float(
            lm[1]
        )

        lz = float(
            lm[2]
        )

        pontos.append(
            (
                lx,
                ly,
                lz
            )
        )

    return pontos


# ============================================================
# CLASSIFICAÇÃO GEOMÉTRICA DOS LANDMARKS
# ============================================================

# Índices MediaPipe:
#
# 0  wrist
# 1  thumb CMC
# 2  thumb MCP
# 3  thumb IP
# 4  thumb tip
#
# 5  index MCP
# 6  index PIP
# 7  index DIP
# 8  index tip
#
# 9  middle MCP
# 10 middle PIP
# 11 middle DIP
# 12 middle tip
#
# 13 ring MCP
# 14 ring PIP
# 15 ring DIP
# 16 ring tip
#
# 17 pinky MCP
# 18 pinky PIP
# 19 pinky DIP
# 20 pinky tip


def distancia_3d(a, b):

    return math.sqrt(
        (a[0] - b[0]) ** 2 +
        (a[1] - b[1]) ** 2 +
        (a[2] - b[2]) ** 2
    )


def angulo_3pontos(
    a,
    b,
    c
):

    bax = a[0] - b[0]
    bay = a[1] - b[1]
    baz = a[2] - b[2]

    bcx = c[0] - b[0]
    bcy = c[1] - b[1]
    bcz = c[2] - b[2]

    produto = (
        bax * bcx
        +
        bay * bcy
        +
        baz * bcz
    )

    norma_a = math.sqrt(
        bax * bax +
        bay * bay +
        baz * baz
    )

    norma_c = math.sqrt(
        bcx * bcx +
        bcy * bcy +
        bcz * bcz
    )

    if norma_a == 0 or norma_c == 0:
        return 180

    coseno = (
        produto /
        (norma_a * norma_c)
    )

    coseno = max(
        -1,
        min(
            1,
            coseno
        )
    )

    return math.degrees(
        math.acos(coseno)
    )


def classificar_landmarks(
    landmarks
):

    if not landmarks:
        return GESTO_UNKNOWN, {}

    wrist = landmarks[0]

    dedos = [
        (5, 6, 7, 8),
        (9, 10, 11, 12),
        (13, 14, 15, 16),
        (17, 18, 19, 20)
    ]

    estendidos = 0

    flexoes = []

    for mcp, pip, dip, tip in dedos:

        angulo = angulo_3pontos(
            landmarks[mcp],
            landmarks[pip],
            landmarks[tip]
        )

        flexoes.append(
            angulo
        )

        # Dedo aberto normalmente
        # apresenta uma cadeia muito
        # mais linear.
        if angulo > 145:

            estendidos += 1

    # Polegar.
    #
    # Para FIST não precisamos exigir
    # que ele esteja completamente fechado.
    polegar_dist = distancia_3d(
        landmarks[4],
        landmarks[5]
    )

    palma = distancia_3d(
        landmarks[0],
        landmarks[9]
    )

    if palma <= 0:
        return GESTO_UNKNOWN, {}

    polegar_rel = (
        polegar_dist /
        palma
    )

    # --------------------------------------------------------
    # FIST
    # --------------------------------------------------------

    # Quatro dedos recolhidos.
    #
    # Toleramos um dedo ambíguo.
    if estendidos <= 1:

        gesto = GESTO_FIST

    elif estendidos >= 3:

        gesto = GESTO_OPEN_PALM

    else:

        # Caso intermediário.
        #
        # Usa a distância média das pontas
        # em relação ao punho.
        pontas = [
            landmarks[8],
            landmarks[12],
            landmarks[16],
            landmarks[20]
        ]

        distancia_media = sum(
            distancia_3d(
                p,
                wrist
            )
            for p in pontas
        ) / 4

        distancia_relativa = (
            distancia_media /
            palma
        )

        if distancia_relativa < 2.0:

            gesto = GESTO_FIST

        else:

            gesto = GESTO_OPEN_PALM

    print()
    print(
        "========================================"
    )
    print(
        "🧠 LANDMARK CLASSIFIER"
    )
    print(
        "========================================"
    )

    print(
        "DEDOS ESTENDIDOS:",
        estendidos
    )

    print(
        "ÂNGULOS:",
        [
            round(v, 1)
            for v in flexoes
        ]
    )

    print(
        "POLEGAR/PALMA:",
        round(
            polegar_rel,
            3
        )
    )

    print(
        "GESTO:",
        gesto
    )

    return gesto, {
        "dedos_estendidos":
            estendidos,

        "angulos":
            flexoes,

        "polegar_rel":
            polegar_rel
    }


# ============================================================
# POLÍGONO DA MÃO
# ============================================================

def detectar_poligono(
    contorno
):

    return criar_poligono_contorno(
        contorno
    )


# ============================================================
# SALVAR MÁSCARA
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

    return (
        resultado.returncode == 0
    )


# ============================================================
# DEBUG
# ============================================================

def pintar_debug(
    arquivo_original,
    componentes,
    principal,
    contorno,
    poligono,
    gesto,
    metricas
):

    cmd = [
        "magick",
        arquivo_original,
        "-resize",
        f"{TAMANHO_MAXIMO}x{TAMANHO_MAXIMO}",
        "-pointsize",
        "12"
    ]

    desenhos = []

    for idx, comp in enumerate(
        componentes,
        start=1
    ):

        x = comp["x"]
        y = comp["y"]
        w = comp["w"]
        h = comp["h"]

        desenhos.append(
            f"fill none stroke yellow "
            f"stroke-width 1 rectangle "
            f"{x},{y} {x+w},{y+h}"
        )

        desenhos.append(
            f"fill yellow stroke none "
            f"text {x+2},{y+13} '{idx}'"
        )

    if principal:

        x = principal["x"]
        y = principal["y"]
        w = principal["w"]
        h = principal["h"]

        desenhos.append(
            f"fill none stroke blue "
            f"stroke-width 3 rectangle "
            f"{x},{y} {x+w},{y+h}"
        )

    if len(contorno) >= 3:

        pontos = " ".join(
            f"{x},{y}"
            for x, y in contorno
        )

        desenhos.append(
            f"fill none stroke red "
            f"stroke-width 1 "
            f"polygon {pontos}"
        )

    if len(poligono) >= 3:

        pontos = " ".join(
            f"{x},{y}"
            for x, y in poligono
        )

        desenhos.append(
            f"fill none stroke lime "
            f"stroke-width 2 "
            f"polygon {pontos}"
        )

        for i, (x, y) in enumerate(
            poligono
        ):

            desenhos.append(
                f"fill lime stroke black "
                f"stroke-width 1 circle "
                f"{x},{y} {x+3},{y}"
            )

            desenhos.append(
                f"fill white stroke black "
                f"stroke-width 1 "
                f"text {x+4},{y-4} '{i}'"
            )

    cx = metricas.get(
        "centro_x"
    )

    cy = metricas.get(
        "centro_y"
    )

    if cx is not None:

        desenhos.append(
            f"fill magenta stroke black "
            f"stroke-width 2 circle "
            f"{int(cx)},{int(cy)} "
            f"{int(cx)+5},{int(cy)}"
        )

    texto = (
        f"{gesto} "
        f"dedos={metricas.get('dedos_estendidos', '-')}"
    )

    desenhos.append(
        f"fill white stroke black "
        f"stroke-width 2 "
        f"text 8,18 '{texto}'"
    )

    for desenho in desenhos:

        cmd.extend([
            "-draw",
            desenho
        ])

    cmd.append(
        ARQUIVO_DEBUG
    )

    resultado = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if resultado.returncode != 0:

        print(
            "❌ ERRO DEBUG"
        )

        print(
            resultado.stderr
        )

        return False

    return True


# ============================================================
# RECONHECER
# ============================================================

def reconhecer_gesto(
    arquivo
):

    print()
    print(
        "========================================"
    )
    print(
        "🖐️ DETECTOR DE GESTO TFLITE"
    )
    print(
        "========================================"
    )

    print(
        "ARQUIVO:",
        arquivo
    )

    # --------------------------------------------------------
    # MODELOS
    # --------------------------------------------------------

    if not baixar_modelos():

        return GESTO_UNKNOWN

    # --------------------------------------------------------
    # ARQUIVO
    # --------------------------------------------------------

    if not os.path.exists(
        arquivo
    ):

        print(
            "❌ FOTO NÃO EXISTE"
        )

        return GESTO_UNKNOWN

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

    dados = carregar_rgb(
        arquivo,
        largura,
        altura
    )

    if dados is None:

        return GESTO_UNKNOWN

    imagem = rgb_para_numpy(
        dados,
        largura,
        altura
    )

    # --------------------------------------------------------
    # MÁSCARA
    # --------------------------------------------------------

    mascara = criar_mascara(
        dados,
        largura,
        altura
    )

    salvar_mascara(
        mascara,
        largura,
        altura
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
        "COMPONENTES:",
        len(componentes)
    )

    if not componentes:

        print(
            "❌ NENHUM COMPONENTE"
        )

        return GESTO_UNKNOWN

    principal = escolher_componente(
        componentes,
        largura,
        altura
    )

    if principal is None:

        return GESTO_UNKNOWN

    pontos = principal[
        "pontos"
    ]

    # --------------------------------------------------------
    # CONTORNO
    # --------------------------------------------------------

    contorno = extrair_contorno(
        pontos,
        largura,
        altura
    )

    if len(contorno) < 10:

        print(
            "❌ CONTORNO INVÁLIDO"
        )

        return GESTO_UNKNOWN

    poligono = detectar_poligono(
        contorno
    )

    # --------------------------------------------------------
    # TFLITE LANDMARK
    # --------------------------------------------------------

    gesto = GESTO_UNKNOWN
    metricas = {}

    try:

        landmark_interpreter = criar_interpreter(
            MODELO_LANDMARK
        )

        crop, box = recortar_mao(
            imagem,
            principal
        )

        print()
        print(
            "CROP DA MÃO:",
            box
        )

        landmarks = detectar_landmarks(
            landmark_interpreter,
            crop
        )

        if landmarks is not None:

            gesto, metricas_landmark = (
                classificar_landmarks(
                    landmarks
                )
            )

            metricas.update(
                metricas_landmark
            )

    except Exception as e:

        print()
        print(
            "⚠️ ERRO TFLITE LANDMARK"
        )

        print(
            type(e).__name__,
            e
        )

        gesto = GESTO_UNKNOWN

    # --------------------------------------------------------
    # MÉTRICAS DA MÁSCARA
    # --------------------------------------------------------

    cx, cy = calcular_centro(
        pontos
    )

    area = len(
        pontos
    )

    ocupacao = (
        area /
        max(
            1,
            principal["w"]
            *
            principal["h"]
        )
    )

    metricas[
        "centro_x"
    ] = cx

    metricas[
        "centro_y"
    ] = cy

    metricas[
        "pixels"
    ] = area

    metricas[
        "ocupacao"
    ] = ocupacao

    metricas[
        "contorno"
    ] = len(contorno)

    metricas[
        "vertices"
    ] = len(poligono)

    # --------------------------------------------------------
    # DEBUG
    # --------------------------------------------------------

    pintar_debug(
        arquivo_original=arquivo,
        componentes=componentes,
        principal=principal,
        contorno=contorno,
        poligono=poligono,
        gesto=gesto,
        metricas=metricas
    )

    print()
    print(
        "========================================"
    )

    print(
        "🤖 RESULTADO:",
        gesto
    )

    print(
        "POLÍGONO:",
        len(poligono),
        "vértices"
    )

    print(
        "MÁSCARA:",
        ARQUIVO_MASCARA
    )

    print(
        "DEBUG:",
        ARQUIVO_DEBUG
    )

    print(
        "========================================"
    )

    return gesto


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) > 1:

        foto = sys.argv[1]

    else:

        foto = os.path.join(
            PASTA_PROJETO,
            "robot_foto.jpg"
        )

    resultado = reconhecer_gesto(
        foto
    )

    print()
    print(
        "RESULTADO FINAL:",
        resultado
    )