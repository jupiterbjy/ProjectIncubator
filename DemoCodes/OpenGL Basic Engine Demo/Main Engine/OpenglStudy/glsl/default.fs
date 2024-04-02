#version 330 core
out vec4 FragColor;

in vec3 FragPos; 
in vec3 Normal;

uniform mat4 model;
uniform vec3 lightPos; 
uniform vec3 objectColor;
// uniform Material material;


// material structs
// float shininess;
// float ambient;
// float diffuse;
// float specular;
// 
// sampler2D diffuse, specular, normal, height;
// sampler2D[5] textures;


void main()
{
    // ambient
    float ambient = 0.2f;
  	
    // diffuse 
    vec3 norm = normalize(mat3(model) * Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
            
    vec3 result = (ambient + diff) * objectColor;

    FragColor = vec4(result, 1.0);
}