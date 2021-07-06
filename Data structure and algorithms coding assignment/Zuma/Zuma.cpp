// Defining and using unnessary class "chain" would slow down the program a lot.

#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <string.h>
using namespace std;

struct bead {
public:
	char color; bead* pred; bead* succ;

	bead() {}
	bead(char c, bead* p = NULL, bead* s = NULL) :color(c), pred(p), succ(s) {}
	bead* insertAsPre(char color) {
		bead* b = new bead(color, this->pred, this);
		this->pred->succ = b;
		this->pred = b;
		return b;
	}
	void remove() {
		this->pred->succ = this->succ;
		this->succ->pred = this->pred;
		delete this;
	}
};

//class chain {
//public:
//	int _size; bead* header; bead* trailer;
//
//	chain() {
//		header = new bead('-');
//		trailer = new bead('-');
//		header->pred = NULL; header->succ = trailer;
//		trailer->pred = header; trailer->succ = NULL;
//		_size = 0;
//	}
//	~chain() {
//		while (_size--) {
//			remove(header->succ);
//		}
//		delete header;
//		delete trailer;
//	}
//	bead* insertB(bead* b, char color) {
//		_size++;
//		return b->insertAsPre(color);
//	}
//	bead* insertAsLast(char color) {
//		_size++;
//		return trailer->insertAsPre(color);
//	}
//	char remove(bead* b) {
//		char c = b->color;
//		_size--;
//		b->pred->succ = b->succ;
//		b->succ->pred = b->pred;
//		delete b;
//		return c;
//	}
//};

int main() {
	//	char S[10010];
	bead* header = new bead('-');
	bead* trailer = new bead('-');
	header->pred = NULL; header->succ = trailer;
	trailer->pred = header; trailer->succ = NULL;
	char col;
	//	scanf("%s", &*S);
	//	int n = (int)strlen(S);
	//	for(int i =0;i<n;i++) {C.insertAsLast(S[i]);}
	while ((col = getchar()) != '\n') { trailer->insertAsPre(col); }
	int M;
	scanf("%d", &M);
	int rank;
	while (M--) {
		bead* b = header->succ;
		scanf("%d %c", &rank, &col);
		while (rank--) {
			b = b->succ;
		}
		b = b->insertAsPre(col);
		while (true) {
			int j = 1;
			bead* l = b; bead* r = b;
			while ((l != header) && ((l = l->pred)->color == col)) { j++; }
			while ((r != trailer) && ((r = r->succ)->color == col)) { j++; }
			if (j > 2) {
				l = l->succ;
				while (l != r) { l = l->succ; l->pred->remove(); }
				b = l == trailer ? l->pred : l;
				col = l->color;
			}
			else break;
		}
		bead* t = header->succ;
		if (t == trailer) putchar('-');
		else {
			for (; t != trailer; t = t->succ) {
				putchar(t ->color);
			}
		}
		putchar('\n');
	}
	return 0;
}
