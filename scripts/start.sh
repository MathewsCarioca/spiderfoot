#!/bin/sh

[[ -e "/home/spiderfoot/uploads" ]]; mkdir -p /home/spiderfoot/uploads && chmod -R 777 /home/spiderfoot/uploads
while true ;do
    sleep 1
    dir="/home/spiderfoot/uploads"
    if find "$dir" -type f -name "*.txt" | grep -q .; then
       echo "Tem arquivos .txt na pasta uploads/"

## vericar essa etapa acima
        count=1
        #for i in $(ls /home/spiderfoot/scripts/uploads/*.txt);do 
        for i in $(ls /home/spiderfoot/uploads/*.txt);do 
            echo arquivo $i | grep -Eo "[^/]+txt" 
            sleep 2
            #varNome=$(ls /home/spiderfoot/scripts/uploads/ |head -n $count |tail -n1)
            varNome=$(ls /home/spiderfoot/uploads/ |head -n $count |tail -n1)
            
            #for j in $(paste /home/spiderfoot/scripts/uploads/$varNome);do
            for j in $(paste /home/spiderfoot/uploads/$varNome);do
                varIP=$j
                echo "varrendo IP $varIP"
                echo "comando $varNome-$varIP"
                sleep 3
                scanTarget=`echo $varNome | grep -Eo "^.+[^.txt]"`
                nohup $(printf 'start %s -t IP_ADDRESS -n %s\n' "$varIP" "$scanTarget" | /home/spiderfoot/sfcli.py) >/dev/null 2>&1 &
            done
            sleep 2
            count=$((count+1))
            
            echo Scan "$scanTarget-$varIP"
            echo Removendo aquivo "/home/spiderfoot/uploads/$varNome"
            
            rm $dir/$varNome
        done
        sleep 2
    else
        echo "A pasta esta vazia ou nao contem arquivos .txt"
    fi
done
