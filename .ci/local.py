import os,pathlib,re,shutil,subprocess,tempfile
from common import ROOT,Incomplete,main,need,run

def node_lane(major):
    node=os.environ.get('NODE'+str(major)+'_BIN') or shutil.which('node')
    need(node,'Provide NODE'+str(major)+'_BIN for the original Node matrix')
    node=pathlib.Path(node).resolve()
    version=subprocess.check_output([str(node),'--version'],text=True).strip()
    need(version.startswith('v'+str(major)+'.'),'Node '+str(major)+' is required; got '+version)
    npm=node.parent/'npm'
    need(npm.exists(),'Matching npm is required next to '+str(node))
    work_base=ROOT/'.ci/work';work_base.mkdir(parents=True,exist_ok=True)
    environment={'PATH':str(node.parent)+os.pathsep+os.environ.get('PATH',''),'CI':'true'}
    # Every invocation gets current source. Reuse npm's cache, never prior source.
    with tempfile.TemporaryDirectory(prefix='node'+str(major)+'-',dir=work_base) as directory:
        work=pathlib.Path(directory)/'ClientApp'
        shutil.copytree(ROOT/'podkast/ClientApp',work,ignore=shutil.ignore_patterns('node_modules','build'))
        run([str(npm),'install'],cwd=work,env=environment)
        run([str(npm),'test','--','--runInBand'],cwd=work,env=environment)

main({'node8':lambda:node_lane(8),'node10':lambda:node_lane(10),'node12':lambda:node_lane(12)},['node8','node10','node12'])
