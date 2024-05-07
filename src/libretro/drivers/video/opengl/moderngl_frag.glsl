#version 330

uniform sampler2D texture;
in vec2 transformedTexCoord;
out vec4 pixelColor;

void main() {
    pixelColor = vec4(texture(texture, transformedTexCoord).rgb, 1.0f);
}
