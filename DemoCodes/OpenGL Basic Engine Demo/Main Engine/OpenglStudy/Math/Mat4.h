#pragma once
#define M_PI       3.14159265358979323846   // pi

#include <initializer_list>
#include "Vec3.h"

inline float toRadians(float degrees)
{
	return degrees * ((float)M_PI / 180.f);
}


namespace hin_hardcoded {
	static const float identity[4 * 4] = {
		1, 0, 0, 0,
		0, 1, 0, 0,
		0, 0, 1, 0,
		0, 0, 0, 1
	};

	static const float zero[4 * 4] = {
		0, 0, 0, 0,
		0, 0, 0, 0,
		0, 0, 0, 0,
		0, 0, 0, 0
	};
}


struct Mat4
{
	float m[4 * 4];

	// --- Constructors ---

	// Creates matrix without initialized values.
	// Currently deleted to explicitly find linter error
	Mat4() = delete;

	// Array constructor
	Mat4(const float* values);

	// Copy constructor
	Mat4(const Mat4& other);

	// Initializer list constructor
	Mat4(std::initializer_list<float> values);

	// Named constructor for Identity matrix.
	// Should be theorically faster as this use memcpy.
	// This is return-value-optimized.
	static Mat4 Identity() noexcept;

	// Named constructor for scaled Identity matrix
	// This is return-value-optimized.
	static Mat4 Identity(float scale) noexcept;

	// Named constructor for zero matrix
	static Mat4 Zero();

	// Move constructor
	// Mat4(Mat4&& other) noexcept;

	// --- In-Place Methods ---

	// Inplace Inverse
	void inverse();

	// Inplace Transpose
	void transpose();

	// Inplace Multiply. Alias of `*this = make_multiply()`
	void multiply(const Mat4& m);

	// Inplace Translation
	void translate(float x_, float y_, float z_);

	// Inplace Translation
	void translate(const Vec3& other);

	// Inplace Scale
	void scale(float x_, float y_, float z_);

	// Inplace Scale
	void scale(const Vec3& scale);

	// Inplace Rotation
	void scale(float scale_);

	// Inplace Rotation
	void rotate(float radians, const Vec3& axis);

	// Inplace Rotation for X
	void rotate_x(float radians);

	// Inplace Rotation for Y
	void rotate_y(float radians);

	// Inplace Rotation for Z
	void rotate_z(float radians);


	// --- Operators ---
	
	// alias for `make_multiplied`
	Mat4 operator*(const Mat4 other) const;

	// alias for `multiply; return *this`
	Mat4& operator*=(const Mat4& other);

	// Check each 
	bool operator==(const Mat4& other) const;


	// --- Static Methods ---

	
	// Creates new inversed matrix
	static Mat4 make_inversed(const Mat4 other);

	// Creates new transposed matrix
	static Mat4 make_transposed(const Mat4& other);

	// Creates new multiplied matrix
	static Mat4 make_multiplied(const Mat4& a, const Mat4& b);

	// Creates new translated matrix
	static Mat4 make_translated(const Vec3& translation);

	// Creates new rotation matrix
	static Mat4 make_rotation(float angle, const Vec3& axis);

	// Creates new rotation matrix for X axis
	static Mat4 make_rotation_x(float angle);

	// Creates new rotation matrix for Y axis
	static Mat4 make_rotation_y(float angle);

	// Creates new rotation matrix for Z axis
	static Mat4 make_rotation_z(float angle);

	// Creates new scale matrix
	static Mat4 make_scale(const Vec3& scale);

	// Creates new orthographic matrix
	static Mat4 orthographic(float left, float right, float bottom, float top, float near, float far); //Camera graphics

	// Creates new perspective matrix
	static Mat4 perspective(float fov, float aspectRatio, float near, float far);

};


//struct Mat4RowProxy {
//	Mat4& mat;
//	int row;
//
//	Mat4RowProxy(Mat4 & mat, int row)
//		: mat(mat), row(row)
//	{}
//
//	//operator float() const;
//	//Mat4ColProxy operator[](int row) const;
//	Mat4ColProxy operator[](int col);
//};
//
//
//struct Mat4ColProxy {
//	Mat4& mat;
//	int idx;
//
//	Mat4ColProxy(Mat4RowProxy proxy, int col)
//		: mat(proxy.mat), idx(proxy.row + col * 4)
//	{}
//
//	operator float() const
//	{
//		return mat.m[idx];
//	}
//
//	float& operator[](int col) const
//	{
//		return mat.m[idx];
//	}
//
//	void operator=(float val)
//	{
//		mat.m[idx] = val;
//	}
//
//};
