import os
import time
import subprocess
import termuxgui
import json


# ============================================================
# CAMERA
# ============================================================

def encontrar_camera_frontal():

    print()
    print("========================================")
    print("🔎 PROCURANDO CAMERA FRONTAL")
    print("========================================")

    try:

        resultado = subprocess.run(
            [
                "termux-camera-info"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )

        if resultado.returncode != 0:

            print("❌ ERRO AO CONSULTAR CAMERAS")
            print(resultado.stderr)

            return None

        cameras = json.loads(
            resultado.stdout
        )

        for camera in cameras:

            camera_id = camera.get("id")
            facing = camera.get("facing")

            print(
                "CAMERA:",
                camera_id,
                "| FACING:",
                facing
            )

            if facing == "front":

                print()
                print("🤳 CAMERA FRONTAL ENCONTRADA")
                print("ID:", camera_id)

                return camera_id

        print()
        print("❌ CAMERA FRONTAL NÃO ENCONTRADA")

        return None

    except Exception as e:

        print()
        print("❌ ERRO AO IDENTIFICAR CAMERA")

        print(
            type(e).__name__,
            e
        )

        return None

def tirar_foto():

    print()
    print("========================================")
    print("📷 TIRANDO FOTO")
    print("========================================")

    pasta_atual = os.getcwd()

    arquivo = os.path.join(
        pasta_atual,
        "robot_foto.jpg"
    )

    camera = encontrar_camera_frontal()

    if camera is None:

        print(
            "❌ NÃO FOI POSSÍVEL ENCONTRAR CAMERA FRONTAL"
        )

        return False

    print("CAMERA FRONTAL:", camera)
    print("ARQUIVO:", arquivo)

    try:

        resultado = subprocess.run(
            [
                "termux-camera-photo",
                "-c",
                str(camera),
                arquivo
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15
        )

        print("RETORNO:", resultado.returncode)

        print("STDOUT:")
        print(resultado.stdout)

        print("STDERR:")
        print(resultado.stderr)

        if os.path.exists(arquivo):

            tamanho = os.path.getsize(
                arquivo
            )

            print()
            print("========================================")
            print("🤳 FOTO FRONTAL CRIADA")
            print("========================================")

            print("CAMERA:", camera)
            print("ARQUIVO:", arquivo)
            print("TAMANHO:", tamanho, "bytes")

            return True

        print()
        print("❌ FOTO NÃO FOI CRIADA")

        return False

    except subprocess.TimeoutExpired:

        print(
            "❌ TIMEOUT DA CAMERA"
        )

        return False

    except Exception as e:

        print()
        print("========================================")
        print("❌ ERRO CAMERA")
        print("========================================")

        print(
            "TIPO:",
            type(e).__name__
        )

        print(
            "ERRO:",
            e
        )

        return False


# ============================================================
# PYTHON -> JAVASCRIPT
# ============================================================

def enviar_comando(webview, comando):

    print()
    print("########################################")
    print("# PYTHON -> JAVASCRIPT")
    print("########################################")

    print("EVENTO:", comando)

    js = "window.robotEvent(" + repr(comando) + ");"

    print("JS:", js)

    try:

        resultado = webview.evaluatejs(
            js
        )

        print("RESULTADO JS:", resultado)

        print("JS ENVIADO COM SUCESSO")

        return True

    except Exception as e:

        print("ERRO AO EXECUTAR JAVASCRIPT:")

        print(e)

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("========================================")
    print("🤖 ROBOT")
    print("========================================")
    print()

    # ========================================================
    # PASTA ATUAL
    # ========================================================

    pasta_atual = os.getcwd()

    print("PASTA ATUAL:")
    print(pasta_atual)

    print()

    # ========================================================
    # HTML
    # ========================================================

    caminho_html = os.path.join(
        pasta_atual,
        "robot.html"
    )

    print("CARREGANDO:")
    print(caminho_html)

    with open(
        caminho_html,
        "r",
        encoding="utf-8"
    ) as f:

        html = f.read()

    print("robot.html CARREGADO")

    # ========================================================
    # CONEXÃO
    # ========================================================

    with termuxgui.Connection() as conn:

        activity = termuxgui.Activity(
            conn
        )

        webview = termuxgui.WebView(
            activity
        )

        print(
            "WEBVIEW CRIADO"
        )

        # ====================================================
        # VISIBILIDADE
        # ====================================================

        webview.setvisibility(
            termuxgui.WebView.VISIBLE
        )

        # ====================================================
        # TAMANHO
        # ====================================================

        webview.setdimensions(
            termuxgui.WebView.MATCH_PARENT,
            termuxgui.WebView.MATCH_PARENT
        )

        # ====================================================
        # FUNDO
        # ====================================================

        webview.setbackgroundcolor(
            0xFF050505
        )

        # ====================================================
        # JAVASCRIPT
        # ====================================================

        print(
            "HABILITANDO JAVASCRIPT..."
        )

        webview.allowjavascript(
            True
        )

        print(
            "JAVASCRIPT HABILITADO"
        )

        # ====================================================
        # TOUCH
        # ====================================================

        print(
            "HABILITANDO TOUCH DO WEBVIEW..."
        )

        webview.sendtouchevent(
            True
        )

        print(
            "TOUCH DO WEBVIEW HABILITADO"
        )

        # ====================================================
        # HTML
        # ====================================================

        print(
            "CARREGANDO robot.html..."
        )

        webview.setdata(
            html
        )

        print(
            "robot.html ENVIADO"
        )

        print()
        print(
            "========================================"
        )
        print(
            "AGUARDANDO WEBVIEW..."
        )
        print(
            "========================================"
        )
        print()

        # ====================================================
        # ESTADO
        # ====================================================

        webview_pronto = False

        # ====================================================
        # LOOP
        # ====================================================

        while True:

            event = conn.checkevent()

            if event:

                print()
                print(
                    "========================================"
                )

                print(
                    "EVENTO RECEBIDO"
                )

                print(
                    "TYPE:",
                    event.type
                )

                print(
                    "VALUE:",
                    event.value
                )

                print(
                    "========================================"
                )

                # ============================================
                # WEBVIEW CARREGADO
                # ============================================

                if event.type == "webviewProgress":

                    progress = event.value.get(
                        "progress",
                        0
                    )

                    print(
                        "WEBVIEW:",
                        progress,
                        "%"
                    )

                    if (
                        progress >= 100
                        and
                        not webview_pronto
                    ):

                        webview_pronto = True

                        print()
                        print(
                            "========================================"
                        )

                        print(
                            "🤖 WEBVIEW CARREGADO"
                        )

                        print(
                            "========================================"
                        )

                        print()

                        print(
                            "🤖 ROBOT PRONTO"
                        )

                        print(
                            "👆 TOQUE NA TELA PARA PISCAR E TIRAR FOTO"
                        )

                        print()

                # ============================================
                # TOUCH
                # ============================================

                elif event.type == "touch":

                    print()
                    print(
                        "👆 TOUCH RECEBIDO PELO PYTHON!"
                    )

                    print(
                        "DADOS DO TOUCH:"
                    )

                    print(
                        event.value
                    )

                    # ----------------------------------------
                    # AÇÃO
                    # ----------------------------------------

                    action = event.value.get(
                        "action"
                    )

                    print(
                        "AÇÃO:",
                        action
                    )

                    # ----------------------------------------
                    # SOMENTE PRESSIONAR
                    # ----------------------------------------

                    if action in (
                        "down",
                        "pointer_down"
                    ):

                        if webview_pronto:

                            print()
                            print(
                                "👆 TOQUE CONFIRMADO"
                            )

                            # =================================
                            # BLINK
                            # =================================

                            print(
                                "👁️ ENVIANDO BLINK..."
                            )

                            enviar_comando(
                                webview,
                                "BLINK"
                            )

                            # =================================
                            # FOTO
                            # =================================

                            print(
                                "📷 TIRANDO FOTO..."
                            )

                            tirar_foto()

                # ============================================
                # JAVASCRIPT CONSOLE
                # ============================================

                elif event.type == "webviewConsoleMessage":

                    print(
                        "JAVASCRIPT:",
                        event.value
                    )

            time.sleep(
                0.01
            )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()