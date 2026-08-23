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

    with open("robot.html", "r", encoding="utf-8") as f:
        html = f.read()


    # --------------------------------------
    # CONEXÃO
    # --------------------------------------

    with termuxgui.Connection() as conn:

        activity = termuxgui.Activity(conn)

        webview = termuxgui.WebView(activity)

        print("WEBVIEW CRIADO")


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

        print("HABILITANDO JAVASCRIPT...")

        webview.allowjavascript(True)

        print("JAVASCRIPT HABILITADO")


        # --------------------------------------
        # CARREGAR HTML
        # --------------------------------------

        print("CARREGANDO robot.html...")

        webview.setdata(html)

        print("robot.html ENVIADO")
        print()

        print("AGUARDANDO WEBVIEW...")
        print()


        # --------------------------------------
        # ESTADO
        # --------------------------------------

        webview_pronto = False


        # --------------------------------------
        # LOOP PRINCIPAL
        # --------------------------------------

        while True:

            event = conn.checkevent()


            if event:

                print(
                    "EVENTO:",
                    event.type,
                    event.value
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


                    if progress >= 100 and not webview_pronto:

                        webview_pronto = True

                        print()
                        print("========================================")
                        print("WEBVIEW CARREGADO")
                        print("========================================")
                        print()

                        time.sleep(0.5)

                        # Verifica se a função existe

                        try:

                            resultado = webview.evaluatejs(
                                "typeof window.robotEvent"
                            )

                            print(
                                "robotEvent:",
                                resultado
                            )

                        except Exception as e:

                            print(
                                "ERRO AO VERIFICAR robotEvent:",
                                e
                            )

                        print()
                        print("🤖 ROBOT PRONTO")
                        print("AGUARDANDO TOUCH...")
                        print()


                # ==================================
                # CONSOLE JAVASCRIPT
                # ==================================

                elif event.type == "webviewConsoleMessage":

                    print(
                        "JAVASCRIPT:",
                        event.value
                    )


                # ==================================
                # TOUCH
                # ==================================

                elif event.type == "touch":

                    action = event.value.get(
                        "action"
                    )

                    x = event.value.get(
                        "pointers",
                        [{}]
                    )[0].get(
                        "x",
                        0
                    )

                    y = event.value.get(
                        "pointers",
                        [{}]
                    )[0].get(
                        "y",
                        0
                    )


                    print()
                    print("========================================")
                    print("👆 TOUCH CAPTURADO PELO PYTHON")
                    print("========================================")

                    print("AÇÃO:", action)
                    print("X:", x)
                    print("Y:", y)


                    # ----------------------------------
                    # DISPARA SOMENTE QUANDO SOLTAR
                    # ----------------------------------

                    if action == "up":

                        print()
                        print("PYTHON DETECTOU TOQUE COMPLETO")

                        enviar_comando(
                            webview,
                            "BLINK"
                        )

                        print()
                        print("AGUARDANDO PRÓXIMO TOUCH...")
                        print()


            time.sleep(0.01)


if __name__ == "__main__":
    main()