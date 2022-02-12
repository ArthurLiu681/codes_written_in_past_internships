#include <iostream>
using namespace std;
#include <string.h>
#define DEFAULT_CAPACITY  3
#define Rank int
#define InHeap(n, i) (-1<(i) &&(i)<n)
#define LChild(i) (((i)<<1)+1)
#define RChild(i) (((i)+1)<<1)
#define Parent(i) (((i)-1)>>1)
#define ParentValid(i) (0<i)
#define LChildValid(n, i) (InHeap(n, LChild(i)))
#define RChildValid(n, i) (InHeap(n, RChild(i)))
#define Bigger(PQ, i, j) (PQ[i]<PQ[j]?j:i)
#define ProperParent(PQ, n, i) (LChildValid(n, i)?(RChildValid(n, i)?Bigger(PQ, i, Bigger(PQ, LChild(i), RChild(i))):Bigger(PQ, i, LChild(i))):i)

struct task {
	long long p;
	char name[10]; // Although the maximum length of the name is 8 characters, declaring name as char name[8] is not correct since there is a '\0' at the end of the string. 
	bool operator<(task& t) { return ((p > t.p) || ((p == t.p) && (strcmp(name, t.name) > 0))); }
};

template <typename T> void percolateDown(T* A, int n, int i) {
	Rank j;
	while (i != (j = ProperParent(A, n, i))) {
		swap(A[i], A[j]);
		i = j;
	}
}

template <typename T> void heapify(T* A, int lo, int hi) {
	A = A + lo;
	int n = hi - lo;
	for (int i = (n - 2) >> 1; i >= 0; i--) {
		percolateDown(A, n, i);
	}
}

int main() {
	int n, m;
	scanf("%d %d", &n, &m);
	task* pq = new task[n];
	for (int i = 0; i < n; i++) {
		scanf("%lld %s", &pq[i].p, pq[i].name); // Using "%lld" instead of "%I64d" accelerates the program a lot, making four test sets which originally exceeded time limit accepted.
	}
	int size = n;
	heapify(pq, 0, size);
	for (int i = 0; size && (i < m); i++) {
		// if(size==0) break;
		// Using "size&&(i<m)" instead of "if(size==0) break;" accelerates the program a lot, making four test sets which originally exceeded time limit accepted.
		printf("%s\n", pq[0].name);
		pq[0].p *= 2;
		if (pq[0].p >= 4294967296) {
			pq[0] = pq[--size];
		}
		percolateDown(pq, size, 0);
	}
	return 0;
}
