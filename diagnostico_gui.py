import termuxgui
import inspect

print("=" * 60)
print("TERMUX GUI DIAGNOSTICO")
print("=" * 60)

print("\nARQUIVO:")
print(termuxgui.__file__)

print("\nVERSAO PYTHON:")
import sys
print(sys.version)

print("\nVERSAO TERMUX GUI:")
try:
    c = termuxgui.Connection()
    print(c.getversion())
    c.close()
except Exception as e:
    print("ERRO:", repr(e))

classes = [
    "Connection",
    "Activity",
    "View",
    "TextView",
    "Button",
    "LinearLayout",
    "FrameLayout",
    "ImageView",
    "Event",
]

for name in classes:

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    C = getattr(termuxgui, name, None)

    if C is None:
        print("NAO EXISTE")
        continue

    try:
        print("ASSINATURA:")
        print(inspect.signature(C))
    except Exception as e:
        print("assinatura:", repr(e))

    print("\nMETODOS:")

    for method in dir(C):

        if method.startswith("_"):
            continue

        obj = getattr(C, method)

        if callable(obj):

            try:
                sig = inspect.signature(obj)
                print(f"  {method}{sig}")
            except Exception:
                print(f"  {method}")

print("\n" + "=" * 60)
print("EVENTOS")
print("=" * 60)

for x in dir(termuxgui.Event):

    if not x.startswith("_"):

        try:
            print(x, "=", getattr(termuxgui.Event, x))
        except:
            pass

print("\nFIM")
