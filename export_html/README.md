# Como instalar 
São 3 arquivos que sofreram update para termos a geração dos relatórios (relatórios em HTML).

## Arquivos modificados
* sfwebui.py 
* scaninfo.tmpl
* spiderfoot.scanlist.js

# Como instalar
Vamos ter que substiuir os arquivos originais do Spiderfoot por esses 3 novos, devemos deletar os que já existem, inserir esses novos e dar permissão para cada arquivo. Cada arquivo vai tem um diretório que é:

* sfwebui.py --> Raiz do projeto (spiderfoot)
* scaninfo.tmpl --> Pasta templates (spiderfoot/spiderfoot/templates)
* spiderfoot.scanlist.js --> pasta static/js (spiderfoot/spiderfoot/static/js)