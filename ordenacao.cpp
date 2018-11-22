#include <iostream>
#include <fstream>
#include <cstdio>
#include <cstdlib>

using namespace std;

struct Dado{
public:
	int chave1;
	int chave2;
	float valor1;
	char campo1[5];
	char campo2[20];
	char lixo[500];
};

bool intercalaBloco ( ifstream auxE[2], ofstream auxS[2], int passo, int saida){
	bool intercalou = false;
	Dado dados[2];
	int pos[2] = {0,0};
	bool valido[2] = {false, false};
	while ((pos[0]+pos[1]) < (2*passo) ){
		if ( (pos[0] < passo) && (not valido[0])){
			if ( auxE[0].read((char*) &dados[0], sizeof(Dado)) ){
				cout << "leu arq1" << endl;
				valido[0] = true;
			}
			else{
				pos[0] = passo;
				cout << "arq1 acabou" << endl;
			}
		}
		if ( (pos[1] < passo) && (not valido[1])){
			if ( auxE[1].read((char*) &dados[1], sizeof(Dado)) ){
				cout << "leu arq2" << endl;
				valido[1] = true;
			}
			else{
				pos[1] = passo;
				cout << "arq2 acabou" << endl;
			}
		}
		if (valido[0] and valido[1] ){
			intercalou = true;
			if (dados[0].chave1 <= dados[1].chave1){
				auxS[saida].write((const char*)(&dados[0]), sizeof(Dado));
				valido[0] = false;
				pos[0]++;
			}else{
				auxS[saida].write((const char*)(&dados[1]), sizeof(Dado));
				valido[1] = false;
				pos[1]++;
			}
		}
		else if (valido[0]){
			intercalou = true;
			auxS[saida].write((const char*)(&dados[0]), sizeof(Dado));
			valido[0] = false;
			pos[0]++;
		}
		else if (valido[1]){
			intercalou = true;
			auxS[saida].write((const char*)(&dados[1]), sizeof(Dado));
			valido[1] = false;
			pos[1]++;
		}
		else{
			cout << "circulando..." << endl;
		}
	}
	return intercalou;
}
void mergeexterno ( ifstream &arqEntrada, ofstream &arqSaida){
	ofstream arqB1("arqB1.dat", ios::binary);
	ofstream arqB2("arqB2.dat", ios::binary);
	
	if ((not arqB1) or (not arqB2)){
		cerr << "nao foi possivel abrir os arquivos" << endl;
		exit(EXIT_FAILURE);
	}
	Dado umDado;
	
	arqEntrada.seekg(0, ios::end);
	int tamanho = arqEntrada.tellg();
	int numRegistros = tamanho / sizeof(Dado);
	int metade = (numRegistros/2.0)+0.5;
	arqEntrada.seekg(0,ios::beg);
	
	for ( int i = 0; i < metade; i++){
		arqEntrada.read((char*) &umDado, sizeof(Dado));
		arqB1.write((char*) &umDado, sizeof(Dado));
	}
	for ( int i = metade; i < numRegistros; i++){
		arqEntrada.read((char*) &umDado, sizeof(Dado));
		arqB2.write((char*) &umDado, sizeof(Dado));
	}
	arqB1.close();
	arqB2.close();
	arqEntrada.close();
	
	ifstream auxEntrada[2];
	ofstream auxSaida[2];
	
	int passo = 1;
	bool ida = true;
	bool ultimo[2];
	
	while ( passo <= numRegistros ){
		if (ida){
			auxEntrada[0].open("arqB1.dat", ios::binary);
			auxEntrada[1].open("arqB2.dat", ios::binary);
			auxSaida[0].open("arqC1.dat", ios::binary);
			auxSaida[1].open("arqC2.dat", ios:: binary);
		}else{
			auxEntrada[0].open("arqC1.dat", ios::binary);
			auxEntrada[1].open("arqC2.dat", ios::binary);
			auxSaida[0].open("arqB1.dat", ios::binary);
			auxSaida[1].open("arqB2.dat", ios:: binary);
		}
		
		if ((not auxEntrada[0]) or (not auxEntrada[1]) or (not auxSaida[0]) or (not auxSaida[1])){
			cerr << "arq aux nao podem ser abertos" << endl;
			exit(EXIT_FAILURE);
		}
		while((not auxEntrada[0].eof()) and (not auxEntrada[1].eof())){
			ultimo[0] = intercalaBloco(auxEntrada, auxSaida, passo, 0 );
			ultimo[1] = intercalaBloco(auxEntrada, auxSaida, passo, 1);
		}
		
		auxEntrada[0].close();
		auxEntrada[1].close();
		auxSaida[0].close();
		auxSaida[1].close();
		
		ida = not(ida);
		passo *= 2;
	}
	ifstream auxEnt;
	
	if (ida){
		if (ultimo[0] ){
			auxEnt.open("arqB1.dat", ios:: binary);
		}else{
			auxEnt.open ("arqB2.dat", ios:: binary);
		}
	}
	else{
		if (ultimo[0] ){
			auxEnt.open("arqC1.dat", ios:: binary);
		}else{
			auxEnt.open ("arqC2.dat", ios:: binary);
		}
	}
	if ( not auxEnt ){
		cerr << "arq aux nao foram abertos" << endl;
		exit(EXIT_FAILURE);
	}
	while ( auxEnt.read((char*) (&umDado), sizeof(Dado))){
		arqSaida.write((const char*)(&umDado), sizeof(Dado));
	}
	auxEnt.close();
	remove("arqB1.dat");
	remove("arqB2.dat");
	remove("arqC1.dat");
	remove("arqC2.dat");
}
int main( int argc, char* argv[]){
	if ( argc != 3){
		cerr << "Uso: " << argv[0] << " arquivoEntrada arquivoSaida" << endl;
		exit(EXIT_FAILURE);
	}
	ifstream entrada(argv[1], ios:: binary);
	ofstream saida(argv[2], ios:: binary);
	if (not entrada){
		cerr << " arq de ent nao foi aberto" << endl;
		exit(EXIT_FAILURE);
	}
	if (not saida){
		cerr << " arq de saida nao foi aberto" << endl;
		exit(EXIT_FAILURE);
	}
	mergeexterno(entrada, saida);
	entrada.close();
	saida.close();
	return 0;
}
