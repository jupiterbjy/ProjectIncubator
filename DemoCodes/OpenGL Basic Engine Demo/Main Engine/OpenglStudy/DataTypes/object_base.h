#ifndef HIN_OBJECT_BASE_H_
#define HIN_OBJECT_BASE_H_


#include "../Math/YAMath.h"


namespace basis_vec
{
    const Vec3 DEFAULT_UP = Vec3(0, 1, 0);
}


class ObjectBase {
    // Honestly this doesn't need to be a class as we're gonna expose transform

    float _scaling_factor(int row) const;

public:
    Mat4 transform = Mat4::Identity();

    // Local up vector
    Vec3 up() const;

    // Local forward vector
    Vec3 forward() const;
    
    // Local right vector
    Vec3 right() const;

    void look_at(float x, float y, float z, const Vec3 up_vec = Vec3(0, 1, 0));
    void look_at(const Vec3& target_pos, const Vec3 up_vec = Vec3(0, 1, 0));
    void look_at(const ObjectBase& target_obj, const Vec3 up_vec = Vec3(0, 1, 0));

    void rotate(float rad_amount, const Vec3& axis);
    void rotate(float rad_amount, float x, float y, float z);

    void translate(const Vec3& translation);
    void translate(float x, float y, float z);

    void scale(const Vec3& scale);
    void scale(float x, float y, float z);
    void scale(float scale);

    Vec3 get_position() const;
    Vec3 get_rotation() const;
    Vec3 get_scale() const;

    void position(const Vec3& pos);
    void position(float x, float y, float z);
};



#endif // !HIN_OBJECT_BASE_H_
