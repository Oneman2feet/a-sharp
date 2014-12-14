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
varying vec4 dispColor;

void main() {
  gl_TexCoord[0] = gl_TextureMatrix[0] * gl_MultiTexCoord0;

  float disp = texture2D(disp_texture, gl_TexCoord[0].st).g;
  dispColor = texture2D(disp_texture, gl_TexCoord[0].st);
  // vec3 heights = dispColor;
  // float average = ((heights.x + heights.y + heights.z) / 3);

  vec4 newPos = vec4(gl_Vertex.xyz * radius, gl_Vertex.w);

  int index = gl_VertexID % 48;
  // if(index == 0 || index == 3 || index == 43 || index == 41 || index == 34 || index == 32) {
  //   newPos = gl_Vertex + vec4(gl_Normal, 0) * bump;
  // }
  //if(index == 0 || index == 3 || index == 43 || index == 29 || index == 22 || index == 20){
  //  newPos = newPos + vec4(gl_Normal, 0) * bump;
  //}

  // if(gl_VertexID % 10 == 1 || gl_VertexID % 10 == 9) {
  //   newPos = gl_Vertex + vec4(gl_Normal, 0) * bump * (1/2);
  // }


  // newPos = newPos + vec4(gl_Normal, 0) * disp;

  worldPos = newPos;

  eyeVec = -newPos.xyz;

  gl_Position = gl_ProjectionMatrix * gl_ModelViewMatrix * worldPos;

  fN = normalize(gl_NormalMatrix * gl_Normal);
}