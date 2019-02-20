mkdir blast
cd blast;wget ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.7.1/ncbi-blast-2.7.1+-x64-linux.tar.gz 
cd blast;tar -zxvf ncbi-blast-2.7.1+-x64-linux.tar.gz 
cd blast;rm -rf ncbi-blast-2.7.1+-x64-linux.tar.gz

echo GERANDO ARQUIVOS DE ENTRADA

cont=0

while read line; do
	cont=$((cont+1))
	echo \#"$cont" GERANDO ARQUIVO PARA ESPECIE "$line"
	tosave="$(echo $line | tr -d /)"
	tosave="$(echo $line | tr ' ' _)"
	echo SALVANDO ARQUIVO COMO "$tosave"
	blast/ncbi-blast-2.7.1+/bin/blastp -query proteina -db nr -remote -entrez_query "$line" -outfmt 7 > LA\ FILES/"$tosave".la
done < especies
echo FIM DO PROCESSO

