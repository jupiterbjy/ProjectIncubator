#include "mat4.h"


Mat4::Mat4(float diagonal)
{
	for (int i = 0; i < 4 * 4; i++)
		m[i] = 0.0f;

	m[0 + 0 * 4] = diagonal;
	m[1 + 1 * 4] = diagonal;
	m[2 + 2 * 4] = diagonal;
	m[3 + 3 * 4] = diagonal;
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
	m[0 + 3 * 4] += x_;
	m[1 + 3 * 4] += y_;
	m[2 + 3 * 4] += z_;
}

void Mat4::Translate(const Vec3& rhs)
{
	m[0 + 3 * 4] += rhs.x;
	m[1 + 3 * 4] += rhs.y;
	m[2 + 3 * 4] += rhs.z;
}

void Mat4::Scale(float x_, float y_, float z_)
{
	m[0 + 0 * 4] *= x_;
	m[1 + 1 * 4] *= y_;
	m[2 + 2 * 4] *= z_;
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
	rotationMatrix.m[0 + 0 * 4] = c;
	rotationMatrix.m[1 + 0 * 4] = -s;
	rotationMatrix.m[0 + 1 * 4] = s;
	rotationMatrix.m[1 + 1 * 4] = c;
	
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
				sum += m[c + k * 4] * other.m[k + r * 4];

			new_mat.m[c + r * 4] = sum;
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

	result.m[0 + 0 * 4] = c + (1 - c) * axis.x * axis.x;
	result.m[0 + 1 * 4] = (1 - c) * axis.x * axis.y - s * axis.z;
	result.m[0 + 2 * 4] = (1 - c) * axis.x * axis.z + s * axis.y;

	result.m[1 + 0 * 4] = axis.x * axis.y * (1 - c) + s * axis.z;
	result.m[1 + 1 * 4] = c + (1 - c) * axis.y * axis.y;
	result.m[1 + 2 * 4] = (1 - c) * axis.y * axis.z - s * axis.x;

	result.m[2 + 0 * 4] = axis.x * axis.z * (1 - c) - s * axis.y;
	result.m[2 + 1 * 4] = axis.y * axis.z * (1 - c) + s * axis.x;
	result.m[2 + 2 * 4] = c + (1 - c) * axis.z * axis.z;

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

	result.m[0 + 0 * 4] = 2.0f / (right - left);
	result.m[1 + 1 * 4] = 2.0f / (top - bottom);
	result.m[2 + 2 * 4] = 2.0f / (near - far);
	result.m[3 + 0 * 4] = (left + right) / (left - right);
	result.m[3 + 1 * 4] = (bottom + top) / (bottom - top);
	result.m[3 + 2 * 4] = (far + near) / (far - near);

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


	result.m[0 + 0 * 4] = a;
	result.m[1 + 1 * 4] = q;
	result.m[2 + 2 * 4] = b;
	result.m[2 + 3 * 4] = c;
	result.m[3 + 2 * 4] = -1.0f;

	return result;
}

Vec3 Mat4::position() const
{
	return Vec3(m[0 + 3 * 4], m[1 + 3 * 4], m[2 + 3 * 4]);
}
