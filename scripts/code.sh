#!/bin/sh

[[ -e $(pwd)/uploads ]]; mkdir -p $(pwd)/uploads && chmod -R 777 $(pwd)/uploads
dir="/home/spiderfoot/scripts/uploads"
while true ;do
    if find "$dir" -type f -name "*.txt" | grep -q .; then
       echo "Tem arquivos .txt na pasta uploads/"

## vericar essa etapa acima
        count=1
        for i in $(ls /home/spiderfoot/scripts/uploads/*.txt);do 
            echo arquivo $i | grep -Eo "[^/]+txt" 
            sleep 2
            varNome=$(ls /home/spiderfoot/scripts/uploads/ |head -n $count |tail -n1)

            for j in $(paste /home/spiderfoot/scripts/uploads/$varNome);do
                varIP=$j
                echo "varrendo IP $varIP"
                echo "comando $varNome-$varIP"
                sleep 1
            done
            sleep 3
            count=$((count+1))
            scanTarget=`echo $varNome | grep -Eo "^.+[^.txt]"`
            echo Scan "$scanTarget-$varIP"
            echo Movendo aquivo "/home/spiderfoot/scripts/uploads/$varNome"
            mv $(pwd)/uploads/$varNome $(pwd)/consultados/$varNome
        done
        sleep 2
    else
        echo "A pasta esta vazia ou nao contem arquivos .txt"
    fi
    sleep 2
done
