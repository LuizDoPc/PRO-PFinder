sudo apt-get install ncbi-blast+

while read line; do
	blastp -query proteina -db nr -remote -entrez_query "$line" -outfmt 7 > LA\ FILES/"$line".la
done < especies

