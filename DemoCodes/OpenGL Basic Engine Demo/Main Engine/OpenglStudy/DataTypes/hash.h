#pragma once

#include <string>

const size_t FIXED_SEED = std::hash<std::string>{}(
    "Yumewa kimiga hitori ehgakunzanaku miehnai kazega todokettekureru"
);


// From boost
// https://stackoverflow.com/q/5889238/10909029
template <class T>
inline void hash_combine(std::size_t& seed, const T& v)
{
    std::hash<T> hasher;
    seed ^= hasher(v) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
};



template <class T>
inline size_t hash_1d_array(const T arr[], const size_t size) {
    size_t seed = FIXED_SEED;

	for (size_t i = 0; i < size; i++)
		hash_combine(seed, arr[i]);

	return seed;
}