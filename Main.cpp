#include "ABB.h"
#include "TabelaHash.h"
#include <dirent.h>
#include <vector>
#include <fstream>

vector<string> open(string path = "LA FILES") {

    DIR*    dir;
    dirent* pdir;
    vector<string> files;

    dir = opendir(path.c_str());

    while ((pdir = readdir(dir))) {
        files.push_back(pdir->d_name);
    }
    
    return files;
}

int main(int argc, char const *argv[]){
    
    ABB *abb = new ABB();
    TabelaHash *th = new TabelaHash(194);

    
    vector<string> f;

    f = open();

    int k = 0;
    for(vector<string>::iterator it =  f.begin(); it != f.end() and k < 5; it++, k++){
        ifstream file("LA FILES/"+*it);
        if(file.is_open()){
            string line;

            while(getline(file, line)){
                if(line[0] != '#'){
                    int cont = 0;
                    string accession = "";
                    for(int i=0; i<line.size(); i++){
                        if(line[i] == '\t'){ 
                            cont ++;
                        }
                        if(line[i] != '\t' and cont == 1){
                            accession += line[i];
                        }
                    }
                    
                    int pos = th->insere(accession);
                    abb->Inserir(*th, pos);
                    //cout << accession << endl;
                }    
            }
        }
    }
    return 0;
}
