#include "cmake_dll_demo.hpp"

int add(int a, int b)
{
	return a + b;
}

int sub(int a, int b)
{
	return a - b;
}

int mul(int a, int b)
{
	return a * b;
}

float div(int a, int b)
{
	return float(a) / float(b);
}
