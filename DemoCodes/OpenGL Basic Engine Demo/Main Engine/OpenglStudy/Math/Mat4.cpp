#include "mat4.h"


// row-column access to 1d array
#define MAT(r, c) m[r + c * 4]


Mat4::Mat4(float diagonal)
{
	for (int i = 0; i < 4 * 4; i++)
		m[i] = 0.0f;

	MAT(0, 0) = diagonal;
	MAT(1, 1) = diagonal;
	MAT(2, 2) = diagonal;
	MAT(3, 3) = diagonal;
}

Mat4 Mat4::Identity()
{
	return Mat4(1.0f);
}

Mat4 Mat4::GetInverse()
{
	// TODO: Implement this
	return Mat4();
}

Mat4 Mat4::GetTranspose()
{
	Mat4 mat;

	for (int i = 0; i < 4; i++)
		for (int j = i + 1; j < 4; j++)
			mat.m[i + j * 4] = m[j + i * 4];

	return mat;
}


Mat4& Mat4::multiply(const Mat4& other)
{
	*this = *this * other;
	return *this;
}

void Mat4::Translate(float x_, float y_, float z_)
{
	MAT(0, 3) += x_;
	MAT(1, 3) += y_;
	MAT(2, 3) += z_;
}

void Mat4::Translate(const Vec3& rhs)
{
	MAT(0, 3) += rhs.x;
	MAT(1, 3) += rhs.y;
	MAT(2, 3) += rhs.z;
}

void Mat4::Scale(float x_, float y_, float z_)
{
	MAT(0, 0) *= x_;
	MAT(1, 1) *= y_;
	MAT(2, 2) *= z_;
}

void Mat4::Scale(const Vec3& scale)
{
	Scale(scale.x, scale.y, scale.z);
}

void Mat4::Scale(float scale_)
{
	Scale(scale_, scale_, scale_);
}

void Mat4::RotateZ(float radians)
{
	float c = cos(radians);
	float s = sin(radians);

	Mat4 rotationMatrix(1.0f);

	rotationMatrix.MAT(0, 0) = c;
	rotationMatrix.MAT(1, 0) = -s;
	rotationMatrix.MAT(0, 1) = s;
	rotationMatrix.MAT(1, 1) = c;
	
	// TODO: check if this deepcopies array
	*this = multiply(rotationMatrix);
}

void Mat4::RotateX(float radians)
{
	float c = cos(radians);
	float s = sin(radians);

	Mat4 rotationMatrix(1.0f);
	rotationMatrix.m[1 + 1 * 4] = c;
	rotationMatrix.m[2 + 1 * 4] = -s;
	rotationMatrix.m[1 + 2 * 4] = s;
	rotationMatrix.m[2 + 2 * 4] = c;

	*this = multiply(rotationMatrix);
}

void Mat4::RotateY(float radians)
{
	float c = cos(radians);
	float s = sin(radians);

	Mat4 rotationMatrix(1.0f);
	rotationMatrix.m[0 + 0 * 4] = c;
	rotationMatrix.m[2 + 0 * 4] = s;
	rotationMatrix.m[0 + 2 * 4] = -s;
	rotationMatrix.m[2 + 2 * 4] = c;

	*this = multiply(rotationMatrix);
}

void Mat4::Rotate(float radians, const Vec3& axis)
{
	*this *= rotation(radians, axis);
}

Mat4 Mat4::operator*(const Mat4 other) const
{
	Mat4 new_mat;

	for (size_t r = 0; r < 4; r++) {
		for (size_t c = 0; c < 4; c++) {
			float sum = 0.0f;

			for (size_t k = 0; k < 4; k++)
				sum += MAT(c, k) * other.MAT(k, r);

			new_mat.MAT(c, r) = sum;
		}
	}

	return new_mat;
}

Mat4& Mat4::operator*=(const Mat4& other)
{
	return multiply(other);
}

bool Mat4::operator==(const Mat4& mat) const
{
	for (int i = 0; i < 4 * 4; i++)
		if (m[i] != mat.m[i])
			return false;

	return true;
}

Mat4 Mat4::identity()
{
	return Mat4();
}

Mat4 Mat4::inverse(const Mat4 m)
{
	// TODO: Implement this
	return Mat4();
}

Mat4 Mat4::translate(const Vec3& translation)
{

	return Mat4();
}

Mat4 Mat4::rotation(float radians, const Vec3& axis)
{
	float s = sin(radians);
	float c = cos(radians);

	Mat4 result(1.0f);

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

Mat4 Mat4::rotationX(float radians)
{
	return Mat4();
}

Mat4 Mat4::rotationY(float radians)
{
	return Mat4();
}

Mat4 Mat4::rotationZ(float radians)
{
	return Mat4();
}

Mat4 Mat4::scale(const Vec3& scale)
{
	return Mat4();
}

Mat4 Mat4::orthographic(float left, float right, float bottom, float top, float near, float far)
{
	Mat4 result(1.0f);
	/*
	2/r-l		0		0		l+r/l-r
	0		2/t-b		0		t+b/b-t
	0			0		2/n-f	f+n/f-n
	0			0		0			1
	*/

	result.MAT(0, 0) = 2.0f / (right - left);
	result.MAT(1, 1) = 2.0f / (top - bottom);
	result.MAT(2, 2) = 2.0f / (near - far);
	result.MAT(3, 0) = (left + right) / (left - right);
	result.MAT(3, 1) = (bottom + top) / (bottom - top);
	result.MAT(3, 2) = (far + near) / (far - near);

	return result;
}

Mat4 Mat4::perspective(float fov, float aspectRatio, float near, float far)
{
	Mat4 result(1.0f);

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
