[ -d fasta ] || mkdir fasta 

echo DOWNLOADING SEQUENCES

while read line; do
	wget -q -O fasta/"$line".fasta "https://www.ncbi.nlm.nih.gov/sviewer/viewer.fcgi?id="+$line+"&db=protein&report=fasta&extrafeat=null&conwithfeat=on&hide-cdd=on&retmode=html&withmarkup=on&tool=portal&log$=seqview&maxdownloadsize=1000000"
done < seq

echo DONE. CHECK /fasta 
