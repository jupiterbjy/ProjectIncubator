#ifndef HIN_MESH_H_
#define HIN_MESH_H_

#include <unordered_map>
#include "../Math/YAMath.h"
#include "glad/glad.h"


namespace vo_state {
    static std::unordered_map<size_t, GLuint> hash_vbo_map;
    static std::unordered_map<size_t, GLuint> hash_vao_map;

    static size_t bound_hash = 0;
    // void unregister_mesh();
};


struct Mesh {
    float* p_verts = nullptr;
    size_t size = 0;
    size_t hash = 0;

    Vec3 color = { 1.0f, 1.0f, 1.0f };

    Mat4 transform;

    Mesh() {};

    // Create Mesh from array pointer
    Mesh(const float a_vert_arr[], size_t vert_count);

    // Create Mesh with known hash
    Mesh(const float a_vert_arr[], size_t vert_count, size_t a_hash);

    // Move from another Mesh
    Mesh(Mesh&& mesh) noexcept;

    ~Mesh() {
        delete[] p_verts;
    }

    // initializer job
    void init(const float a_vert_arr[], size_t vert_count);

    // Swap two Mesh
    void swap(Mesh& mesh);

    void rotate(float rad_amount, const Vec3& axis);

    void translate(const Vec3& translation);

    void translate(float x, float y, float z);

    void scale(const Vec3& scale);

    // Cube mesh builder
    static Mesh Cube();

    // Plane mesh builder
    static Mesh Plane();
};


void vao_bind(const Mesh& mesh);

void vao_register(const Mesh& mesh);


struct Vertice {
    Vec3 pos;
    Vec3 normal;

    inline Vertice(float x, float y, float z, float norm_x, float norm_y, float norm_z)
        : pos(x, y, z), normal(norm_x, norm_y, norm_z) {}
};

#endif // !HIN_MESH_H_
