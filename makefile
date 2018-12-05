main: ABB.cpp Lista.cpp Main.cpp
	g++ -c ABB.cpp
	g++ -c Lista.cpp
	g++ -c Main.cpp
	g++ -o ed.larun ABB.o Lista.o Main.o