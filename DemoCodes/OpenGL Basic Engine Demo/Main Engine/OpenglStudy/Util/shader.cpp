#include "shader.h"

#include "glad/glad.h"

#include "IO.h"


void checkCompileErrors(GLuint shader, std::string type)
{
    GLint success;
    GLchar infoLog[1024];
    if (type != "PROGRAM")
    {
        glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
        if (!success)
        {
            glGetShaderInfoLog(shader, 1024, NULL, infoLog);
            std::cout << "ERROR::SHADER_COMPILATION_ERROR of type: " << type << "\n" << infoLog << "\n -- --------------------------------------------------- -- " << std::endl;
        }
    }
    else
    {
        glGetProgramiv(shader, GL_LINK_STATUS, &success);
        if (!success)
        {
            glGetProgramInfoLog(shader, 1024, NULL, infoLog);
            std::cout << "ERROR::PROGRAM_LINKING_ERROR of type: " << type << "\n" << infoLog << "\n -- --------------------------------------------------- -- " << std::endl;
        }
    }
}

Shader::Shader(const char* vertexPath, const char* fragmentPath)
{
    //Create Shader
    std::string vert_src = read_file(vertexPath);
    std::string frag_src = read_file(fragmentPath);

    char* vert_src_arr = new char[vert_src.size() + 1];
    strcpy_s(vert_src_arr, vert_src.size() + 1, vert_src.c_str());

    char* frag_src_arr = new char[frag_src.size() + 1];
    strcpy_s(frag_src_arr, frag_src.size() + 1, frag_src.c_str());

    // https://stackoverflow.com/a/32779192/10909029
    // Const casting allowed moment
    unsigned int vert_shader = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vert_shader, 1, const_cast<const char**>(&vert_src_arr), NULL);
    glCompileShader(vert_shader);
    checkCompileErrors(vert_shader, "VERTEX");

    unsigned int frag_shader = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(frag_shader, 1, const_cast<const char**>(&frag_src_arr), NULL);
    glCompileShader(frag_shader);
    checkCompileErrors(frag_shader, "FRAGMENT");

    ID = glCreateProgram();
    glAttachShader(ID, vert_shader);
    glAttachShader(ID, frag_shader);
    glLinkProgram(ID);
    checkCompileErrors(frag_shader, "PROGRAM");

    glUseProgram(ID);

    glDeleteShader(vert_shader);
    glDeleteShader(frag_shader);

    delete[] vert_src_arr;
    delete[] frag_src_arr;
}

void Shader::use()
{
    glUseProgram(ID);
}

void Shader::setBool(const std::string& name, bool value) const
{
    glUniform1i(glGetUniformLocation(ID, name.c_str()), (int)value);
}

void Shader::setInt(const std::string& name, int value) const
{
    glUniform1i(glGetUniformLocation(ID, name.c_str()), value);
}

void Shader::setFloat(const std::string& name, float value) const
{
    glUniform1f(glGetUniformLocation(ID, name.c_str()), value);
}

void Shader::setVec2(const std::string& name, float x, float y) const
{
    glUniform2f(glGetUniformLocation(ID, name.c_str()), x, y);
}

void Shader::setVec3(const std::string& name, const Vec3& value) const
{
    glUniform3fv(glGetUniformLocation(ID, name.c_str()), 1, &value.x);
}

void Shader::setVec3(const std::string& name, float x, float y, float z) const
{
    glUniform3f(glGetUniformLocation(ID, name.c_str()), x, y, z);
}

void Shader::setMat4(const std::string& name, const Mat4& mat) const
{
    glUniformMatrix4fv(glGetUniformLocation(ID, name.c_str()), 1, GL_FALSE, &mat.m[0]);
}
