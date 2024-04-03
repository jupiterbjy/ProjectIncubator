#include "mesh.h"

#include "glad/glad.h"

#include "struct.h"


void vao_bind(const Mesh& mesh)
{
    // Assuming all Mesh creation goes through register_mesh
    const auto VAO = vo_state::hash_vao_map[mesh.hash];
    const auto VBO = vo_state::hash_vbo_map[mesh.hash];

    glBindVertexArray(VAO);
    //vo_state::bound_hash = mesh.hash;
}


void vao_register(const Mesh& mesh)
{
    if (vo_state::hash_vao_map.find(mesh.hash) != vo_state::hash_vao_map.end())
        return;

    GLuint new_vao, new_vbo;

    // https://community.khronos.org/t/understanding-vaos-vbos-and-drawing-two-objects/72778/6
        
    glGenBuffers(1, &new_vbo);
    glBindBuffer(GL_ARRAY_BUFFER, new_vbo);

    // Let GL populate VBO with our array.
    // GL_STREAM_DRAW: only set once, used rarely, so stream from system memory?
    // GL_STATIC_DRAW: only set once, used a lot, so keep in VRAM?
    // GL_DYNAMIC_DRAW: changes a lot over time and used just as much.
    glBufferData(GL_ARRAY_BUFFER, sizeof(mesh.p_verts), mesh.p_verts, GL_STATIC_DRAW);
        
    glGenVertexArrays(1, &new_vao);
    glBindVertexArray(new_vao);

    // Link Vertex attributes
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);

    // Link Normal attributes
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);

    glBufferData(GL_ARRAY_BUFFER, sizeof(cube_verts), &cube_verts, GL_STATIC_DRAW);

    // reset binding
    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindVertexArray(0);

    vo_state::hash_vao_map[mesh.hash] = new_vao;
    vo_state::hash_vbo_map[mesh.hash] = new_vbo;
    // vo_state::bound_hash = 0;
}


void Mesh::init(const float a_vert_arr[], size_t vert_count)
{
    p_verts = new float[vert_count];

    for (size_t i = 0; i < vert_count; i++)
        p_verts[i] = a_vert_arr[i];

    vao_register(*this);
}

void Mesh::swap(Mesh& mesh)
{
    std::swap(size, mesh.size);
	std::swap(hash, mesh.hash);
	std::swap(p_verts, mesh.p_verts);
}


void Mesh::rotate(float rad_amount, const Vec3& axis)
{
    transform.rotate(rad_amount, axis);
}


void Mesh::translate(const Vec3& translation)
{
    transform.translate(translation);
}

void Mesh::translate(float x, float y, float z)
{
    transform.translate(x, y, z);
}


void Mesh::scale(const Vec3& scale)
{
	transform.scale(scale);
}


Mesh::Mesh(const float a_vert_arr[], size_t vert_count)
    : size(vert_count) {

    hash = hash_1d_array<float>(a_vert_arr, vert_count);
    init(a_vert_arr, vert_count);
}


Mesh::Mesh(const float a_vert_arr[], size_t vert_count, size_t a_hash)
    : size(vert_count), hash(a_hash) {

    init(a_vert_arr, vert_count);
}


//Mesh::Mesh(Mesh&& mesh) noexcept
//{
//    swap(mesh);
//}


#define PRIMITIVE(m) { m, m##_size, m##_hash }


Mesh Mesh::Cube() {
    return PRIMITIVE(cube_verts);
}


Mesh Mesh::Plane() {
    return PRIMITIVE(plane_verts);
}
