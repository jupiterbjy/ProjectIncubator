#pragma once

#include "../Math/YAMath.h"

#include <string>
#include <iostream>


class Shader
{
private:
    // Shader Program ID
    unsigned int ID;

public:
    Shader(const char* vertexPath, const char* fragmentPath);
    
    void use();

    unsigned int GetID() { return ID; }

    void setBool(const std::string& name, bool value) const;
    void setInt(const std::string& name, int value) const;
    void setFloat(const std::string& name, float value) const;
    void setVec2(const std::string& name, float x, float y) const;
    void setVec3(const std::string& name, const Vec3& value) const;
    void setVec3(const std::string& name, float x, float y, float z) const;
    void setMat4(const std::string& name, const Mat4& mat) const;
   
};