"""Test actual textured-view renderer for UV boundaries and integer-period shifts."""
import ast,json
from pathlib import Path
import numpy as np
from revision_expansion_common import OUT,write,sha
R=OUT/'iteration012_condition_interference/render_repeat_validation';SOURCE=Path(__file__).with_name('bake_fresh_c_native_uv.py')
def load(path):
 tree=ast.parse(path.read_text());node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='render_textured_view');namespace={'np':np};exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),namespace);return namespace['render_textured_view']
def render(fn,uv,repeat):
 geom={'triangles':np.zeros((1,3,3),np.float32),'triangle_uvs':np.repeat(np.asarray(uv,np.float32)[None,None,:],3,axis=1)};camera={'azimuth':0,'elevation':0};cache={(id(geom['triangles']),0,0,1):{'triangle':np.array([[0]]),'bary':np.array([[[1.,0,0]]]),'depth':np.ones((1,1))}};tex=np.arange(48,dtype=np.float32).reshape(4,4,3)/47;return fn(geom,tex,camera,1,cache,repeat)[0][0,0]
def reference(uv):
 tex=np.arange(48,dtype=np.float32).reshape(4,4,3)/47;u,v=uv;x=(u%1)*4-.5;y=(1-v%1)*4-.5;ix,iy=int(np.floor(x)),int(np.floor(y));fx,fy=x-ix,y-iy;weights=[(1-fx)*(1-fy),fx*(1-fy),(1-fx)*fy,fx*fy];assert min(weights)>=0 and abs(sum(weights)-1)<1e-12;return sum(w*tex[j%4,i%4] for w,(i,j) in zip(weights,[(ix,iy),(ix+1,iy),(ix,iy+1),(ix+1,iy+1)]))
new=load(SOURCE);old=load(R/'render_textured_view_before_fix.py');fixtures=[(u,v) for u in [-2.,-.125,0.,.125,.5,.875,1.,1.125,2.] for v in [-1.,0.,.125,.5,1.,2.]];old_errors=0;shifts=0
for uv in fixtures:
 actual=render(new,uv,True);assert np.allclose(actual,reference(uv),atol=2e-7);old_errors+=not np.allclose(render(old,uv,True),reference(uv),atol=2e-7);assert np.array_equal(render(new,uv,False),render(old,uv,False))
 for du,dv in [(-3,0),(0,4),(2,-2)]:assert np.allclose(actual,render(new,(uv[0]+du,uv[1]+dv),True),atol=2e-7);shifts+=1
assert old_errors>0
write(R/'RENDER_REPEAT_VALIDATION.json',{'status':'PASS_ACTUAL_RENDER_BOUNDARIES_AND_INTEGER_UV_PERIODS','boundary_fixtures':len(fixtures),'period_shift_comparisons':shifts,'nonrepeat_bitidentical_comparisons':len(fixtures),'old_reference_failures_reproduced':int(old_errors),'source_sha256':sha(SOURCE),'scope':'Actual renderer with controlled raster cache; validates interpolation, not camera/mesh/bake realism. Previously executed sources preserved.'});print('PASS',len(fixtures),'boundaries',shifts,'period shifts; old failures',old_errors)
