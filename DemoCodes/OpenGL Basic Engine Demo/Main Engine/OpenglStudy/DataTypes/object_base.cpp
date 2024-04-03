#include "object_base.h"

#include <cmath>
#include <glad/glad.h>
#include "../Math/YAMath.h"


// row-column access to 1d array
#define MAT(r, c) m[r + c * 4]


float ObjectBase::_scaling_factor(int row) const
{
	return std::sqrt(
		transform.MAT(row, 0) * transform.MAT(row, 0)
		+ transform.MAT(row, 1) * transform.MAT(row, 1)
		+ transform.MAT(row, 2) * transform.MAT(row, 2)
	);
}


// https://stackoverflow.com/a/50081973/10909029
Vec3 ObjectBase::up() const
{
	return Vec3(transform.MAT(1, 0), transform.MAT(1, 1), transform.MAT(1, 2));
}

Vec3 ObjectBase::forward() const
{
	return Vec3(transform.MAT(0, 2), transform.MAT(1, 2), transform.MAT(2, 2));
}

Vec3 ObjectBase::right() const
{
	return Vec3(transform.MAT(0, 0), transform.MAT(1, 2), transform.MAT(2, 2));
}

void ObjectBase::look_at(float x, float y, float z, const Vec3 up_vec)
{
	look_at(Vec3(x, y, z));
}

void ObjectBase::look_at(const Vec3& target_pos, const Vec3 up_vec)
{
	// Setup new vectors
	Vec3 forward_v = (target_pos - get_position()).Normalize();
	Vec3 right_v = Vec3::normalize(Vec3::cross(Vec3(0, 1, 0), forward_v));
	Vec3 up_v = Vec3::normalize(Vec3::cross(forward_v, right_v));

	// [ right_v,    0 ]
	// [ up_v,       0 ]
	// [ forward_v,  0 ]
	// [ 0,  0,  0,  1 ]

	Mat4 temp = Mat4::Identity();

	temp.MAT(0, 0) = right_v.x;
	temp.MAT(0, 1) = right_v.y;
	temp.MAT(0, 2) = right_v.z;

	temp.MAT(1, 0) = up_v.x;
	temp.MAT(1, 1) = up_v.y;
	temp.MAT(1, 2) = up_v.z;

	temp.MAT(2, 0) = forward_v.x;
	temp.MAT(2, 1) = forward_v.y;
	temp.MAT(2, 2) = forward_v.z;

	// [ 1, 0, 0, -pos.x ]
	// [ 0, 1, 0, -pos.y ]
	// [ 0, 0, 1, -pos.z ]
	// [ 0, 0, 0,      1 ]

	Mat4 temp_2 = Mat4::Identity();
	Vec3 pos = get_position();

	temp_2.MAT(0, 3) = -pos.x;
	temp_2.MAT(1, 3) = -pos.y;
	temp_2.MAT(2, 3) = -pos.z;

	// return temp * temp_2;
	transform = temp * temp_2;
}


void ObjectBase::look_at(const ObjectBase& target_obj, const Vec3 up_vec)
{
	look_at(target_obj.get_position());
}

void ObjectBase::rotate(float rad_amount, const Vec3& axis)
{
	transform.rotate(rad_amount, axis);
}

void ObjectBase::rotate(float rad_amount, float x, float y, float z)
{
	rotate(rad_amount, Vec3(x, y, z));
}

void ObjectBase::translate(const Vec3& translation)
{
	transform.translate(translation);
}

void ObjectBase::translate(float x, float y, float z)
{
	translate(Vec3(x, y, z));
}

void ObjectBase::scale(const Vec3& scale)
{
	// Revert back scaling of matrix & add it
	transform.scale(Vec3(
		_scaling_factor(0) / scale.x,
		_scaling_factor(1) / scale.y,
		_scaling_factor(2) / scale.z
	));
}

void ObjectBase::scale(float x, float y, float z)
{
	scale(Vec3(x, y, z));
}

void ObjectBase::scale(float uniform_scale)
{
	scale(uniform_scale, uniform_scale, uniform_scale);
}

Vec3 ObjectBase::get_position() const
{
	return Vec3(transform.MAT(0, 3), transform.MAT(1, 3), transform.MAT(2, 3));
}

Vec3 ObjectBase::get_rotation() const
{
	// TODO: CHECK IMPLEMENTATION
	return {
		std::atan2(transform.MAT(2, 1), transform.MAT(2, 2)),
		std::asin(-transform.MAT(2, 0)),
		std::atan2(transform.MAT(1, 0), transform.MAT(0, 0))
	};
}

Vec3 ObjectBase::get_scale() const
{
	return {
		_scaling_factor(0), _scaling_factor(1), _scaling_factor(2)
	};
}


void ObjectBase::position(const Vec3& pos)
{
	// Revert back translation of matrix & add it
	translate(-get_position() + pos);
}

void ObjectBase::position(float x, float y, float z)
{
	position(Vec3(x, y, z));
}
