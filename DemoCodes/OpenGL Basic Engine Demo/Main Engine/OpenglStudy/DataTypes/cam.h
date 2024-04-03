#ifndef HIN_CAM_H_
#define HIN_CAM_H_

#include "../Math/YAMath.h"
#include "object_base.h"


// row-column access to 1d array
#define MAT(r, c) m[r + c * 4]


struct Cam : ObjectBase
{
	Vec3 cam_target;

	Vec3 forward() const {
		// Cam z -axis is the opposite direction of the forward vector
		// So subtract current position from target position
		return (cam_target - get_position()).Normalize();
	}

	Vec3 right() const {
		// Use global up vector(0, 1, 0) to get the right vector
		// Doing cross product anyway so result remains the same
		return Vec3::cross(Vec3(0, 1, 0), forward()).Normalize();
	}

	Vec3 up() const {
		return Vec3::cross(forward(), right()).Normalize();
	}

	void translate(float x, float y, float z) {
		((ObjectBase*)this)->position(x, y, z);
		look_at(cam_target);
	}

	void position(const Vec3& pos) {
		((ObjectBase*)this)->position(pos);
		look_at(cam_target);
	}

	void look_at(const Vec3& target_pos, const Vec3 up_vec = basis_vec::DEFAULT_UP) {
		// need to flip value so going dirty on copy paste and violating DRY
		// TODO: Find if it's better to override forward only or not
		
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

		temp.MAT(2, 0) = -forward_v.x;
		temp.MAT(2, 1) = -forward_v.y;
		temp.MAT(2, 2) = -forward_v.z;

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

	void position(float x, float y, float z) {
		((ObjectBase*)this)->position(x, y, z);
		look_at(cam_target);
	}

	Cam() {
		look_at(cam_target);
	}

};

#endif // !HIN_CAM_H_
