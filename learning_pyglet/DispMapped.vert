#version 120
#extension GL_EXT_gpu_shader4 : require

uniform sampler2D disp_texture;

uniform float dispMagnitude;
uniform float bump;

varying vec3 fN;
varying vec4 worldPos;
varying vec3 eyeVec;

void main() {
  gl_TexCoord[0] = gl_TextureMatrix[0] * gl_MultiTexCoord0;

  // vec3 dispColor = texture2D(disp_texture, gl_TexCoord[0].st).rgb;
  // vec3 heights = dispColor;
  // float average = ((heights.x + heights.y + heights.z) / 3);
  vec4 newPos = gl_Vertex;
  if(gl_VertexID % 10 == 0) {
    newPos = gl_Vertex + vec4(gl_Normal, 0) * bump;
  }

  worldPos = gl_ModelViewMatrix * newPos;

  eyeVec = -newPos.xyz;

  gl_Position = gl_ProjectionMatrix * worldPos;

  fN = normalize(gl_NormalMatrix * gl_Normal);
}