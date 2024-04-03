#include "mat4.h"
#include <utility>
#include <string.h>

// row-column access to 1d array
#define MAT(r, c) m[r + c * 4]


Mat4::Mat4(const float* values)
{
	memcpy(m, values, 4 * 4 * sizeof(float));
}


Mat4::Mat4(const Mat4& other)
{
	memcpy(m, other.m, 4 * 4 * sizeof(float));
}

Mat4::Mat4(std::initializer_list<float> values)
{
	memcpy(m, values.begin(), 4 * 4 * sizeof(float));
}

Mat4 Mat4::Identity() noexcept
{
	return { hin_hardcoded::identity };
}

Mat4 Mat4::Identity(float scale) noexcept
{
	return {
		scale, 0, 0, 0,
		0, scale, 0, 0,
		0, 0, scale, 0,
		0, 0, 0, scale
	};
}

Mat4 Mat4::Zero()
{
	return { hin_hardcoded::zero };
}


void Mat4::inverse()
{
	// TODO: implement this 
	*this = make_inversed(*this);
}

void Mat4::transpose()
{
	auto tmp = m[0];

	for (size_t r = 0; r < 4; r++)
		for (size_t c = 0; c < 4; c++) {
			tmp = MAT(r, c);
			MAT(r, c) = MAT(c, r);
			MAT(c, r) = tmp;
		}
}


void Mat4::multiply(const Mat4& other)
{
	*this = make_multiplied(*this, other);
}

void Mat4::translate(float x_, float y_, float z_)
{
	MAT(0, 3) += x_;
	MAT(1, 3) += y_;
	MAT(2, 3) += z_;
}

void Mat4::translate(const Vec3& other)
{
	MAT(0, 3) += other.x;
	MAT(1, 3) += other.y;
	MAT(2, 3) += other.z;
}

void Mat4::scale(float x_, float y_, float z_)
{
	MAT(0, 0) *= x_;
	MAT(1, 1) *= y_;
	MAT(2, 2) *= z_;
}

void Mat4::scale(const Vec3& scale_vec)
{
	MAT(0, 0) *= scale_vec.x;
	MAT(1, 1) *= scale_vec.y;
	MAT(2, 2) *= scale_vec.z;
}

void Mat4::scale(float scale_)
{
	MAT(0, 0) *= scale_;
	MAT(1, 1) *= scale_;
	MAT(2, 2) *= scale_;
}

//void Mat4::RotateZ(float radians)
//{
//	float c = cos(radians);
//	float s = sin(radians);
//
//	Mat4 rotationMatrix(1.0f);
//
//	rotationMatrix.MAT(0, 0) = c;
//	rotationMatrix.MAT(1, 0) = -s;
//	rotationMatrix.MAT(0, 1) = s;
//	rotationMatrix.MAT(1, 1) = c;
//	
//	// TODO: check if this deepcopies array
//	multiply(rotationMatrix);
//}
//
//void Mat4::RotateX(float radians)
//{
//	float c = cos(radians);
//	float s = sin(radians);
//
//	Mat4 rotationMatrix(1.0f);
//	rotationMatrix.m[1 + 1 * 4] = c;
//	rotationMatrix.m[2 + 1 * 4] = -s;
//	rotationMatrix.m[1 + 2 * 4] = s;
//	rotationMatrix.m[2 + 2 * 4] = c;
//
//	multiply(rotationMatrix);
//}
//
//void Mat4::RotateY(float radians)
//{
//	float c = cos(radians);
//	float s = sin(radians);
//
//	Mat4 rotationMatrix(1.0f);
//	rotationMatrix.m[0 + 0 * 4] = c;
//	rotationMatrix.m[2 + 0 * 4] = s;
//	rotationMatrix.m[0 + 2 * 4] = -s;
//	rotationMatrix.m[2 + 2 * 4] = c;
//
//	multiply(rotationMatrix);
//}

void Mat4::rotate(float radians, const Vec3& axis)
{
	*this *= make_rotation(radians, axis);
}

void Mat4::rotate_x(float radians)
{
	rotate(radians, Vec3(1, 0, 0));
}

void Mat4::rotate_y(float radians)
{
	rotate(radians, Vec3(0, 1, 0));
}

void Mat4::rotate_z(float radians)
{
	rotate(radians, Vec3(0, 0, 1));
}

Mat4 Mat4::operator*(const Mat4 other) const
{
	return make_multiplied(*this, other);
}

Mat4& Mat4::operator*=(const Mat4& other)
{
	multiply(other);
	return *this;
}

bool Mat4::operator==(const Mat4& other) const
{
	// wish to use memcmp but due to possible padding bits I'm not gonna do that

	for (int i = 0; i < 4 * 4; i++)
		if (m[i] != other.m[i])
			return false;

	return true;
}


Mat4 Mat4::make_inversed(const Mat4 mat)
{
	// https://graphics.stanford.edu/courses/cs248-98-fall/Final/q4.html
	// This much simpler one exists; but this won't work for perspective matrix
	// As it's not affline matrix; nor that we can remember the processing steps
	// done to Affline matrix

	// below ref: https://stackoverflow.com/a/44446912/10909029

	auto A2323 = mat.MAT(2, 2) * mat.MAT(3, 3) - mat.MAT(2, 3) * mat.MAT(3, 2);
	auto A1323 = mat.MAT(2, 1) * mat.MAT(3, 3) - mat.MAT(2, 3) * mat.MAT(3, 1);
	auto A1223 = mat.MAT(2, 1) * mat.MAT(3, 2) - mat.MAT(2, 2) * mat.MAT(3, 1);
	auto A0323 = mat.MAT(2, 0) * mat.MAT(3, 3) - mat.MAT(2, 3) * mat.MAT(3, 0);
	auto A0223 = mat.MAT(2, 0) * mat.MAT(3, 2) - mat.MAT(2, 2) * mat.MAT(3, 0);
	auto A0123 = mat.MAT(2, 0) * mat.MAT(3, 1) - mat.MAT(2, 1) * mat.MAT(3, 0);
	auto A2313 = mat.MAT(1, 2) * mat.MAT(3, 3) - mat.MAT(1, 3) * mat.MAT(3, 2);
	auto A1313 = mat.MAT(1, 1) * mat.MAT(3, 3) - mat.MAT(1, 3) * mat.MAT(3, 1);
	auto A1213 = mat.MAT(1, 1) * mat.MAT(3, 2) - mat.MAT(1, 2) * mat.MAT(3, 1);
	auto A2312 = mat.MAT(1, 2) * mat.MAT(2, 3) - mat.MAT(1, 3) * mat.MAT(2, 2);
	auto A1312 = mat.MAT(1, 1) * mat.MAT(2, 3) - mat.MAT(1, 3) * mat.MAT(2, 1);
	auto A1212 = mat.MAT(1, 1) * mat.MAT(2, 2) - mat.MAT(1, 2) * mat.MAT(2, 1);
	auto A0313 = mat.MAT(1, 0) * mat.MAT(3, 3) - mat.MAT(1, 3) * mat.MAT(3, 0);
	auto A0213 = mat.MAT(1, 0) * mat.MAT(3, 2) - mat.MAT(1, 2) * mat.MAT(3, 0);
	auto A0312 = mat.MAT(1, 0) * mat.MAT(2, 3) - mat.MAT(1, 3) * mat.MAT(2, 0);
	auto A0212 = mat.MAT(1, 0) * mat.MAT(2, 2) - mat.MAT(1, 2) * mat.MAT(2, 0);
	auto A0113 = mat.MAT(1, 0) * mat.MAT(3, 1) - mat.MAT(1, 1) * mat.MAT(3, 0);
	auto A0112 = mat.MAT(1, 0) * mat.MAT(2, 1) - mat.MAT(1, 1) * mat.MAT(2, 0);

	auto det =
		  mat.MAT(0, 0) * (mat.MAT(1, 1) * A2323 - mat.MAT(1, 2) * A1323 + mat.MAT(1, 3) * A1223)
		- mat.MAT(0, 1) * (mat.MAT(1, 0) * A2323 - mat.MAT(1, 2) * A0323 + mat.MAT(1, 3) * A0223)
		+ mat.MAT(0, 2) * (mat.MAT(1, 0) * A1323 - mat.MAT(1, 1) * A0323 + mat.MAT(1, 3) * A0123)
		- mat.MAT(0, 3) * (mat.MAT(1, 0) * A1223 - mat.MAT(1, 1) * A0223 + mat.MAT(1, 2) * A0123);
	det = 1 / det;

	return {
		det *  (mat.MAT(1, 1) * A2323 - mat.MAT(1, 2) * A1323 + mat.MAT(1, 3) * A1223),	// m00
		det * -(mat.MAT(0, 1) * A2323 - mat.MAT(0, 2) * A1323 + mat.MAT(0, 3) * A1223),	// m01
		det *  (mat.MAT(0, 1) * A2313 - mat.MAT(0, 2) * A1313 + mat.MAT(0, 3) * A1213),	// m02
		det * -(mat.MAT(0, 1) * A2312 - mat.MAT(0, 2) * A1312 + mat.MAT(0, 3) * A1212),	// m03
		det * -(mat.MAT(1, 0) * A2323 - mat.MAT(1, 2) * A0323 + mat.MAT(1, 3) * A0223),	// m10
		det *  (mat.MAT(0, 0) * A2323 - mat.MAT(0, 2) * A0323 + mat.MAT(0, 3) * A0223),	// m11
		det * -(mat.MAT(0, 0) * A2313 - mat.MAT(0, 2) * A0313 + mat.MAT(0, 3) * A0213),	// m12
		det *  (mat.MAT(0, 0) * A2312 - mat.MAT(0, 2) * A0312 + mat.MAT(0, 3) * A0212),	// m13
		det *  (mat.MAT(1, 0) * A1323 - mat.MAT(1, 1) * A0323 + mat.MAT(1, 3) * A0123),	// m20
		det * -(mat.MAT(0, 0) * A1323 - mat.MAT(0, 1) * A0323 + mat.MAT(0, 3) * A0123),	// m21
		det *  (mat.MAT(0, 0) * A1313 - mat.MAT(0, 1) * A0313 + mat.MAT(0, 3) * A0113),	// m22
		det * -(mat.MAT(0, 0) * A1312 - mat.MAT(0, 1) * A0312 + mat.MAT(0, 3) * A0112),	// m23
		det * -(mat.MAT(1, 0) * A1223 - mat.MAT(1, 1) * A0223 + mat.MAT(1, 2) * A0123),	// m30
		det *  (mat.MAT(0, 0) * A1223 - mat.MAT(0, 1) * A0223 + mat.MAT(0, 2) * A0123),	// m31
		det * -(mat.MAT(0, 0) * A1213 - mat.MAT(0, 1) * A0213 + mat.MAT(0, 2) * A0113),	// m32
		det *  (mat.MAT(0, 0) * A1212 - mat.MAT(0, 1) * A0212 + mat.MAT(0, 2) * A0112) 	// m33
	};
}

Mat4 Mat4::make_translated(const Vec3& translation)
{
	return {
		1, 0, 0, translation.x,
		0, 1, 0, translation.y,
		0, 0, 1, translation.z,
		0, 0, 0, 1
	};
}

Mat4 Mat4::make_rotation(float radians, const Vec3& axis)
{
	// make sure axis is normalized
	Vec3 normalized = axis.Normalized();

	float s = sin(radians);
	float c = cos(radians);

	Mat4 result = Identity();

	result.MAT(0, 0) = c + (1 - c) * axis.x * axis.x;
	result.MAT(0, 1) = (1 - c) * axis.x * axis.y - s * axis.z;
	result.MAT(0, 2) = (1 - c) * axis.x * axis.z + s * axis.y;

	result.MAT(1, 0) = axis.x * axis.y * (1 - c) + s * axis.z;
	result.MAT(1, 1) = c + (1 - c) * axis.y * axis.y;
	result.MAT(1, 2) = (1 - c) * axis.y * axis.z - s * axis.x;

	result.MAT(2, 0) = axis.x * axis.z * (1 - c) - s * axis.y;
	result.MAT(2, 1) = axis.y * axis.z * (1 - c) + s * axis.x;
	result.MAT(2, 2) = c + (1 - c) * axis.z * axis.z;

	return result;
}

Mat4 Mat4::make_rotation_x(float radians)
{
	return make_rotation(radians, Vec3(1, 0, 0));
}

Mat4 Mat4::make_rotation_y(float radians)
{
	return make_rotation(radians, Vec3(0, 1, 0));
}

Mat4 Mat4::make_rotation_z(float radians)
{
	return make_rotation(radians, Vec3(0, 0, 1));
}

Mat4 Mat4::make_scale(const Vec3& scale)
{
	return {
		scale.x, 0, 0, 0,
		0, scale.y, 0, 0,
		0, 0, scale.z, 0,
		0, 0, 0, 1
	};
}

Mat4 Mat4::orthographic(float left, float right, float bottom, float top, float near, float far)
{
	Mat4 result = Identity();
	/*
	2/r-l		0		0		l+r/l-r
	0		2/t-b		0		t+b/b-t
	0			0		2/n-f	f+n/f-n
	0			0		0			1
	*/

	result.MAT(0, 0) = 2.0f / (right - left);
	result.MAT(1, 1) = 2.0f / (top - bottom);
	result.MAT(2, 2) = 2.0f / (near - far);
	result.MAT(0, 3) = (left + right) / (left - right);
	result.MAT(1, 3) = (bottom + top) / (bottom - top);
	result.MAT(2, 3) = (far + near) / (far - near);

	return result;
}

Mat4 Mat4::perspective(float fov, float aspectRatio, float near, float far)
{
	Mat4 result = Identity();

	/*
	1/(a*tan(fov/2))	0				0			0
		0			1/fan(fov/2))		0			0
		0				0			n+f/n-f		2*f*n/n-f
		0				0				-1			0
	*/
	float q = 1.0f / (float)tan(toRadians(0.5f * fov));
	float a = q / aspectRatio;
	float b = (near + far) / (near - far);
	float c = (2.0f * near * far) / (near - far);

	result.MAT(0, 0) = a;
	result.MAT(1, 1) = q;
	result.MAT(2, 2) = b;
	result.MAT(2, 3) = c;
	result.MAT(3, 2) = -1.0f;

	return result;
}

Mat4 Mat4::make_transposed(const Mat4& other)
{
	Mat4 result = Zero();

	for (size_t i = 0; i < 4; i++)
		for (size_t j = 0; j < 4; j++)
			result.MAT(i, j) = other.MAT(j, i);

	return result;

}

Mat4 Mat4::make_multiplied(const Mat4& a, const Mat4& b)
{
	Mat4 result = Zero();
	float sum;

	// for each result's row/col
	for (size_t r = 0; r < 4; r++) {
		for (size_t c = 0; c < 4; c++) {

			// result[r][c] = sum(a[r][k] * b[k][c] for each k in range(4))
			sum = 0.0f;

			for (size_t k = 0; k < 4; k++)
				sum += a.MAT(r, k) * b.MAT(k, c);

			result.MAT(r, c) = sum;
		}
	}

	return result;
}
