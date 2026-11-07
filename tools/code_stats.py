import io, os, re, subprocess
ROOT = r"D:\XTS\code\SystemFeature"; GIT = r"D:\XTS"
PROJECTS = [(r"Media\Camera"),(r"Media\GamePuzzle"),(r"Media\MusicPlayer"),(r"Media\Recorder"),(r"Media\VoiceCallDemo"),(r"Notification\Publish"),(r"ResourceAllocation\ApplicationThemeSwitch"),(r"Security\CertificateFramework"),(r"WindowManagement\WindowManage")]
def git(*a):
    return subprocess.run(["git","-C",GIT]+list(a),capture_output=True,text=True,encoding="utf-8",errors="replace").stdout
for rel in PROJECTS:
    gp = "code/SystemFeature/" + rel.replace("\\","/")
    add=dele=files=0
    for line in git("diff","--numstat","--",gp).splitlines():
        p=line.split("\t")
        if len(p)>=3 and (p[2].endswith(".ets") or p[2].endswith(".ts")):
            try: add+=int(p[0]); dele+=int(p[1]); files+=1
            except: pass
    uf=ul=0
    for line in git("status","--porcelain","--",gp).splitlines():
        if not line.startswith("??"): continue
        path=line[3:].strip()
        if not (path.endswith(".ets") or path.endswith(".ts")): continue
        full=os.path.join(GIT,path)
        if os.path.isfile(full):
            uf+=1; ul+=io.open(full,encoding="utf-8",errors="replace").read().count("\n")+1
    print("{}\tcodeFiles={}\t+{}\t-{}\tnewFiles={}\tnewLines={}\ttotal={}".format(rel,files,add,dele,uf,ul,add+dele+ul))
