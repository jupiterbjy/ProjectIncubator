#ifndef HIN_CAM_H_
#define HIN_CAM_H_

#include "../Math/YAMath.h"


struct Cam
{
	Mat4 transform;
	Vec3 cam_target;

	Mat4 view_matrix;

	Vec3 forward() const {
		// Cam z -axis is the opposite direction of the forward vector
		// So subtract current position from target position
		return (cam_target - transform.position()).Normalize();
	}

	Vec3 right() const {
		// Use global up vector(0, 1, 0) to get the right vector
		// Doing cross product anyway so result remains the same
		return Vec3::cross(Vec3(0, 1, 0), forward()).Normalize();
	}

	Vec3 up() const {
		return Vec3::cross(forward(), right()).Normalize();
	}

	Mat4 _lookAt()
	{
		// TODO: Add caching of these values
		Vec3 right_v = right();
		Vec3 up_v = up();
		Vec3 forward_v = forward();
		Vec3 pos = transform.position();

		// [ right_v,    0 ]
		// [ up_v,       0 ]
		// [ forward_v,  0 ]
		// [ 0,  0,  0,  1 ]

		Mat4 temp;
		temp.m[0 + 0 * 4] = right_v.x;
		temp.m[0 + 1 * 4] = right_v.y;
		temp.m[0 + 2 * 4] = right_v.z;

		temp.m[1 + 0 * 4] = up_v.x;
		temp.m[1 + 1 * 4] = up_v.y;
		temp.m[1 + 2 * 4] = up_v.z;

		temp.m[2 + 0 * 4] = -forward_v.x;
		temp.m[2 + 1 * 4] = -forward_v.y;
		temp.m[2 + 2 * 4] = -forward_v.z;

		// [ 1, 0, 0, -pos.x ]
		// [ 0, 1, 0, -pos.y ]
		// [ 0, 0, 1, -pos.z ]
		// [ 0, 0, 0,      1 ]
		Mat4 temp_2;

		temp_2.m[0 + 3 * 4] = -pos.x;
		temp_2.m[1 + 3 * 4] = -pos.y;
		temp_2.m[2 + 3 * 4] = -pos.z;

		view_matrix =  temp * temp_2;
		return view_matrix;
	}

	void translate(float x, float y, float z) {
		transform.Translate(x, y, z);
		view_matrix = _lookAt();
	}

	void position(float x, float y, float z) {
		transform.m[0 + 3 * 4] = x;
		transform.m[1 + 3 * 4] = y;
		transform.m[2 + 3 * 4] = z;
		view_matrix = _lookAt();
	}

	Cam() {
		view_matrix = _lookAt();
	}

};

#endif // !HIN_CAM_H_
