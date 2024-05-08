#version 330

uniform sampler2D screenTexture;
in vec2 transformedTexCoord;
out vec4 pixelColor;

void main() {
    pixelColor = vec4(texture(screenTexture, transformedTexCoord).rgb, 1.0f);
}
