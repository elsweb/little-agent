import time
import termuxgui


def enviar_comando(webview, comando):

    print()
    print("########################################")
    print("# PYTHON -> JAVASCRIPT")
    print("########################################")

    print("EVENTO:", comando)

    js = "window.robotEvent(" + repr(comando) + ");"

    print("JS:", js)

    try:

        resultado = webview.evaluatejs(js)

        print("RESULTADO JS:", resultado)

        print("JS ENVIADO COM SUCESSO")

        return True

    except Exception as e:

        print("ERRO AO EXECUTAR JAVASCRIPT:")

        print(e)

        return False


def main():

    print()
    print("========================================")
    print("🤖 ROBOT")
    print("========================================")
    print()

    # --------------------------------------
    # HTML
    # --------------------------------------

    with open(
        "robot.html",
        "r",
        encoding="utf-8"
    ) as f:

        html = f.read()


    # --------------------------------------
    # CONEXÃO
    # --------------------------------------

    with termuxgui.Connection() as conn:

        activity = termuxgui.Activity(conn)

        webview = termuxgui.WebView(activity)

        print(
            "WEBVIEW CRIADO"
        )


        # --------------------------------------
        # VISIBILIDADE
        # --------------------------------------

        webview.setvisibility(
            termuxgui.WebView.VISIBLE
        )


        # --------------------------------------
        # TAMANHO
        # --------------------------------------

        webview.setdimensions(
            termuxgui.WebView.MATCH_PARENT,
            termuxgui.WebView.MATCH_PARENT
        )


        # --------------------------------------
        # FUNDO
        # --------------------------------------

        webview.setbackgroundcolor(
            0xFF050505
        )


        # --------------------------------------
        # JAVASCRIPT
        # --------------------------------------

        print(
            "HABILITANDO JAVASCRIPT..."
        )

        webview.allowjavascript(True)

        print(
            "JAVASCRIPT HABILITADO"
        )


        # --------------------------------------
        # TOUCH
        # --------------------------------------

        print(
            "HABILITANDO TOUCH DO WEBVIEW..."
        )

        webview.sendtouchevent(
            True
        )

        print(
            "TOUCH DO WEBVIEW HABILITADO"
        )


        # --------------------------------------
        # HTML
        # --------------------------------------

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


        # --------------------------------------
        # ESTADO
        # --------------------------------------

        webview_pronto = False


        # --------------------------------------
        # LOOP
        # --------------------------------------

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


                # ==================================
                # WEBVIEW CARREGADO
                # ==================================

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
                            "👆 TOQUE NA TELA PARA PISCAR"
                        )

                        print()


                # ==================================
                # TOUCH
                # ==================================

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


                    # ----------------------------------
                    # AÇÃO DO TOUCH
                    # ----------------------------------

                    action = event.value.get(
                        "action"
                    )


                    print(
                        "AÇÃO:",
                        action
                    )


                    # ----------------------------------
                    # PISCAR SOMENTE AO PRESSIONAR
                    # ----------------------------------

                    if action in (
                        "down",
                        "pointer_down"
                    ):

                        if webview_pronto:

                            print(
                                "👁️ ENVIANDO BLINK..."
                            )

                            enviar_comando(
                                webview,
                                "BLINK"
                            )


                # ==================================
                # EVENTOS DE TOUCH DIRETOS
                # ==================================

                elif event.type == "down":

                    print(
                        "👆 TOUCH DOWN"
                    )

                    print(
                        event.value
                    )

                    if webview_pronto:

                        enviar_comando(
                            webview,
                            "BLINK"
                        )


                elif event.type == "pointer_down":

                    print(
                        "👆 POINTER DOWN"
                    )

                    print(
                        event.value
                    )

                    if webview_pronto:

                        enviar_comando(
                            webview,
                            "BLINK"
                        )


                # ==================================
                # JAVASCRIPT CONSOLE
                # ==================================

                elif event.type == "webviewConsoleMessage":

                    print(
                        "JAVASCRIPT:",
                        event.value
                    )


            time.sleep(
                0.01
            )


if __name__ == "__main__":

    main()