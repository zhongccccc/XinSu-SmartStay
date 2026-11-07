import io
p = r'D:\XTS\code\SystemFeature\Media\Recorder\entry\src\main\ets\pages\Play.ets'
t = io.open(p, encoding='utf-8').read()
t = t.replace("import { AudioModel } from '../model/AudioModel';",
              "import { AudioModel } from '../model/AudioModel';\nimport Logger from '../model/Logger';\n\nconst TAG: string = '[Recorder.Play]';")
t = t.replace("    this.title = name;\n    this.audioModel.initAudioPlayer(this.filePath, true);",
              "    this.title = name;\n    Logger.info(TAG, `PlayPage ready, title=${name}`);\n    this.audioModel.initAudioPlayer(this.filePath, true);")
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('play log added')
