#mkdir blast
#cd blast;wget ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.7.1/ncbi-blast-2.7.1+-x64-linux.tar.gz
#cd blast;tar -zxvf ncbi-blast-2.7.1+-x64-linux.tar.gz
#cd blast;rm -rf ncbi-blast-2.7.1+-x64-linux.tar.gz

echo GERANDO ARQUIVOS DE ENTRADA

cont=1

while read line; do
	echo \#"$cont" GERANDO ARQUIVO PARA ESPECIE "$line"
	blast/ncbi-blast-2.7.1+/bin/blastp -query proteina -db nr -remote -entrez_query "$line" -outfmt 7 > LA\ FILES/"$line".la
done < especies
echo FIM DO PROCESSO

