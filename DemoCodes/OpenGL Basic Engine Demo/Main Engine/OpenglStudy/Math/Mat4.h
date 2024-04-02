#pragma once
#define M_PI       3.14159265358979323846   // pi
#include "Vec3.h"

inline float toRadians(float degrees)
{
	return degrees * ((float)M_PI / 180.f);
}

struct Mat4
{
	float m[4 * 4];

	Mat4(float diagonal=1.0f);

	Mat4 Identity();

	Mat4 GetInverse();
	Mat4 GetTranspose();

	Mat4& multiply(const Mat4& m);

	void Translate(float x_, float y_, float z_);
	void Translate(const Vec3& rhs);

	void Scale(float x_, float y_, float z_);
	void Scale(const Vec3& scale);
	void Scale(float scale_);

	void RotateZ(float angle);
	void RotateX(float angle);
	void RotateY(float angle);
	void Rotate(float angle, const Vec3& axis); //option

	Mat4 operator*(const Mat4 m) const;

	Mat4& operator*=(const Mat4& m);
	bool operator==(const Mat4& mat) const;

	/****************** static matrix *************/
	static Mat4 identity();
	static Mat4 inverse(const Mat4 m);

	static Mat4 translate(const Vec3& translation);
	static Mat4 rotation(float angle, const Vec3& axis); //option
	static Mat4 rotationX(float angle);
	static Mat4 rotationY(float angle);
	static Mat4 rotationZ(float angle);
	static Mat4 scale(const Vec3& scale);


	static Mat4 orthographic(float left, float right, float bottom, float top, float near, float far); //Camera graphics
	static Mat4 perspective(float fov, float aspectRatio, float near, float far);

	// Custom methods
	Vec3 position() const;
};