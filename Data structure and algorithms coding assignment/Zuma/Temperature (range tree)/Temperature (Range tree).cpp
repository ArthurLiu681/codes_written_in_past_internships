// In a two dimensional range tree, points with the same x coordinate is put into a single xNode class. 
// The left child of an xnode does not contain points with x coordinate euqal to the x value of the xnode. 
// Neither does the node's right child, so points with x coordinate equal to x value of the xnode has to be checked first
// before dig into the node's left child and right child.

#include <iostream>
#include "temperature.h"
using namespace std;

#define Rank int
#define DEFAULT_CAPACITY  3

template <typename T> class Vector {
protected:
	Rank _size; int _capacity;  T* _elem;
	void copyFrom(T const* A, Rank lo, Rank hi);
	void expand();
public:
	Vector(int c = DEFAULT_CAPACITY) {
		_elem = new T[_capacity = c];
		_size = 0;
	}
	Vector(Vector<T> const& V) { copyFrom(V._elem, 0, V._size); }
	Vector(T const* A, Rank n) { copyFrom(A, 0, n); }
	~Vector() { delete[] _elem; }
	Rank size() const { return _size; }
	bool empty() const { return !_size; }
	T& operator[] (Rank r);
	Vector<T>& operator= (Vector<T> const&);
	Rank insertAtlast(const T& e);
	Rank insert(const T& e);
	void merge(Rank lo, Rank mi, Rank hi);
	void mergeSort(Rank lo, Rank hi);
};

template <typename T> void Vector<T>::expand() {
	if (_size < _capacity) return;
	if (_capacity < DEFAULT_CAPACITY) _capacity = DEFAULT_CAPACITY;
	T* oldElem = _elem;  _elem = new T[_capacity <<= 1];
	for (int i = 0; i < _size; i++)
		_elem[i] = oldElem[i];
	delete[] oldElem;
}

template <typename T> void Vector<T>::copyFrom(T const* A, Rank lo, Rank hi) {
	_elem = new T[_capacity = 2 * (hi - lo)];
	for (_size = 0; lo < hi; _size++, lo++)
		_elem[_size] = A[lo];
}

template <typename T> T& Vector<T>::operator[] (Rank r)
{
	return _elem[r];
}

template <typename T> Vector<T>& Vector<T>::operator= (Vector<T> const& V) {
	if (_elem) delete[] _elem;
	copyFrom(V._elem, 0, V.size());
	return *this;
}
template < typename T> void Vector<T>::merge(Rank lo, Rank mi, Rank hi) {
	T* A = _elem + lo;
	int lb = mi - lo; T* B = new T[lb];
	for (Rank i = 0; i < lb; i++) {
		B[i] = A[i];
	}
	int lc = hi - mi; T* C = _elem + mi;
	for (Rank i = 0, j = 0, k = 0; j < lb; ) {
		if (!(k < lc) || (!(C[k] < B[j]))) A[i++] = B[j++];
		else A[i++] = C[k++];
	}
	delete[] B;
}

template < typename T> void Vector<T>::mergeSort(Rank lo, Rank hi) {
	if (hi - lo < 2) return;
	int mi = (lo + hi) / 2;
	mergeSort(lo, mi); mergeSort(mi, hi);
	merge(lo, mi, hi);
}

struct station {
public:
	int x; int y; int temp;
	station(int x = 0, int y = 0, int temp = 0) :x(x), y(y), temp(temp) {}
	int coordinate(int hv) { return hv ? y : x; }
	bool operator < (const station& s) { return y < s.y; }
	bool operator > (const station& s) { return y > s.y; }
	bool operator == (const station& s) { return y == s.y; }
};

struct xNode {
public:
	int x; int p; Vector<station> v; Vector<station> subv; xNode* lc; xNode* rc;
	xNode(int x = 0, int p = 0, xNode* lc = NULL, xNode* rc = NULL) :x(x), p(0), v(), subv(), lc(lc), rc(rc) {}
	bool operator==(const xNode& s) { return x == s.x; }
	bool operator<(const xNode& s) { return x < s.x; }
	bool operator>(const xNode& s) { return x > s.x; }
	bool operator==(int i) { return x == i; }
	bool operator<(int i) { return x < i; }
	bool operator>(int i) { return x > i; }
};

long long temperature;
int number;
Vector<xNode> V;
int xl, yl, xh, yh;

template <typename T, typename K> Rank binSearch(Vector<T>& V, K const& e) {
	Rank lo = 0; Rank hi = V.size();
	while (lo < hi) {
		Rank mi = (lo + hi) >> 1;
		(V[mi] > e) ? hi = mi : lo = mi + 1;
	}
	return --lo;
}

template <typename T> Rank Vector<T>::insertAtlast(T const& e) {
	expand();
	_elem[_size] = e; _size++;
	return (_size - 1);
}

template <typename T> Rank Vector<T>::insert(T const& e) {
	Rank r = binSearch(*this, e);
	if ((r != -1) && (_elem[r] == e)) return r;
	expand();
	_elem[_size] = e; _size++;
	return (_size - 1);
}

void merge(Vector<station>& v1, Vector<station>& v2) {
	Vector<station> v;
	int s1 = v1.size(); int s2 = v2.size();
	for (Rank j = 0, k = 0; (j < s1) || (k < s2); ) {
		if ((j < s1) && (!(k < s2) || (v1[j].y <= v2[k].y))) {
			v.insertAtlast(v1[j]);
			j++;
		}
		if ((k < s2) && (!(j < s1) || (v2[k].y < v1[j].y))) {
			v.insertAtlast(v2[k]);
			k++;
		}
	}
	v1 = v;
}

Rank binSearchSmallestGreater(Vector<station>& v, const int& x, int hv) {
	Rank lo = 0; Rank hi = v.size();
	while (lo < hi) {
		Rank mi = (lo + hi) >> 1;
		(x < v[mi].coordinate(hv)) ? hi = mi : lo = mi + 1;
	}
	return lo;
}

Rank binSearchSmallestNotSmaller(Vector<station>& v, const int& x, int hv) {
	Rank lo = 0; Rank hi = v.size();
	while (lo < hi) {
		Rank mi = (lo + hi) >> 1;
		(x <= v[mi].coordinate(hv)) ? hi = mi : lo = mi + 1;
	}
	return lo;
}

//The createTree1 function, which combines createTree and buildTree into a single recursive function will cause 
//run time error, perhaps because too many recursive layers cause stack overflow.

//void createTree1(xNode*& root, int lo, int hi) {
//	if (hi - lo < 2) {
//		root = &V[lo];
//		root->v.mergeSort(0, root->v.size());
//		root->subv = root->v;
//		return;
//	}
//	int mi = (lo + hi) >> 1;
//	root = &V[mi];
//	root->v.mergeSort(0, root->v.size());
//	root->subv = root->v;
//	if (lo < mi) {
//		createTree(root->lc, lo, mi);
//		merge(root->subv, root->lc->subv);
//	}
//	if (mi + 1 < hi) {
//		createTree(root->rc, mi + 1, hi);
//		merge(root->subv, root->rc->subv);
//	}
//}

void createTree(xNode*& root, int lo, int hi) {
	if (hi - lo < 2) {
		root = &V[lo];
		root->p = lo;
		return;
	}
	int mi = (lo + hi) >> 1;
	root = &V[mi];
	root->p = mi;
	if (lo < mi) {
		createTree(root->lc, lo, mi);
	}
	if (mi + 1 < hi) {
		createTree(root->rc, mi + 1, hi);
	}
}

void build(xNode* root) {
	if (!root) return;

	build(root->lc);
	build(root->rc);

	root->v.mergeSort(0, root->v.size());
	root->subv = root->v;

	if (root->lc) {
		merge(root->subv, root->lc->subv);
	}
	if (root->rc) {
		merge(root->subv, root->rc->subv);
	}
}

void cumulate(xNode* root) {
	if (!root) return;
	for (int i = 1; i < root->subv.size(); i++) {
		root->subv[i].temp += root->subv[i - 1].temp;
	}
	for (int i = 1; i < root->v.size(); i++) {
		root->v[i].temp += root->v[i - 1].temp;
	}
	cumulate(root->lc);
	cumulate(root->rc);
}

void traverse(Vector<station>& subv) {
	Rank r1 = binSearchSmallestNotSmaller(subv, yl, 1) - 1;
	Rank r2 = binSearchSmallestGreater(subv, yh, 1) - 1;
	if (r2 < 0) return;
	number += (r2 - r1);
	temperature += ((long long)subv[r2].temp - (long long)((r1 == -1 ? 0 : subv[r1].temp)));
}

void rangeEnquiry(int x_min, int x_max, xNode* root) {
	if (!root) return;
	if ((xl <= x_min) && (x_max <= xh)) {
		traverse(root->subv);
		return;
	}
	if ((x_max < xl) || (xh < x_min)) return;
	if ((xl <= root->x) && (root->x <= xh)) {
		traverse(root->v);
	}
	rangeEnquiry(x_min, V[root->p - 1].x, root->lc);
	rangeEnquiry(V[root->p + 1].x, x_max, root->rc);
}

int main() {
	int n = GetNumOfStation();
	for (int i = 0; i < n; i++) {
		int x; int y; int temp;
		GetStationInfo(i, &x, &y, &temp);
		Rank r = V.insert(xNode(x));
		V[r].v.insertAtlast(station(x, y, temp));
	}
	V.mergeSort(0, V.size());
	for (int i = 0; i < V.size(); i++) {
		V[i].v.mergeSort(0, V[i].v.size());
	}
	xNode* root = NULL;
	createTree(root, 0, V.size());
	build(root);
	cumulate(root);
	while (GetQuery(&xl, &yl, &xh, &yh)) {
		temperature = 0;
		number = 0;
		rangeEnquiry(V[0].x, V[V.size() - 1].x, root);
		Response(number ? (temperature / number) : 0);
	}
	return 0;
}