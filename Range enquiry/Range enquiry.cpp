// "Scanf" and "printf" are faster than "cin" and "cout".
//
// Use "int* S = new int[x]" to allocate memory for an array whose size is denoted by a 
// variable whose value is to be determined by input is faster than allocate the largest 
// memory the array can take.

#include<iostream>
#include<cstdio>
using namespace std;
#define Rank int

Rank binarySearch(int* S, int lo, int hi, int e) {
    while (lo < hi) {
        Rank mi = (lo + hi) >> 1;
        if (S[mi] < e) lo = mi + 1;
        else hi = mi;
    }
    return --lo;
}

void merge(int* S, Rank l, Rank m, Rank h) {
    int* A = S + l;
    int lb = m - l; int* B = new int[lb];
    for (int i = 0; i < lb; i++) B[i] = A[i];
    int lc = h - m; int* C = S + m;
    for (int i = 0, j = 0, k = 0; j < lb;) {
        if ((k < lc) && (B[j] > C[k])) {
            A[i++] = C[k++];
        }
        else {
            A[i++] = B[j++];
        }
    }
    delete[] B;
}

void mergeSort(int* S, int n) {
    if (n < 2) return;
    int m = n >> 1;
    mergeSort(S, m); mergeSort(S + m, n - m);
    merge(S, 0, m, n);
}

int main() {
    int n, m;
    scanf("%d%d", &n, &m);
    int* S = new int[n];
    for (int i = 0; i < n; i++) {
        scanf("%d", &S[i]);
    }
    mergeSort(S, n);
    int a, b;
    while (0 < m--) {
        scanf("%d%d", &a, &b);
        int l = binarySearch(S, 0, n, a);
        int st = 0 < l ? l : 0;
        int h = binarySearch(S, st, n, b + 1);
        printf("%d \n", h - l);
    }
    delete[] S;
    return 0;
}

