#pragma once
#include <cmath>

struct Vec3
{
	float x, y, z;

	Vec3();
	Vec3(float x, float y, float z);

	float DotProduct(const Vec3& v) const;
	Vec3 CrossProduct(const Vec3& v) const;

	float Length() const;

	float DistanceSq(const Vec3& v) const;
	float Distance(const Vec3& v) const;

	Vec3& Normalize();

	/****************** operator ******************/
	Vec3 operator+(const Vec3& v) const;
	Vec3 operator-(const Vec3& v) const;
	Vec3& operator+=(const Vec3& v);
	Vec3& operator-=(const Vec3& v);

	Vec3 operator*(float s) const;
	Vec3& operator*=(float s);

	Vec3 operator/(float s) const;
	Vec3& operator/=(float s);

	Vec3 operator-()const;

	bool operator==(const Vec3& v) const;
	bool operator!=(const Vec3& v) const;

	// --- Custom ---
	
	// Rule of five;
	// https://en.wikipedia.org/wiki/Rule_of_three_%28C++_programming%29#Rule_of_five

	static Vec3 cross(const Vec3& v1, const Vec3& v2);
	static float dot(const Vec3& v1, const Vec3& v2);
	static Vec3 normalize(const Vec3& v);

	Vec3 Normalized() const;
};

