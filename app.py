import time
import termuxgui


def main():

    print()
    print("========================================")
    print("🤖 ROBOT")
    print("========================================")
    print()

    # Carrega o arquivo robot.html
    with open("robot.html", "r", encoding="utf-8") as f:
        html = f.read()

    with termuxgui.Connection() as conn:

        activity = termuxgui.Activity(conn)

        # WEBVIEW
        webview = termuxgui.WebView(activity)

        print("WEBVIEW CRIADO")

        # VISIBILIDADE
        webview.setvisibility(
            termuxgui.WebView.VISIBLE
        )

        # TAMANHO
        webview.setdimensions(
            termuxgui.WebView.MATCH_PARENT,
            termuxgui.WebView.MATCH_PARENT
        )

        # FUNDO
        webview.setbackgroundcolor(
            0xFF050505
        )

        # JAVASCRIPT
        webview.allowjavascript(
            True
        )

        # CARREGAR robot.html
        print("CARREGANDO robot.html...")

        webview.setdata(
            html
        )

        print("robot.html ENVIADO")
        print()
        print("A tela deve mostrar o conteúdo do robot.html.")
        print()

        # LOOP
        while True:

            event = conn.checkevent()

            if event:
                print(
                    "EVENTO:",
                    event.type,
                    event.value
                )

            time.sleep(0.03)


if __name__ == "__main__":
    main()
