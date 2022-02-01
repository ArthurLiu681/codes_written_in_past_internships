//利用康托展开对整数数组进行散射
#include <iostream>
using namespace std;
#define DEFAULT_CAPACITY  3
#define Rank int
#include <cstring>

static int hashCode(int* V) {
	int fac[8] = { 1, 1, 2, 6, 24, 120, 720, 5040 };
	int x = 0;
	for (int i = 0; i < 8; i++) {
		int k = 0;
		for (int j = 0; j < i; j++) {
			if (V[j] < V[i])k++;
		}
		x = x + k * fac[i];
	}
	return x;
}

struct label {
public:
	int* V;
	int hash;
	int visited;
	label(int* v = NULL, int vi = -1) :visited(vi) {
		V = new int[8];
		if (v) {
			for (int i = 0; i < 8; i++) {
				V[i] = v[i];
			}
		}
		hash = hashCode(V);
	}
	label(label& l) : hash(l.hash), visited(l.visited) {
		V = new int[8];
		for (int i = 0; i < 8; i++) {
			V[i] = l.V[i];
		}
	}
	label& operator=(label& l) {
		hash = l.hash;
		visited = l.visited;
		for (int i = 0; i < 8; i++) {
			V[i] = l.V[i];
		}
		return *this;
	}
	~label() {
		delete V;
	}
};

int* Op1(int*& s) {
	int* v = new int[8];
	for (int i = 0; i < 8; i++) {
		v[i] = s[7 - i];
	}
	return v;
}

int* Op2(int*& s) {
	int* v = new int[8];
	v[3] = s[0];
	for (int i = 0; i < 3; i++) {
		v[i] = s[i + 1];
	}
	v[4] = s[7];
	for (int i = 5; i < 8; i++) {
		v[i] = s[i - 1];
	}
	return v;
}

int* Op3(int*& s) {
	int* v = new int[8];
	v[0] = s[0];
	v[1] = s[2];
	v[2] = s[5];
	v[3] = s[3];
	v[4] = s[4];
	v[5] = s[6];
	v[6] = s[1];
	v[7] = s[7];
	return v;
}

int n;
int s[8];
label candidate[40320];
int d[40320];

int main() {
	for (int i = 0; i < 40320; i++) {
		d[i] = -1;
	}
	int t[8] = { 1, 2, 3, 4, 5, 6, 7, 8 };
	scanf("%d", &n);
	int* output = new int[n];
	label temp(t, 0);
	d[temp.hash] = 0;
	int head = 0;
	int tail = 0;
	candidate[tail++] = temp;
	for (int i = 0; i < n; i++) {
		for (int j = 0; j < 8; j++) {
			scanf("%d", &s[j]);
		}
		int inputh = hashCode(s);
		if (d[inputh] != -1) {
			output[i] = d[inputh];
			continue;
		}
		while (head < tail) {
			label l = candidate[head++];
			label temp1(Op1(l.V), l.visited + 1);
			if (d[temp1.hash] == -1) {
				candidate[tail++] = temp1;
				d[temp1.hash] = temp1.visited;
			}
			label temp2(Op2(l.V), l.visited + 1);
			if (d[temp2.hash] == -1) {
				candidate[tail++] = temp2;
				d[temp2.hash] = temp2.visited;
			}
			label temp3(Op3(l.V), l.visited + 1);
			if (d[temp3.hash] == -1) {
				candidate[tail++] = temp3;
				d[temp3.hash] = temp3.visited;
			}
			if (d[inputh] != -1) {
				output[i] = d[inputh];
				break;
			}
		}
	}
	for (int i = 0; i < n; i++) {
		printf("%d\n", output[i]);
	}
	delete[] output;
	return 0;
}