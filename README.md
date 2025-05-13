# 🖥️ WinLink – Resource Sharing Desktop App

WinLink is a desktop application built with Python and PyQt5 that allows a Master PC to monitor system resources (CPU, RAM, Battery) of connected Worker PCs over LAN.

---

## ✅ Required Python Libraries

Install the following libraries before running the project:

pip install PyQt5 psutil
🔧 How to Run the Project (Source Code)
Clone or download this repository.

Open a terminal in the project root.

Run the main file:

python main.py

This will launch the welcome screen. From there, you can choose to run as a Master or Worker PC.

🛠️ How to Build Executable (.exe)
Make sure you have PyInstaller installed:

pip install pyinstaller

Then run:

pyinstaller --onefile --windowed main.py
