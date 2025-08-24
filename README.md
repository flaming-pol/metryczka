---

# Metryczka

Program służy do generowania wirtualnych "pieczątek" na metryczkach strzeleckich do zawodów
KS Amator (<a href="https://braterstwo.eu" target="_blank">https://braterstwo.eu</a>).

Wystarczy wgrać do programu plik PDF z metryczkami wygenerowany podczas zapisów na zawody.
Program automatycznie rozpozna możliwe konkurencje i umożliwi wstawienie "wirtualnych pieczątek" *KLUBOWA*/*WŁASNA*. Program umożliwia wstawienie "wirtualnej pieczątki" *DOPUSZCZENIE* aby skorzystać z promocji moc dopuszczeń.

Po wybraniu interesujących nas konkurencji do "opieczętowania" należy wygenerować metryczki z "wirtualnymi pieczątkami" w formie PDF i wydrukować na **kolorowej drukarce**.

## Instalacja w środowisku Windows (pojedynczy plik EXE)

Z zakładki *Releases* na Githubie należy kliknąć aktualną wersję (*Latest*), następnie z drzewka *Assets* pobrać, oraz uruchomić plik ``metryczka.exe`` - to jest skompilowane archiwum zawierające program, interpreter języka Python oraz m.in. biblioteki Qt6.
Plik wynikowy został wygenerowany przy pomocy narzędzia ``pyinstaller``.

## Instalacja w środowisku Linux (pojedynczy plik BIN)

Z zakładki *Releases* na Githubie należy kliknąć aktualną wersję (*Latest*), następnie z drzewka *Assets* pobrać, oraz uruchomić plik ``metryczka.bin`` - to jest skompilowane archiwum zawierające program, interpreter języka Python oraz m.in. biblioteki Qt6. Przed uruchomienime należy nadać uprawnienia wykonywalności ``chmod +x metryczka.bin``.
Plik wynikowy został wygenerowany przy pomocy narzędzia ``pyinstaller``.

## Instalacja w środowisku Windows (Python + Virtual Env)

1. Program był pisany w środowisku Linux, ale przy użyciu bibliotek, które mają wsparcie dla systemu Windows, więc *wszystko powinno działać*.
Autor nie ponosi odpowiedzialności za pracę programu w systemie Windows oraz nie udziela żadnego wsparcia co do obsługi programu w systemie Windows;

1. Musisz mieć zainstalowany interpreter języka Python 3, można pobrać gotowy, skompilowany w formie instalatora z <a href="https://www.python.org/downloads/windows/">do pobrania stąd</a> Warto wybrać najnowszą wersję. **UWAGA: podczas instalacji Python należy koniecznie zaznaczyć opcję "Add python.exe to PATH"**;

1. Należy pobrać kod tego programu do metryczek z Githuba na swój komputer;

1. Uruchomić skrypt ``windows_install.bat`` z katalogu z programem. Skrypt zainstaluje niezbędne biblioteki korzystając ze środowiska Virtual Env, w katalogu ``venv``;

1. Uruchomić skrypt ``windows_start.bat``, który załaduje środowisko wirtualne oraz uruchomi program do metryczek.

## Instalacja w środowisku Linux

1. Należy utworzyć środowisko wirtualne do pythona 3:
``python3 -m venv venv``

1. Aktywować środowisko Virtual Env
``source venv/bin/activate``

1. Zainstalować zależności przy pomocy PIP-a:
``pip install -r requirements.txt``
lub wersję deweloperską:
``pip install -r requirements-dev.txt``

1. Uruchomić program
``python metryczka.py``

1. Można też użyć programu w wesji terminalowej:
``python metryczka_cli.py``
