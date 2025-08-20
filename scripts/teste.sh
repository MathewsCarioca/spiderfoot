#!/bin/sh
count=$(ls -l $(pwd)/uploads |wc -l)
        for (( n=1; n<$count ; n++ ))do
            echo $n
            varNome=$(ls $(pwd)/uploads/ |head -n$n |tail -n1 | grep -Eo "[^ ]+.txt")
            for j in $(<"`pwd`/uploads/$varNome"); do
                varIP=$j
                echo "varrendo IP $j"
                echo "comando $varNome-$varIP"
                sleep 1
            done
            echo n = $n
            echo Movendo aquivo $(pwd)/uploads/$varNome
            mv $(pwd)/uploads/$varNome $(pwd)/consultados/$varNome
        done
        sleep 5
