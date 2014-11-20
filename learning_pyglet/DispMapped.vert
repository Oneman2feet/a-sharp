#version 120

uniform sampler2D disp_texture;

uniform float dispMagnitude;

varying vec3 fN;
varying vec4 worldPos;
varying vec3 eyeVec;

void main() {
  gl_TexCoord[0] = gl_TextureMatrix[0] * gl_MultiTexCoord0;

  vec3 values = texture2D(disp_texture, gl_TexCoord[0].st).rgb;
  vec3 heights = values;
  float average = (heights.x + heights.y + heights.z) / 3;
  vec4 newPos = gl_Vertex + vec4(gl_Normal, 0) * dispMagnitude * average;

  worldPos = gl_ModelViewMatrix * newPos;

  eyeVec = -newPos.xyz;

  gl_Position = gl_ProjectionMatrix * worldPos;

  fN = normalize(gl_NormalMatrix * gl_Normal);
}