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

        webview.evaluatejs(js)

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

        print(
            "HABILITANDO JAVASCRIPT..."
        )

        webview.allowjavascript(True)

        print(
            "JAVASCRIPT HABILITADO"
        )


        # --------------------------------------
        # HTML
        # --------------------------------------

        print(
            "CARREGANDO robot.html..."
        )

        webview.setdata(html)

        print(
            "robot.html ENVIADO"
        )

        print()
        print(
            "AGUARDANDO WEBVIEW..."
        )
        print()


        # --------------------------------------
        # ESTADO
        # --------------------------------------

        webview_pronto = False

        ultimo_blink = 0


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
                            "BLINK AUTOMÁTICO A CADA 2 SEGUNDOS"
                        )

                        print()


                # ==================================
                # JAVASCRIPT CONSOLE
                # ==================================

                elif event.type == "webviewConsoleMessage":

                    print(
                        "JAVASCRIPT:",
                        event.value
                    )


            # ==========================================
            # BLINK AUTOMÁTICO
            # ==========================================

            if webview_pronto:

                agora = time.monotonic()


                if (
                    agora - ultimo_blink
                    >= 2
                ):

                    ultimo_blink = agora

                    enviar_comando(
                        webview,
                        "BLINK"
                    )


            time.sleep(
                0.01
            )


if __name__ == "__main__":

    main()