#version 330

in vec2 vertexCoord;
in vec2 texCoord;
uniform mat4 mvp;
out vec2 transformedTexCoord;

void main() {
    gl_Position = mvp * vec4(vertexCoord, 0.0, 1.0);
    transformedTexCoord = texCoord;
}
