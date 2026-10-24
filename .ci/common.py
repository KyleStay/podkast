"""Local execution and evidence helpers; no GitHub Actions API or credentials."""
import datetime,json,os,pathlib,shutil,subprocess,sys,signal
ROOT=pathlib.Path(__file__).resolve().parents[1]
RESULTS=ROOT/'.ci/results'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'-'+str(os.getpid()))
COMMANDS=[]
class Incomplete(RuntimeError): pass
class SignalInterrupted(BaseException):
    def __init__(self,signum): self.signum=signum

def interrupt_signal(signum,frame):
    signal.signal(signum,signal.SIG_IGN)
    raise SignalInterrupted(signum)
def guard():
    if os.environ.get('GITHUB_ACTIONS','').lower()=='true': raise Incomplete('GitHub-hosted CI is prohibited; run locally')
    files=[str(p.relative_to(ROOT)) for p in (ROOT/'.github/workflows').glob('*') if p.suffix.lower() in {'.yml','.yaml'}]
    if files: raise Incomplete('Active workflow source is prohibited: '+', '.join(files))
def need_tool(name):
    if not shutil.which(name): raise Incomplete('Missing local tool: '+name)
def need(condition,message):
    if not condition: raise Incomplete(message)
def run(args,cwd=ROOT,env=None):
    print('+ '+' '.join(map(str,args)),flush=True)
    RESULTS.mkdir(parents=True,exist_ok=True)
    log=RESULTS/(str(len(COMMANDS)+1)+'.log')
    process=None;code=None;interrupted=False
    with log.open('w') as output:
        try:
            process=subprocess.Popen(list(map(str,args)),cwd=cwd,env={**os.environ,**(env or {})},stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=os.name!='nt')
            for line in process.stdout:
                output.write(line);output.flush();print(line,end='',flush=True)
            code=process.wait()
        except BaseException as error:
            interrupted=isinstance(error,(KeyboardInterrupt,SignalInterrupted))
            if process is not None and process.poll() is None:
                if os.name=='nt': process.terminate()
                else: os.killpg(process.pid,signal.SIGTERM)
                try: process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    if os.name=='nt': process.kill()
                    else: os.killpg(process.pid,signal.SIGKILL)
                    process.wait()
            code=(128+error.signum if isinstance(error,SignalInterrupted) else 130) if interrupted else (process.returncode if process is not None else 127)
            raise
        finally:
            COMMANDS.append(dict(command=list(map(str,args)),cwd=str(cwd),exit_code=code,interrupted=interrupted,log=str(log.relative_to(ROOT))))
    if code: raise subprocess.CalledProcessError(code,args)

def main(lanes,all_lanes):
    import argparse,platform
    parser=argparse.ArgumentParser(description='Run local checks; each lane is reported separately. No hosted fallback.')
    parser.add_argument('lane',nargs='?',default='all',choices=['all',*lanes])
    parser.add_argument('--check',action='store_true',help='Guard and Python syntax only; no application test coverage')
    parser.add_argument('--list',action='store_true',help='List local lanes without claiming they passed')
    args=parser.parse_args();code=0;status='passed'
    for name in ['SIGTERM','SIGHUP']:
        if hasattr(signal,name): signal.signal(getattr(signal,name),interrupt_signal)
    try:
        guard()
        if args.check:
            for file in (ROOT/'.ci').glob('*.py'): compile(file.read_text(),str(file),'exec')
            print('Local-only guard and syntax passed; project tests were not run');return
        if args.list:
            print('Available lanes: '+', '.join(lanes));print('Default all requires: '+', '.join(all_lanes));return
        selected=all_lanes if args.lane=='all' else [args.lane]
        for lane in selected:
            print('Local lane: '+lane,flush=True);lanes[lane]()
    except Incomplete as error: code=2;status='incomplete';print(str(error),file=sys.stderr)
    except subprocess.CalledProcessError as error: code=error.returncode or 1;status='failed'
    except SignalInterrupted as error: code=128+error.signum;status='interrupted'
    except KeyboardInterrupt: code=130;status='interrupted'
    except Exception as error: code=1;status='failed';print(type(error).__name__+': '+str(error),file=sys.stderr)
    finally:
        RESULTS.mkdir(parents=True,exist_ok=True)
        (RESULTS/'receipt.json').write_text(json.dumps(dict(schema=1,time=datetime.datetime.now(datetime.timezone.utc).isoformat(),lane=args.lane,status=status,exit_code=code,scope='guard-only' if args.check else 'lane-list' if args.list else args.lane,full_matrix_requested=args.lane=='all' and not args.check and not args.list,host=platform.platform(),commands=COMMANDS),indent=2)+'\n')
    raise SystemExit(code)
