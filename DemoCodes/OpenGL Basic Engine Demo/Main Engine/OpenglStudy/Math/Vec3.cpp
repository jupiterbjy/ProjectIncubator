#include "vec3.h"

#include <math.h>
#include <algorithm>


Vec3::Vec3() :x(0.0f), y(0.0f), z(0.0f)
{
}
Vec3::Vec3(float xV, float yV, float zV) : x(xV), y(yV), z(zV)
{
}


float Vec3::DotProduct(const Vec3& v) const
{
	return x * v.x + y * v.y + z * v.z;
}

Vec3 Vec3::CrossProduct(const Vec3& v) const
{
	return Vec3(
		y * v.z - z * v.y,
		z * v.x - x * v.z,
		x * v.y - y * v.x
	);
}


float Vec3::Length() const
{
	return sqrt(x * x + y * y + z * z);
}

float Vec3::DistanceSq(const Vec3& v) const
{
	return (
		pow(x - v.x, 2) +
		pow(y - v.y, 2) +
		pow(z - v.z, 2)
	);
}
float Vec3::Distance(const Vec3& v) const
{
	return sqrt(DistanceSq(v));
}

Vec3& Vec3::Normalize()
{
	if (Length() == 0.0f)
		return *this;

	*this /= Length();
	return *this;
}


/************************* operator ***********************/
Vec3 Vec3::operator+(const Vec3& v) const
{
	return Vec3(x + v.x, y + v.y, z + v.z);
}
Vec3 Vec3::operator-(const Vec3& v) const
{
	return Vec3(x - v.x, y - v.y, z - v.z);
}
Vec3& Vec3::operator+=(const Vec3& v)
{
	x += v.x;
	y += v.y;
	z += v.z;

	return *this;
}
Vec3& Vec3::operator-=(const Vec3& v)
{
	x -= v.x;
	y -= v.y;
	z -= v.z;

	return *this;
}


Vec3 Vec3::operator*(float s) const
{
	return Vec3(x * s, y * s, z * s);
}
Vec3& Vec3::operator*=(float s)
{
	x *= s;
	y *= s;
	z *= s;

	return *this;
}

Vec3 Vec3::operator/(float s) const
{
	return Vec3(x / s, y / s, z / s);
}
Vec3& Vec3::operator/=(float s)
{
	x /= s;
	y /= s;
	z /= s;

	return *this;
}
Vec3 Vec3::operator-()const
{
	return Vec3(-x, -y, -z);
}

bool Vec3::operator==(const Vec3& v) const
{
	return x == v.x && y == v.y && z == v.z;
}
bool Vec3::operator!=(const Vec3& v) const
{
	return !operator==(v);
}

Vec3 Vec3::cross(const Vec3& v1, const Vec3& v2)
{
	return {
		v1.y * v2.z - v1.z * v2.y,
		v1.z * v2.x - v1.x * v2.z,
		v1.x * v2.y - v1.y * v2.x
	};
}

float Vec3::dot(const Vec3& v1, const Vec3& v2)
{
	return 0.0f;
}

Vec3 Vec3::normalize(const Vec3& v)
{
	if (v.Length() == 0.0f)
		return v;

	// TODO: check number of constructor calls
	return Vec3(v.x, v.y, v.z).Normalize();
}

Vec3 Vec3::Normalized() const
{
	return Vec3::normalize(*this);
}
