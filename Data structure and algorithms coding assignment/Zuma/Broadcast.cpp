#define _CRT_SECURE_NO_WARNINGS
#include <string.h>
#include <iostream>
using namespace std;

#define Rank int
#define DEFAULT_CAPACITY  3

template <typename T> class Vector {
protected:
	Rank _size; int _capacity;  T* _elem;
	void expand();
	void copyFrom(T const* A, Rank lo, Rank hi);
public:
	Vector(int c = DEFAULT_CAPACITY, int s = 0, T v = 0)
	{
		_elem = new T[_capacity = c];
		for (_size = 0; _size < s; _elem[_size++] = v);
	}
	Vector(Vector<T> const& V) { copyFrom(V._elem, 0, V._size); } //This function is necessary. Otherwise, the parameter "v" in the default constructor above will create a temporary variable, which shallowly copies Vector<int>(3,0,0) and cause problems at destruction. 
	~Vector() { delete[] _elem; }
	Rank size() const { return _size; }
	bool empty() const { return !_size; }
	T& operator[] (Rank r);
	Vector<T>& operator= (Vector<T> const&);
	Rank insert(Rank r, T const& e);
	Rank insert(T const& e) { return insert(_size, e); }
	T remove(Rank r);
	int remove(Rank lo, Rank hi);
};

template < typename T> void Vector<T>::copyFrom(T const* A, Rank lo, Rank hi) {
	_elem = new T[_capacity = 2 * (hi - lo)]; _size = 0;
	while (lo < hi)
		_elem[_size++] = A[lo++];
}

template <typename T> void Vector<T>::expand() {
	if (_size < _capacity) return;
	if (_capacity < DEFAULT_CAPACITY) _capacity = DEFAULT_CAPACITY;
	T* oldElem = _elem;  _elem = new T[_capacity <<= 1];
	for (int i = 0; i < _size; i++)
		_elem[i] = oldElem[i];
	delete[] oldElem;
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

template <typename T> Rank Vector<T>::insert(Rank r, T const& e) {
	expand();
	for (int i = _size; i > r; i--) _elem[i] = _elem[i - 1];
	_elem[r] = e; _size++;
	return r;
}

template <typename T> T Vector<T>::remove(Rank r) {
	T e = _elem[r];
	remove(r, r + 1);
	return e;
}

template <typename T> int Vector<T>::remove(Rank lo, Rank hi) {
	if (lo == hi) return 0;
	while (hi < _size) _elem[lo++] = _elem[hi++];
	_size = lo;
	return hi - lo;
}

int main(){
	int n, m;
	scanf("%d %d", &n, &m);
	Vector<int> c(n, n, -1);
	Vector<Vector<int>> v(n, n, Vector<int>(3, 0, 0)); //This line will construct a variable "Vector<int>(3, 0, 0)", which will be assigned to the n vectors of v by operator "=", so the overriding function of operator "=" is necessary.
	for (int i = 0; i < m; i++) {
		int l, r;
		scanf("%d %d", &l, &r);
		v[l - 1].insert(r - 1);
		v[r - 1].insert(l - 1);
	}
	int i = 0;
	do
		if (c[i] == -1) {
			c[i] = 0;
			Vector<int> Q;
			Q.insert(i);
			while (!Q.empty()) {
				i = Q.remove(0);
				int cc = 1 - c[i];
				for (int j = 0; j < v[i].size(); j++) {
					int k = v[i][j];
					if (c[k] == -1) {
						Q.insert(k); c[k] = cc;
					}
					else if (c[k] != cc){
						cout << "-1" << endl;
						return 0;
					}
				}
 			}
		}
	while ((++i) != n);
	cout << "1" << endl;
	return 0;
}