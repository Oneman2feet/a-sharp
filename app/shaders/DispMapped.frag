#version 120

uniform sampler2D color_texture;
uniform sampler2D normal_texture;
uniform float elapsed_time;

uniform float diffuse_r;
uniform float diffuse_g;
uniform float diffuse_b;

uniform vec3 lightIntensity;
uniform vec3 lightPosition;
uniform vec3 ambientLightIntensity;

varying vec3 fN;
varying vec4 worldPos;
varying vec3 eyeVec;

void main() {
    // vec3 normalColor = texture2D(normal_texture, gl_TexCoord[0].st).rgb;
    // vec3 N = normalize(gl_NormalMatrix * ((normalColor * 2) - 1));
    vec3 N = normalize(fN);
    vec3 V = normalize(-worldPos.xyz);

    vec4 texColor = vec4(texture2D(color_texture, gl_TexCoord[0].st).rgb, 1.0);

    vec4 sceneColor = gl_FrontLightModelProduct.sceneColor;
    vec4 rgb = vec4(texColor.rgb, 1.0);
    vec4 diffuse_color = vec4(diffuse_r, diffuse_g, diffuse_b, 1);
    
    vec4 finalColor = (sceneColor * rgb) +
        (gl_LightSource[0].ambient * rgb * diffuse_color);


    // float t = mod(elapsed_time, 2*bps);
    // float per = mod(elapsed_time / bps, 6);
    // if (per < 2) {
    //     finalColor.x += abs(worldPos.x) - abs((1 - t/bps) * worldPos.x);
    // } else if (per < 4) {
    //     finalColor.y += abs(worldPos.x) - abs((1 - t/bps) * worldPos.x);
    // } else {
    //     finalColor.z += abs(worldPos.x) - abs((1 - t/bps) * worldPos.x);
    // }
    
    // finalColor.x += abs(pow(worldPos.x * worldPos.y, 0.5)) - abs((1 - t/bps) * worldPos.x);

    float r = length(gl_LightSource[0].position.xyz - worldPos.xyz);
    vec3 L = normalize(gl_LightSource[0].position.xyz - worldPos.xyz);
    vec3 H = normalize(L + V);

    vec4 Idiff = gl_LightSource[0].diffuse * gl_FrontMaterial.diffuse * max(dot(N, L), 0.0);
    Idiff = clamp(Idiff, 0.0, 1.0);

    float specular = pow(max(dot(N, H), 0.0), gl_FrontMaterial.shininess);
    vec4 Ispec = gl_LightSource[0].specular * gl_FrontMaterial.specular * specular;
    Ispec = clamp(Ispec, 0.0, 1.0);

    finalColor += (Ispec + Idiff) / (r * r);

    gl_FragColor = finalColor;
}