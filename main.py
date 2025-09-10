# main.py
from ui import build_ui

if __name__ == "__main__":
    demo = build_ui()
    demo.launch(inbrowser=True,share=True)  # share=False karena lokal saja
