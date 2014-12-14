#version 110
#extension GL_EXT_gpu_shader4 : require

uniform sampler2D color_texture;
uniform sampler2D disp_texture;

uniform float dispMagnitude;
uniform float bump;
uniform float radius;
uniform mat4 model;

varying vec3 fN;
varying vec4 worldPos;
varying vec3 eyeVec;

void main() {
  gl_TexCoord[0] = gl_MultiTexCoord0;

  float disp = texture2D(disp_texture, gl_TexCoord[0].st).g;
  vec4 newPos = vec4(gl_Vertex.xyz * radius, gl_Vertex.w);
  newPos = newPos + vec4(gl_Normal, 0) * disp * 2.0;

  worldPos = newPos;
  eyeVec = -newPos.xyz;
  gl_Position = gl_ProjectionMatrix * gl_ModelViewMatrix * worldPos;

  fN = normalize(gl_NormalMatrix * gl_Normal);
}