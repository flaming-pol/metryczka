---

# Metryczka

Program służy do generowania wirtualnych "pieczątek" na metryczkach strzeleckich do zawodów
KS Amator (<a href="https://braterstwo.eu" target="_blank">https://braterstwo.eu</a>).

Wystarczy wgrać do programu plik PDF z metryczkami wygenerowany podczas zapisów na zawody.
Program automatycznie rozpozna możliwe konkurencje i umożliwi wstawienie "wirtualnych pieczątek" *KLUBOWA*/*WŁASNA*. Program umożliwia wstawienie "wirtualnej pieczątki" *DOPUSZCZENIE* aby skorzystać z promocji moc dopuszczeń.

Po wybraniu interesujących nas konkurencji do "opieczętowania" należy wygenerować metryczki z "wirtualnymi pieczątkami" w formie PDF i wydrukować na **kolorowej drukarce**.

# GUI

Program posiada uniwersalne GUI napisane w QT6. Ta forma pozwala na zapewnienie wieloplatformowości aplikacji, jednak oznacza stosunkowo duże pliki wynikowe po skompilowaniu.

# CLI

Program posiada możliwość uruchomienia w trybie "bez GUI" - przydatne gdy chcemy zautomatyzować proces przygotowania metryczek.

Program w trybie konsolowym wymaga podania następujących parametrów:
  ```
  --no-gui, -n          uruchamia program w trybie konsolowym
  --in INPUT_FILE       ścieżka do pliku pdf z metryczkami (plik źródłowy)
  --out OUTPUT_FILE     nazwa pliku z wstawionymi pieczątkami. Jeśli nie podasz nazwy pliku, ostęplowane metryczki zostaną
                        zapisane pod nazwą taką jak plik źródłowy tylko z dopiskiem "-stamp"
  -d                    dopuszczenie - pierwsza metryczka będzie oznaczona "DOP"
  --competitions COMPETITIONS, -c COMPETITIONS
                        Nazwy konkurencji, które chcesz umieścić na metryczkach, wg. formatu: NAZWA_KONKURECNJI:OPCJE. Program
                        przewiduje następujące opcje do konkurencji: "w" - pieczątka "własna", "k" - pieczątka "klubowa", "b" -
                        brak pieczątki. Gdy strzelasz więcej konkurencji rozdziel je przecinkiem. Przykład:
                        Kcz10m5:w,Pcz25m10z13:k program wygeneruje metryczki dla konkurencji "Kcz10m5" z pieczątką "własna" oraz
                        dla konkurencji Pcz25m10z13 z pieczątką "klubowa". Wskazane konkurencje muszą znajdować się na metryczkach
                        źródłowych.
  ```

# Skrypt ``metryczka_script.sh``

Skrypt stanowi "wrapper" na program w trybie konsolowym. Przydatny w sytuacji gdy często strzelamy z góry przewidziane zawody. W treści skryptu wpisujemy konkurencje, które skrypt ma oznaczyć na metryczkach. Skrypt przyjmuje jeden parametr - nazwę pliku źródłowego z metryczkami. Skrypt można skonfigurować do automatycznego drukowania metryczek.

Istotne sekcje w kodzie skryptu:
  ```
  MOJE_KONKURENCJE="Pcz25m10z13:w,Ksp25m10:k,pm25m10:w,Strzelba25m10:b"

  # Jeśli chcesz umiescić symbol dopuszczenia, zmień "0" na "1"
  DOPUSZCZENIE=0

  # Jeśli chcesz automatycznie wydrukować metryczki, ustaw "1"
  DRUKUJ=0
  ```

## Instalacja w środowisku Windows (pojedynczy plik EXE)

Z zakładki *Releases* na Githubie należy kliknąć aktualną wersję (*Latest*), następnie z drzewka *Assets* pobrać, oraz uruchomić plik ``metryczka.exe`` - to jest skompilowane archiwum zawierające program, interpreter języka Python oraz m.in. biblioteki Qt6.
Plik wynikowy został wygenerowany przy pomocy narzędzia ``pyinstaller``.

## Instalacja w środowisku Linux (pojedynczy plik BIN)

Z zakładki *Releases* na Githubie należy kliknąć aktualną wersję (*Latest*), następnie z drzewka *Assets* pobrać, oraz uruchomić plik ``metryczka.bin`` - to jest skompilowane archiwum zawierające program, interpreter języka Python oraz m.in. biblioteki Qt6. Przed uruchomienime należy nadać uprawnienia wykonywalności ``chmod +x metryczka.bin``.
Plik wynikowy został wygenerowany przy pomocy narzędzia ``pyinstaller``.

## Instalacja w środowisku macOS (pojedynczy plik ZIP)

Z zakładki *Releases* na Githubie należy kliknąć aktualną wersję (*Latest*), następnie z drzewka *Assets* pobrać, oraz uruchomić plik ``metryczka-macOS-arm64.zip`` lub ``metryczka-macOS-intel.zip`` w zależności od architektury - to jest skompilowane archiwum zawierające program, interpreter języka Python oraz m.in. biblioteki Qt6.
**UWAGA**: z racji tego, że autor nie ma komputera z systemem macOS, releasy nie są testowane!
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
