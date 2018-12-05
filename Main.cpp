#include "ABB.h"
#include "Lista.h"
#include <dirent.h>
#include <vector>
#include <fstream>

vector<string> open(string path = "LA FILES") {

    DIR* dir;
    dirent* pdir;
    vector<string> files;

    dir = opendir(path.c_str());

    while ((pdir = readdir(dir))) {
        files.push_back(pdir->d_name);
    }
    
    return files;
}

int main(){
    
    ABB *abb = new ABB();
    Lista *l = new Lista();
    
    vector<string> f;

    f = open();

    for(vector<string>::iterator it =  f.begin(); it != f.end(); it++){
        ifstream file("LA FILES/"+*it);
        if(file.is_open()){
            string line;
            NohLista *aux = l->inserir((*it));

            while(getline(file, line)){
                if(line[0] != '#'){
                    int cont = 0;
                    string accession = "";
                    for(long unsigned int i=0; i<line.size(); i++){
                        if(line[i] == '\t'){ 
                            cont ++;
                        }
                        if(line[i] != '\t' and cont == 1){
                            accession += line[i];
                        }
                    }
                    aux->lista->inserirInterno(accession);
                    abb->Inserir((*it), aux->posicao);
                    //cout << accession << endl;
                }    
            }
        }
    }
    l->imprimir();
    return 0;
}
