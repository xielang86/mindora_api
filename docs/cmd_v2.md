| 用户意图 | action | action_params | 参数说明 | 对话框代答言 | 说明 |
|---------|--------|--------------|---------|------------|-----|
| 天气怎么样<br>天气预报<br>温度 | weather |  |  | 无 |  |
| 这是什么<br>我手里的是什么 | take_photo |  |  | 好的，我看一下 |  |
| 我有些困了<br>我想睡觉 | sleep_assistant |  |  | 好的，让我打一起轻松舒心，准备进入甜美的梦乡 |  |
| 调高音量，声音大点，音量大点，音量高一点，声音大一点<br>调低音量，声音小点，音量小点，音量低一点，声音小一点<br>静音，关闭声音，不要声音，声音静音<br>恢复音量音乐，恢复声音大点，恢复音乐大点<br>降低音量音乐，降低声音大点，降低音乐大点<br>前往音量音乐，前往声音大点，前往音乐大点 | cmd |   ```{   "device": "volume",    "operation": "mute\|voice\|background_sound\|music",    "value": "up\|down\|mute"  }``` | • main 音量<br>• voice 人声<br>• background_soun<br>d 背景音<br>• music 音乐 | 好的，(音量)(人声)(背景音)(音乐)已经(增大)(减小) |  |
| 调暗灯光，灯光暗一点，把灯调暗，灯光调暗<br>调亮灯光，灯光亮一点，把灯调亮，灯光调亮 | cmd |   ```{   "device": "light",    "operation": "brightness",    "value": "up\|down"  }``` |  | 好的，灯光已经(变亮\|变暗) |  |
| 打开变色灯光，把灯调成绿色，将色灯打开 | cmd |   ```{   "device": "light",    "operation": "color",    "value": "green\|blue\|red\|purple\|yellow\|white"  }``` |  | 好的，灯光已变为蓝色[COLOR_NAME] |  |
| 电灯变模式灯光，电灯变彩灯光<br>蓝色模式灯光，蓝色灯光<br>水母模式灯光，水母灯光<br>火焰模式灯光，火焰灯光<br>浪漫模式灯光，浪漫灯光<br>幻彩跑马模式,流彩模式灯光，跑彩灯光 | cmd |   ```{   "device": "light",    "operation": "mode",    "value": <br>      "flowing_color\|starry_sky\|jellyfish\|flame\|waves\|rainbow"  }``` |  | 好的，灯光已变为彩模式 | 模式：流光溢彩，星空，水母，火焰，浪漫，跑彩 |
| 开灯，打开灯，开启灯光 | cmd |   ```{   "device": "light",    "operation": "state",    "value": "on\|off"  }``` |  | 好的，灯光已开启 |  |
| 开音量，打开音量，开启音量<br>关音量，关闭音量，关掉音量 | cmd |   ```{   "device": "volume",    "value": "on\|off"  }``` |  | 好的，音量已经(开光\|关闭) |  |
| 进入睡眠，系统休眠，休眠 | cmd |   ```{   "device": "system",    "value": "sleep"  }``` |  | 好的，设备即将进入休眠模式 |  |
| 关机，关闭机器，关闭设备 | cmd |   ```json {   "device": "system",    "value": "shutdown"  }``` |  | 好的，设备即将关机 |  |
| 打开摄像头，打开摄像，打开监控，打开录像<br>关闭摄像头，关闭摄像，关闭监控，关闭录像 | cmd |   ```{   "device": "camera",    "value": "on\|off"  }``` |  | 好的，摄像头已(开启\|关闭) |  |
| 打开麦克风，打开话筒，开启麦克风<br>关闭麦克风，关闭话筒，关闭语音 | cmd |   ```{   "device": "microphone",    "value": "on\|off"  }``` |  | 好的，麦克风已(开启\|关闭) |  |
| 打开夜灯，开夜灯，夜灯，开启夜灯模式<br>关闭夜灯，关夜灯，停止夜灯 | cmd |   ```{   "device": "light",    "operation": "night_light",    "value": "on\|off"  }``` |  | 好的，夜灯已(开启\|关闭) |  |
| 切换灯光模式，下一个灯光模式，切换灯效 | cmd |   ```{   "device": "light",    "operation": "mode",    "value": "next"  }``` |  | 好的，已切换灯光模式 |  |
| 调亮屏幕，屏幕亮一点，屏幕太暗了<br>调暗屏幕，屏幕暗一点，屏幕太亮了 | cmd |   ```{   "device": "screen",    "operation": "brightness",    "value": "up\|down"  }``` |  | 好的，屏幕亮度已(增加\|降低) |  |
| 香味淡一点，香味调淡，香味太浓了<br>香味浓一点，香味调浓，香味太淡了 | cmd |   ```{   "device": "fragrance",    "operation": "intensity",    "value": "lower\|higher"  }``` |  | 好的，香薰强度已(降低\|增加) |  |
| 打开冥想，开始冥想，冥想，我要冥想<br>关闭冥想，停止冥想，退出冥想，结束冥想 | cmd |   ```{   "device": "meditation",    "value": "start\|stop"  }``` |  | 好的，冥想已(开始\|停止) |  |
| 打开助眠，开始助眠，助眠，开启助眠功能<br>关闭助眠，停止助眠，退出助眠，结束助眠 | cmd |   ```{   "device": "sleep_assistant",    "value": "start\|stop"  }``` |  | 好的，助眠功能已(开启\|关闭) |  |
| 打开音乐，播放音乐，来点音乐，开始播放<br>关闭音乐，停止播放，不要音乐了，停止音乐 | cmd |   ```{   "device": "music",    "value": "play\|stop"  }``` |  | 好的，音乐已(开始\|停止)播放 |  |
| 换一首，换个音乐，下一首，下一曲，切歌 | cmd |   ```{   "device": "music",    "value": "next"  }``` |  | 好的，已切换到下一首 |  |
| 循环播放，全部循环，列表循环<br>单曲循环，单曲重复，重复这首歌 | cmd |   ```{   "device": "music",    "operation": "mode",    "value": "repeat_all\|repeat_one"  }``` |  | 好的，已设置为(全部循环\|单曲循环)播放 |  |
| 打开闹钟，闹钟列表，查看闹钟，显示闹钟<br>关闭闹钟，停止闹钟，闹钟停止，取消闹铃<br>设置闹钟，定一个闹钟，设一个闹钟<br>取消闹钟，删除闹钟，取消明天的闹钟 | cmd |   ```{   "device": "alarm",    "value": "list\|stop\|set\|cancel"  }``` |  | 好的，闹钟(列表已显示\|已停止\|已设置\|已取消) |  |