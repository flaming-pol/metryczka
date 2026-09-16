#!/usr/bin/env bash

# Wpisujemy konkurencje wg. wzorca, wiele konkurencji rozdzielamy przecinkiem:
#  NAZWA:OPCJA
#   gdzie OPCJA to jedna litera: w/k/b oznaczająca pieczątkę:
#    w - WŁASNA
#    k - KLUBOWA
#    b - brak pieczątki
#
# Przykład:
# MOJE_KONKURENCJE="Strzelba25m5:w,Strzelba25m10:k,Psp25m10z13:w,Pm25m10:k,Pcz25m10z13:w,Ksp25m10:w,Kczkp25m10:b"
MOJE_KONKURENCJE="Pcz25m10z13:w,Ksp25m10:k,pm25m10:w,Strzelba25m10:b"

# Jeśli chcesz umiescić symbol dopuszczenia, zmień "0" na "1"
DOPUSZCZENIE=0

# Jeśli chcesz automatycznie wydrukować metryczki, ustaw "1"
DRUKUJ=0

if [[ -z "$1" ]]; then
    echo "Jako argument skryptu podaj ścieżkę do pliku z metryczkami!" >&2
    exit 1
fi
SRC_FILE=$1
DST_FILE="${SRC_FILE}-STAMP.pdf"

python metryczka.py --no-gui --in $SRC_FILE --out $DST_FILE --competitions $MOJE_KONKURENCJE $([[ "$DOPUSZCZENIE" -eq 1 ]] && echo "-d")

if [[ "$DRUKUJ" -eq 1 && -f "$DST_FILE" ]]; then
  # można też dodać opjcę:
  #  -d destination          Specify the destination
  lp -o sides=one-sided -H immediate $DST_FILE
fi
